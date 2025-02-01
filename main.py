# # docker pull ollama/ollama
# # docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
# # docker exec -it ollama ollama pull llama3.1:8b     
##python3 -m venv .venv
##source .venv/bin/activate

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
def iraS_iseB(a: int) -> str:
    """returns if the number is [iraS Sankya] or [iseB Sankya]"""
    if a % 2 == 0:
        return "iraS Sankya"
    else:
        return "iseB Sankya"

toolkit = [add, multiply, square, weather, iraS_iseB]

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
# tool_actions = tool_runnable.invoke({"input": "hi! what's 1+1 and  2 times 2", 'intermediate_steps': []})

# print(tool_actions)

def run_tool_agent(state):
    agent_outcome = tool_runnable.invoke(state)

    #this agent will overwrite the agent outcome state variable
    return {"agent_outcome": agent_outcome}

# tool executor invokes the tool action specified from the agent runnable
# they will become the nodes that will be called when the agent decides on a tool action.

tool_executor = ToolNode(toolkit)

# Define the function to execute tools
# This node will run a different tool as specified in the state variable agent_outcome
def execute_tools(state):
    # Get the most recent agent_outcome - this is the key added in the `agent` above
    agent_action = state['agent_outcome']
    if type(agent_action) is not list:
        agent_action = [agent_action]
    steps = []
    #sca only returns an action while tool calling returns a list
    # convert single actions to a list
    
    for action in agent_action:
    # Execute the tool
        output = tool_executor.invoke(action)
        print(f"The agent action is {action}")
        print(f"The tool result is: {output}")
        steps.append((action, str(output)))
    # Return the output
    return {"intermediate_steps": steps}

class AgentState(TypedDict):
   # The input string from human
   input: str
   # The list of previous messages in the conversation
   chat_history: list[BaseMessage]
   # The outcome of a given call to the agent
   # Needs 'list' as a valid type as the tool agent returns a list.
   # Needs `None` as a valid type, since this is what this will start as
   # this state will be overwritten with the latest everytime the agent is run
   agent_outcome: Union[AgentAction, list, ToolAgentAction, AgentFinish, None]

   # List of actions and corresponding observations
   # These actions should be added onto the existing so we use `operator.add` 
   # to append to the list of past intermediate steps
   intermediate_steps: Annotated[list[Union[tuple[AgentAction, str], tuple[ToolAgentAction, str]]], operator.add]

def should_continue(data):
    # If the agent outcome is an AgentFinish, then we return `exit` string
    # This will be used when setting up the graph to define the flow
    if isinstance(data['agent_outcome'], AgentFinish):
        return "END"
    # Otherwise, an AgentAction is returned
    # Here we return `continue` string
    # This will be used when setting up the graph to define the flow
    else:
        return "CONTINUE"


# Define a new graph
graph = StateGraph(AgentState)

# When nodes are called, the functions for to the tools will be called. 
graph.add_node("agent", run_tool_agent)


# Add tool invocation node to the graph
graph.add_node("action", execute_tools)

# Define which node the graph will invoke at start.
graph.set_entry_point("agent")

# Add flow logic with static edge.
# Each time a tool is invoked and completed we want to 
# return the result to the agent to assess if task is complete or to take further actions 

#each action invocation has an edge leading to the agent node.
graph.add_edge('action', 'agent')

# Add flow logic with conditional edge.
graph.add_conditional_edges(
    # first parameter is the starting node for the edge
    "agent",
    # the second parameter specifies the logic function to be run
    # to determine which node the edge will point to given the state.
    should_continue,

    #third parameter defines the mapping between the logic function 
    #output and the nodes on the graph
    # For each possible output of the logic function there must be a valid node.
    {
        # If 'continue' we proceed to the action node.
        "CONTINUE": "action",
        # Otherwise we end invocations with the END node.
        "END": END
    }
)

memory = MemorySaver()

# Finally, compile the graph! 
# This compiles it into a LangChain Runnable,
app = graph.compile(checkpointer = memory)

input1 = {"input": "Add 1 and 1 and tell me if that is iraS or iseB", "chat_history": []} 
# input2 = {"input": "Multiply 13 times 23 and tell me if that is iraS or iseB", "chat_history": []} 
# input3 = {"input": "How is the weather in San Ramon?", "chat_history": []} 

config = {"configurable": {"thread_id": "1"}}

for s in app.stream(input1, config = config):
    print(list(s.values())[0])
    print("----")

# for s in app.stream(input2, config = config):
#     print(list(s.values())[0])
#     print("----")

# for s in app.stream(input3, config = config):
#     print(list(s.values())[0])
#     print("----")
