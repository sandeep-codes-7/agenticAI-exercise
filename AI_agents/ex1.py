from langgraph.graph import START, StateGraph, END
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from typing import List, TypedDict

class AgentState(TypedDict):
    messages:List[HumanMessage]

llm = ChatOllama(
    model="llama3.2:3b",
    
)

def process(state:AgentState):
    response = llm.invoke(state["messages"])
    print(f"AI: {response.content}")
    return state

graph = StateGraph(AgentState)

graph.add_node("process",process)
graph.add_edge(START,"process")
graph.add_edge("process", END)


app = graph.compile()


user_input = input("enter: ")
res = app.invoke({"messages":[HumanMessage(content=user_input)]})
