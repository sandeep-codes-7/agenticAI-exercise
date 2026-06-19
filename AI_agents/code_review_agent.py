from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode 

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

code_content = ""


@tool
def update(content: str)-> str:
    """Update the code file with the provided content"""
    global code_content
    code_content = content
    return f"Code has been modified and new code is:\n{content}"
    

# @tool
# def save(filename: str) -> str:
#     """Save the current code file in the specified code file format [example: .py, .java, .c, .dart, etc..] and finish the process.

#     Args:
#         filename: Name for the code file.
#     """
#     global code_content

#     try:
#         with open(filename, 'w') as f:
#             f.write(code_content)
#         print(f"file {filename} saved successfully!")
#         return f"file {filename} has been saved successfully!"

#     except Exception as e:
#         return f"error saving the file: {filename} -> {str(e)}"

@tool
def save(filename: str) -> str:
    """Save the current code file..."""
    global code_content

    if not code_content.strip():
        return "Error: no code to save. Use the 'update' tool first to set the code content."

    try:
        with open(filename, 'w') as f:
            f.write(code_content)
        return f"file {filename} has been saved successfully!"
    except Exception as e:
        return f"error saving the file: {filename} -> {str(e)}"
    
tools = [update, save]

model = ChatOllama(model="qwen3:8b").bind_tools(tools)

def agent(state: AgentState)-> AgentState:
    system_prompt = SystemMessage(
        content=f"""
            You are a software professional, you need to review the code base and find bugs in the provided code. And helps the user to write the code file, modify the code file and save the code file.

            - if the user want's to update the code, use need to use 'update' tool with the complete updated code.
            - if the user want's to save the code and finish the process, you need to use 'save' tool to save the code file and finish the process.
            - make sure to show the user the current code file state after modifications and do not save it without consent of the user.

            The current code file content is: {code_content}
        """
    )

    if not state["messages"]:
        user_input = "I am ready to help you with writing and modifying a code file"
        user_message = HumanMessage(content=user_input)
    
    else:
        user_input = input("\nwhat would you like to do with the code?\n")
        print(f"\n USER: {user_input}")
        user_message = HumanMessage(content=user_input)

    all_messages = [system_prompt] + list(state["messages"]) + [user_message]

    response = model.invoke(all_messages)

    print(f"\nAI: {response.content}")

    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"using tools: {[tc['name'] for tc in response.tool_calls]}")

    return {"messages" : list(state["messages"]) + [user_message, response]}

def should_continue(state: AgentState) -> str:
    """Determine if we should continue the conversation or end the conversation."""

    messages = state["messages"]

    for message in reversed(messages):
        if(isinstance(message, ToolMessage) and 'saved' in message.content.lower() and 'file' in message.content.lower()):
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



def run_code_reviewer(file_path=None):
    print("\n===== Welcome to code_reviewer =====")

    global code_content

    if file_path:
        try:
            with open(file_path,'r') as f:
                code_content = f.read()
            print(f"file {file_path} loaded successfully...")
        except Exception as e:
            print(f"error occured!")
            return
    
    state = {"messages":[]}

    for step in app.stream(state, stream_mode="values"):
        if "messages" in step:
            print_messages(step["messages"])

    print(f"\n===== Finished =====")


if __name__ == "__main__":
    user = input("Do you have a code file(y/n): ")
    flag = False
    if user not in ['y', 'Y', 'yes', 'YES']:
        run_code_reviewer()
    else:
        path = input("enter file path: ")
        run_code_reviewer(path)
    