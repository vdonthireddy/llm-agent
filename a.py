#region imports
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
#endregion

llm = ChatOllama(model="llama3.1:8b")

#region tools
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
def iraS_iseB(a: str) -> str:
    """returns if the number is [iraS Sankya] or [iseB Sankya]"""
    if int(a) % 2 == 0:
        return "iraS Sankya"
    else:
        return "iseB Sankya"
#endregion

toolkit = [add, multiply, square, weather, iraS_iseB]

system_prompt = """ You are a mathematician.
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

tool_runnable = create_tool_calling_agent(llm, toolkit, prompt = tool_calling_prompt)

def run_tool_agent(state):
    agent_outcome = tool_runnable.invoke(state)
    return {"agent_outcome": agent_outcome}

tool_executor = ToolNode(toolkit)

def execute_tools(state):
    agent_action = state['agent_outcome']
    if type(agent_action) is not list:
        agent_action = [agent_action]
    steps = []
    for action in agent_action:
        output = tool_executor.invoke(action)
        print(f"The agent action is {action}")
        print(f"The tool result is: {output}")
        steps.append((action, str(output)))
    return {"intermediate_steps": steps}

class AgentState(TypedDict):
   input: str
   chat_history: list[BaseMessage]
   agent_outcome: Union[AgentAction, list, ToolAgentAction, AgentFinish, None]
   intermediate_steps: Annotated[list[Union[tuple[AgentAction, str], tuple[ToolAgentAction, str]]], operator.add]

def should_continue(data):
    if isinstance(data['agent_outcome'], AgentFinish):
        return "END"
    else:
        return "CONTINUE"

graph = StateGraph(AgentState)
graph.add_node("agent", run_tool_agent)
graph.add_node("action", execute_tools)
graph.set_entry_point("agent")
graph.add_edge('action', 'agent')
graph.add_conditional_edges(
    "agent",
    should_continue,
    {
        "CONTINUE": "action",
        "END": END
    }
)

memory = MemorySaver()
app = graph.compile(checkpointer = memory)
input1 = {"input": "Add 1 and 1 and tell me if the result is iraS or iseB", "chat_history": []} 
config = {"configurable": {"thread_id": "1"}}

for s in app.stream(input1, config = config):
    print(list(s.values())[0])
    print("----")
