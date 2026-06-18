from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, Sequence, Annotated, List
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
# from groq import Groq
# from dotenv import load_dotenv
# import os

# load_dotenv()


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


document_content = ""

@tool
def update(content: str) -> str:
    """updates the document with the provided content"""
    global document_content
    document_content = content
    return f"Document has been updated successfully!, the current document is: \n{document_content}"

@tool
def save(filename: str) -> str:
    """Save the current document in a text file and finish the process.

    Args:
        filename: Name for the text file.
    """

    global document_content
    
    if not filename.endswith(".txt"):
        filename = f"{filename}.txt"
    
    try:
        with open(filename,"w") as f:
            f.write(document_content)
        print(f"document {filename} is saved successfully!")
        return f"document {filename} has been saved successfully!"
    except Exception as e:
        return f"error saving the document {filename}: {str(e)}"
    

tools = [update, save]

model = ChatOllama(model="qwen3:8b").bind_tools(tools)
# llm = Groq(model="llama-3.3-70b-versatile", groq_api_key=os.getenv("GROQ_API_KEY"))


def agent(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(
        content=f"""
            You are Drafter, A helpful writing assistant, help the user to update and modify documents.

            - if the user want to update the document, you need to use the 'update' tool with the complete updated document content.
            - if the user want to save and finish, you need to use the 'save' tool and finish the process.
            - make sure to show the user the current document state after modifications.

            the current document content is: {document_content}
        """
    )

    if not state["messages"]:
        user_input = "I'm ready to help you update a document, what would you like to create?"
        user_message = HumanMessage(content=user_input)
    
    else:
        user_input = input("\nwhat would you like to do with the document?\n>>> ")
        print(f"USER: {user_input}")
        user_message = HumanMessage(content=user_input)

    all_messages = [system_prompt] + list(state["messages"]) + [user_message]

    response = model.invoke(all_messages)

    print(f"\nAI: {response.content}")
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"using tools: {[tc["name"] for tc in response.tool_calls]}")

    return {"messages": list(state["messages"]) + [user_message, response]}

def should_continue(state: AgentState) -> str:
    """Determine if we should continue or end the conversation"""

    messages = state["messages"]

    if not messages:
        return "continue"
    
    for message in reversed(messages):
        if (isinstance(message, ToolMessage) and 
            'saved' in message.content.lower() and 
            'document' in message.content.lower()):
            return 'end'
        
    return 'continue'

def print_messages(messages):
    """Function I made to print the message in a more readable format"""
    if not messages:
        return
    
    for message in messages[-3:]:
        if isinstance(message, ToolMessage):
            print(f"\nTool Message: \n{message.content}")

graph = StateGraph(AgentState)

graph.add_node("agent", agent)
tool_node = ToolNode(tools)
graph.add_node("tools", tool_node)

graph.set_entry_point("agent")

graph.add_edge("agent", "tools")

graph.add_conditional_edges(
    "tools",
    should_continue,
    {
        "continue":"agent",
        "end":END
    }
)


app = graph.compile()

def run_drafter():
    print("\n =====Welcome to Drafter=====")
    
    state = {"messages":[]}

    for step in app.stream(state, stream_mode="values"):
        if "messages" in step:
            print_messages(step["messages"])

    print(f"\n ===== Drafter Finished =====")


if __name__ == "__main__":
    run_drafter()