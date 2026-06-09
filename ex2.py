from langgraph.graph import StateGraph
from typing import List, TypedDict


class AgentState(TypedDict):
    values: List[int]
    operation: str
    name: str
    result: int
    message: str


def math_node(state: AgentState) -> AgentState:
    """performing math operations"""

    if state["operation"] == "+":
        state["result"] = sum(state["values"])
    elif state["operation"] == "*":
        state["result"] = 1
        for value in state["values"]:
            state["result"] *= value

    state["message"] = f"hey {state['name']}, your answer is {state['result']}"

    return state


graph = StateGraph(AgentState)

graph.add_node("math", math_node)

graph.set_entry_point("math")

graph.set_finish_point("math")

app = graph.compile()

result = app.invoke({"name": "sandeep", "values": [1, 2, 3, 4], "operation": "*"})

print(result["message"])
