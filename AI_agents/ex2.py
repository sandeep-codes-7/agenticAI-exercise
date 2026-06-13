from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
from typing import TypedDict, List, Union
from langchain_ollama import ChatOllama

class AgentState(TypedDict):
    messages:List[Union[AIMessage, HumanMessage]]

llm = ChatOllama(model="llama3.2:3b")

graph = StateGraph(AgentState)


def process(state: AgentState)-> AgentState:
    response = llm.invoke(state["messages"])
    state["messages"].append(AIMessage(content=response.content))
    print(f"\nAI: {response.content}\n")
    return state

graph.add_node("process",process)
graph.add_edge(START,"process")
graph.add_edge("process",END)

agent = graph.compile()

conv_hist = []
user = input("enter: ")
while user not in ["/exit","/bye"]:
    conv_hist.append(HumanMessage(content=user))
    result = agent.invoke({"messages":conv_hist})
    conv_hist = result["messages"]

    user = input("enter: ")