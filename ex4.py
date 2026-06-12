from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class AgentState(TypedDict):
    n1: int
    n2: int
    op: str
    message: str
    final: int

def addition_node(state: AgentState) -> AgentState:
    state['final'] = state['n1'] + state['n2']
    return state

def subtraction_node(state: AgentState) -> AgentState:
    state['final'] = state['n1'] - state['n2']
    return state

def multiplication_node(state: AgentState) -> AgentState:
    state['final'] = state['n1'] * state['n2']
    return state

def error_node(state: AgentState) -> AgentState:
    state['message'] = "not available!"
    return state

def decision_node(state: AgentState) -> AgentState:
    if state['op'] == "+":
        return "add_node"
    elif state['op'] == "-":
        return "sub_node"
    elif state['op'] == "*":
        return "mul_node"
    else:
        return "error_node"

graph = StateGraph(AgentState)

graph.add_node("addition_node", addition_node)
graph.add_node("sub_node", subtraction_node)
graph.add_node("mul_node", multiplication_node)
graph.add_node("error_node", error_node)
graph.add_node("router", lambda state:state)

graph.add_edge(START,"router")
graph.add_conditional_edges(
    "router",
    decision_node,
    {
        "add_node":"addition_node",
        "sub_node":"sub_node",
        "mul_node":"mul_node",
        "error_node":"error_node"
    }
)

graph.add_edge("addition_node", END)
graph.add_edge("sub_node", END)
graph.add_edge("mul_node", END)
graph.add_edge("error_node", END)

app = graph.compile()

result = app.invoke({"n1":20, "n2":40, "op":"-"})

print(result)