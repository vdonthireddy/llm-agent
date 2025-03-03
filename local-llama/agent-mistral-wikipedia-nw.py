import requests

from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferWindowMemory
from pydantic import BaseModel, Field
from langchain.tools import tool
from langchain_ollama import OllamaLLM

class WikipediaArticleExporter(BaseModel):
    article: str = Field(description="The canonical name of the Wikipedia article")

@tool("wikipedia_text_exporter", args_schema=WikipediaArticleExporter, return_direct=False)
def wikipedia_text_exporter(article: str) -> str:
  '''Fetches the most recent revision for a Wikipedia article in WikiText format.'''
  url = f"https://en.wikipedia.org/w/api.php?action=parse&page={article}&prop=wikitext&formatversion=2"

  result = requests.get(url).text
  start = result.find('"wikitext": "\{\{')
  end = result.find('\}</pre></div></div><!--esi')

  result = result[start+12:end-30]

  return ({"text": result})

@tool("wikipedia_largest_cities", args_schema=WikipediaArticleExporter, return_direct=False)
def wikipedia_largest_cities(article: str) -> str:
  '''Fetches the data of highly populated cities in the world in WikiText format.'''
  url = f"https://en.wikipedia.org/wiki/List_of_largest_cities"

  result = requests.get(url).text
  start = result.find('"wikitext": "\{\{')
  end = result.find('\}</pre></div></div><!--esi')

  result = result[start+12:end-30]

  return ({"text": result})

def append_chat_history(input, response):
    chat_history.save_context({"input": input}, {"output": response})

def invoke(input):
    msg = {
        "input": input,
        "chat_history": chat_history.load_memory_variables({}),
    }
    print(f"Input: {msg}")

    response = agent_executor.invoke(msg)
    print(f"Response: {response}")

    append_chat_history(response["input"], response["output"])
    print(f"History: {chat_history.load_memory_variables({})}")


tools = [wikipedia_text_exporter, wikipedia_largest_cities]
prompt = hub.pull("hwchase17/react-chat")
chat_history = ConversationBufferWindowMemory(k=10)
# llm = OllamaLLM(model="llama3")
llm = OllamaLLM(model="mistral")

agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# invoke("What is the capital of India? Do not use a tool.")
# invoke("What is the next biggest city after the city you just mentioned in that country? Do not use a tool.")
# invoke("What is the country name again? sorry, I forgot? Do not use a tool.")
# invoke("Does this country has any other names? Do not use a tool.")

# invoke("What is the capital of USA? Do not use a tool.")
# invoke("What is the capital of Nepal? Do not use a tool.")
# invoke("What is the capital of India? Do not use a tool.")
# invoke("About which capital cities did I ask? Do not use a tool.")
# # invoke("What are the GDPs of these countries? Do not use a tool.")
# invoke("what city in the world has highest population? Do not use a tool.")

invoke("What is the most populus city in USA? Strictly get data from the tool only")
