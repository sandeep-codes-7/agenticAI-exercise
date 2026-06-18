"""
ReAct Agent
"""

from typing import Annotated, Sequence, TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
from langchain_core.messages import SystemMessage
from langchain_core.messages import ToolMessage
from langgraph.graph.message import add_messages # preserves state with out changing the entire data and maintains the consistency
from langgraph.prebuilt import ToolNode
from langchain_ollama import ChatOllama
from langchain_core.tools import tool #decorator to identify a function/method as a tool

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

@tool
def add(a: int, b:int)->int:
    """performs addition operation upon two integer values"""
    return a+b

@tool
def multi(a: int, b: int):
    """multiplication"""
    return a*b

tools = [add, multi]

model = ChatOllama(model="qwen3:8b").bind_tools(tools)


def model_call(state: AgentState)-> AgentState:

    system_prompt = SystemMessage(content="you are my AI assistant and answers my queries to the best of your ability.")

    response = model.invoke([system_prompt] + state["messages"])

    return {"messages":[response]}

def should_continue(state: AgentState):
    message = state["messages"]
    last_message = message[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"
    

graph = StateGraph(AgentState)
graph.add_node("agent",model_call)
tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)

graph.set_entry_point("agent")

graph.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue":"tools",
        "end":END
    }
)

graph.add_edge("tools","agent")

app = graph.compile()

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message,tuple):
            print(message)
        else:
            message.pretty_print()

user = input("\nenter: ")

# inputs = {"messages":[("user","divide 4/2")]}

# print_stream(app.stream(inputs, stream_mode="values"))

while user != "bye":
    inputs = {"messages":[("user",user)]}
    print_stream(app.stream(inputs,stream_mode="values"))

    user = input("\nenter: ")