"""
LangGraph Agent Implementation
============================

This module contains the LangGraph agent with custom tools.
It's a simplified version of our previous examples.
"""

import os
from typing import Annotated, TypedDict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from tools.database_tool import (
    query_database, get_top_customers, get_customer_purchases,
    get_products_by_category_tool, get_database_stats, generate_and_execute_sql
)

# Extended state to include user information
class AgentState(TypedDict):
    messages: Annotated[list, "List of messages"]
    user_role: Optional[str]
    permission_checked: bool

# Custom tools
@tool
def get_system_info() -> str:
    """Get information about the system and current status."""
    import platform
    import datetime
    
    return f"""
    System Information:
    - Platform: {platform.system()} {platform.release()}
    - Python: {platform.python_version()}
    - Current time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    - Service: LangGraph Agent API
    """

@tool
def calculate(expression: str) -> str:
    """Safely evaluate a mathematical expression."""
    try:
        # Only allow safe mathematical operations
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            return "Error: Only basic mathematical operations are allowed"
        
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"

def setup_models():
    """Initialize the OpenAI LLM."""
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        openai_api_key=os.environ.get("OPENAI_API_KEY")
    )

def create_wikipedia_tool():
    """Create Wikipedia search tool."""
    api_wrapper = WikipediaAPIWrapper(top_k_results=2)
    return WikipediaQueryRun(api_wrapper=api_wrapper)

def check_permissions(state: AgentState):
    """Check if the user has permission to access database tools."""
    user_role = state.get("user_role", "employee")
    last_message = state["messages"][-1]
    message_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
    
    # Define sensitive keywords that require higher permissions
    sensitive_keywords = [
        "revenue", "profit", "financial", "salary", "compensation", "budget",
        "customer data", "personal information", "confidential", "sensitive",
        "delete", "update", "modify", "change", "alter"
    ]
    
    # Check if the message contains sensitive information
    message_lower = message_content.lower()
    is_sensitive = any(keyword in message_lower for keyword in sensitive_keywords)
    
    # Permission logic
    if user_role == "admin":
        return {"permission_checked": True, "access_granted": True}
    elif user_role == "manager":
        if is_sensitive:
            return {
                "permission_checked": True, 
                "access_granted": False,
                "messages": [AIMessage(content="I'm sorry, but this query contains sensitive information that requires admin-level access. Please contact an administrator or rephrase your question to focus on general business metrics.")]
            }
        return {"permission_checked": True, "access_granted": True}
    else:  # employee
        if is_sensitive:
            return {
                "permission_checked": True, 
                "access_granted": False,
                "messages": [AIMessage(content="I'm sorry, but this query contains sensitive information that requires manager or admin access. Please contact your manager or rephrase your question to focus on general company information.")]
            }
        return {"permission_checked": True, "access_granted": True}

def should_continue(state: AgentState):
    """Determine if we should continue to tools or end."""
    last_message = state["messages"][-1]
    
    # If the last message has tool calls, continue to tools
    if isinstance(last_message, AIMessage) and hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    
    # End the conversation if no tool calls are present
    return END

def should_check_permissions(state: AgentState):
    """Determine if we need to check permissions first."""
    if not state.get("permission_checked", False):
        return "check_permissions"
    elif state.get("access_granted", True):
        return "chatbot"
    else:
        return END

def create_graph_workflow():
    """Create the complete graph workflow with all tools and nodes."""
    # Setup models and tools
    llm = setup_models()
    wikipedia_tool = create_wikipedia_tool()
    
    # List of all tools
    tools = [
        wikipedia_tool, 
        get_system_info, 
        calculate,
        query_database,
        get_top_customers,
        get_customer_purchases,
        get_products_by_category_tool,
        get_database_stats,
        generate_and_execute_sql
    ]
    
    # Create tool node
    tool_node = ToolNode(tools)
    
    # Bind tools to the LLM
    model_with_tools = llm.bind_tools(tools)
    
    # Define call_model function inline
    def call_model(state: MessagesState):
        """Extract the last message and handle tool calls or regular LLM responses."""
        last_message = state["messages"][-1]

        # If the last message has tool calls, return the tool's response
        if isinstance(last_message, AIMessage) and hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            # Don't return anything here - let the tool node handle it
            return {"messages": []}
        
        # Otherwise, proceed with a regular LLM response
        return {"messages": [model_with_tools.invoke(state["messages"])]}
    
    # Create workflow with original state
    workflow = StateGraph(MessagesState)
    
    # Add nodes for chatbot and tools (permission checking temporarily disabled)
    workflow.add_node("chatbot", call_model)
    workflow.add_node("tools", tool_node)
    
    # Define an edge connecting START to chatbot
    workflow.add_edge(START, "chatbot")
    
    # Define conditional edges and route "tools" back to "chatbot"
    workflow.add_conditional_edges("chatbot", should_continue, ["tools", END])
    workflow.add_edge("tools", "chatbot")
    
    # Set up memory and compile the workflow
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app
