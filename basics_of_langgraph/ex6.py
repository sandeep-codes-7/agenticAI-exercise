from langgraph.graph import StateGraph, END
from typing import TypedDict, List
import random


class AgentState(TypedDict):
    name:str
    numbers: List[int]
    counter:int

def greet(state:AgentState)->AgentState:
    state['name'] = f"hey there, {state["name"]}!"
    state['counter'] = 0
    return state

def random_node(state: AgentState)-> AgentState:
    state['numbers'].append(random.randint(0,10))
    state['counter'] += 1
    return state

def decision(state:AgentState):
    if state['counter'] < 5:
        print(f"hey i'm in loop: {state["counter"]}")
        return "loop"
    else:
        return "exit"
    
graph = StateGraph(AgentState)

graph.add_node("greet", greet)
graph.add_node("random",random_node)

graph.add_edge("greet","random")

graph.set_entry_point("greet")

graph.add_conditional_edges(
    "random",
    decision,
    {
        "loop":"random",
        "exit":END
    }
)

app = graph.compile()

res = app.invoke({"name":"sandeep","numbers":[],"counter":0})

print(res)