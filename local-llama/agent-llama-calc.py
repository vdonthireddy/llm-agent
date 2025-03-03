# docker pull ollama/ollama
# docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
# docker exec -it ollama ollama pull llama3.1:8b     
from langchain_ollama import ChatOllama
from langchain.agents import Tool
from langgraph.prebuilt import create_react_agent

model = ChatOllama(model="llama3.1:8b")
tools = [
    Tool(
        name="Calculator",
        func=lambda x: eval(x),
        description="A calculator for basic arithmetic operations.",
    ),
    # Add more tools as needed
]
agent_executor = create_react_agent(model, tools)
response= agent_executor.invoke({"messages": [("user", "What is 3 plus 4 multiplied by 5 plus 6 times 0?")]})
for message in response['messages']:
    print(message.content)