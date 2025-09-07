"""
LangGraph Agent Implementation
============================

This module contains the LangGraph agent with custom tools.
It's a simplified version of our previous examples.
"""

import os
from typing import Annotated, TypedDict
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

def should_continue(state: MessagesState):
    """Determine if we should continue to tools or end."""
    last_message = state["messages"][-1]
    
    # If the last message has tool calls, continue to tools
    if isinstance(last_message, AIMessage) and hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    
    # End the conversation if no tool calls are present
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
    
    # Create workflow
    workflow = StateGraph(MessagesState)
    
    # Add nodes for chatbot and tools
    workflow.add_node("chatbot", call_model)
    workflow.add_node("tools", tool_node)
    
    # Define an edge connecting START to the chatbot
    workflow.add_edge(START, "chatbot")
    
    # Define conditional edges and route "tools" back to "chatbot"
    workflow.add_conditional_edges("chatbot", should_continue, ["tools", END])
    workflow.add_edge("tools", "chatbot")
    
    # Set up memory and compile the workflow
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app
