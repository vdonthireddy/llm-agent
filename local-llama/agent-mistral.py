import requests

from math import pi
from typing import Union
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent, initialize_agent
from langchain.memory import ConversationBufferWindowMemory
from pydantic import BaseModel, Field
from langchain.tools import tool, BaseTool
from langchain_ollama import OllamaLLM
from langchain_experimental.chat_models import Llama2Chat
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from typing import Optional, Type

from langchain_core.prompts import PromptTemplate


# class SquareAreaInput(BaseModel):
#     side: Union[int, float] = Field(description="side of the square")

class SquareAreaTool(BaseTool):
    name: str = "Square Area calculator"
    description: str = "use this tool when you need to calculate area using the sides of a square"
    # args_schema: Type[BaseModel] = SquareAreaInput
    # return_direct: bool = True

    def _run(self, side: Union[int, float]):
        return float(side)*float(side)

    def _arun(self, side: Union[int, float]):
        raise NotImplementedError("This tool does not support async")
    
class CircleAreaTool(BaseTool):
    name: str = "Circle Area calculator"
    description: str = "use this tool when you need to calculate a area using the radius of a circle"

    def _run(self, radius: Union[int, float]):
        return float(radius)*float(radius)*pi

    def _arun(self, radius: int):
        raise NotImplementedError("This tool does not support async")
    
class CircleCircumferenceTool(BaseTool):
    name: str = "Circle Circumference calculator"
    description: str = "use this tool when you need to calculate a circumference using the radius of a circle"

    def _run(self, radius: Union[int, float]):
        return float(radius)*2.0*pi

    def _arun(self, radius: int):
        raise NotImplementedError("This tool does not support async")

conversational_memory = ConversationBufferWindowMemory(
        memory_key='chat_history',
        k=5,
        return_messages=True
)

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

llm = OllamaLLM(model="mistral")
tools = [CircleCircumferenceTool(), CircleAreaTool(), SquareAreaTool()]

##the following prompt is copied from the hwchase17/react-chat
# prompt = hub.pull("hwchase17/react-chat")
template = '''Assistant is a large language model trained by OpenAI.

Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.

TOOLS:
------

Assistant has access to the following tools:

{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Begin!

Previous conversation history:
{chat_history}

New input: {input}
{agent_scratchpad}'''

prompt = PromptTemplate.from_template(template)

chat_history = ConversationBufferWindowMemory(k=10)
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

invoke("can you calculate the circumference of a circle that has a radius of 100cm?")
invoke("can you calculate the area of a square with side 2cm?")
invoke("can you calculate the area of that circle?")
