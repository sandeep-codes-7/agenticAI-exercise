from langgraph.graph import StateGraph
from typing import TypedDict


class AgentState(TypedDict):
    name: str
    age: str
    final: str


def first_node(state: AgentState) -> AgentState:
    state["final"] = f"Hi {state["name"]}! "

    return state

def second_node(state: AgentState) -> AgentState:
    state["final"] = state['final'] + f"your age is {state["age"]}"

    return state

graph = StateGraph(AgentState)

graph.add_node("first_node", first_node)
graph.add_node("second_node", second_node)

graph.add_edge("first_node","second_node")


graph.set_entry_point("first_node")

graph.set_finish_point("second_node")

app = graph.compile()

res = app.invoke({"name":"sandeep", "age":"21"})

print(res['final'])

