from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class AgentState(TypedDict):
    n1:int
    n2:int
    n3:int
    n4:int
    op1:str
    op2:str
    final1:int
    final2:int

def add_node(state: AgentState) -> AgentState:
    state['final1'] = state['n1'] + state['n2']
    return state

def sub_node(state: AgentState) -> AgentState:
    state['final1'] = state['n1'] - state['n2']
    return state

def add_node2(state: AgentState) -> AgentState:
    state['final2'] = state['n3'] + state['n4']
    return state

def sub_node2(state: AgentState) -> AgentState:
    state['final2'] = state['n3'] - state['n4']
    return state

def decision_node1(state: AgentState):
    if state['op1'] == "+":
        return "add_node1"
    elif state['op1'] == "-":
        return "sub_node1"
    
def decision_node2(state:AgentState):
    if state['op2'] == "+":
        return "add_node2"
    elif state['op2'] == "-":
        return "sub_node2"

graph = StateGraph(AgentState)

graph.add_node("add_node1", add_node)
graph.add_node("sub_node1", sub_node)
graph.add_node("add_node2", add_node2)
graph.add_node("sub_node2", sub_node2)

graph.add_node("router1", lambda state:state)
graph.add_node("router2", lambda state:state)

graph.add_edge(START, "router1")
graph.add_conditional_edges(
    "router1",
    decision_node1,
    {
        "add_node1":"add_node1",
        "sub_node1":"sub_node1"
    }
)

graph.add_edge("add_node1","router2")
graph.add_edge("sub_node1","router2")

graph.add_conditional_edges(
    "router2",
    decision_node2,
    {
        "add_node2":"add_node2",
        "sub_node2":"sub_node2"
    }
)

graph.add_edge("add_node2", END)
graph.add_edge("sub_node2", END)

app = graph.compile()

res = app.invoke({"n1":1,"n2":1,"n3":1,"n4":1,"op1":"+","op2":"-"})

print(res)