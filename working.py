from langchain_ollama import ChatOllama
from typing import TypedDict, Annotated, Sequence
from langchain.tools import tool
from langchain.agents import create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt.tool_node import ToolNode
from typing import TypedDict, Annotated,Union
from langchain_core.agents import AgentAction, AgentFinish
from langchain.agents.output_parsers.tools import ToolAgentAction
from langchain_core.messages import BaseMessage
import operator
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

llm = ChatOllama(model="llama3.1:8b")

# setup the simple tools using LangChain tool decorator
@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

@tool
def square(a: int) -> int:
    """Calculates the square of a number."""
    a = int(a)
    return a * a

@tool
def weather(a: str) -> str:
    """Gets the weather details."""
    return "98 degrees Fahrenheit"

@tool
def iras_iseb(a: int) -> str:
    """find out if a given number is iraS sankya or iseB sankya"""
    if a % 2 == 0:
        return "iraS Sankya"
    else:
        return "iseB Sankya"

toolkit = [add, multiply, square, weather, iras_iseb]

system_prompt = """ You are a mathematical assistant.
        You are also a weather reporter and use the tool to answer any weathe related questions.
        Use your tools to answer questions. If you do not have a tool to
        answer the question, say so. """

tool_calling_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)

tool_runnable = create_tool_calling_agent(llm, toolkit, prompt  = tool_calling_prompt)
tool_actions = tool_runnable.invoke({"input": "hi! what's 1+1 and tell me if the result is a ariS or esiB, what is 13 times 5 and tell me if the result is a ariS or esiB", 'intermediate_steps': []})
print(tool_actions)