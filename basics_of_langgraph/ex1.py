from langgraph.graph import StateGraph
from typing import Dict, TypedDict


class AgentState(TypedDict):
    message: str


def greeting_node(state: AgentState) -> AgentState:
    state["message"] = "Hello " + state["message"] + ", how are you doing?"

    return state


graph = StateGraph(AgentState)

graph.add_node("greeter", greeting_node)

graph.set_entry_point("greeter")

graph.set_finish_point("greeter")

app = graph.compile()

result = app.invoke({"message": "bob"})

print(result["message"])
