"""
Database Tool for LangGraph Agent
=================================

This tool allows the agent to query the mock e-commerce database.
It uses the DatabaseService for clean separation of concerns.
"""

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from services.database_service import database_service
import os

def generate_sql_from_question(question: str) -> str:
    """
    Generate a SQL query from a natural language question using LLM.
    
    Args:
        question: Natural language question about the database
        
    Returns:
        SQL query string or None if generation fails
    """
    try:
        # Initialize LLM for SQL generation
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Create prompt for SQL generation
        prompt = f"""
You are a SQL expert. Generate a SQL query to answer the following question about an e-commerce database.

Database Schema:
- users: id, name, email, total_spent, created_at
- products: id, name, price, category, stock, created_at  
- orders: id, user_id, product_id, quantity, total_price, order_date

Relationships:
- orders.user_id -> users.id
- orders.product_id -> products.id

Question: {question}

Rules:
1. Only generate SELECT queries (no INSERT, UPDATE, DELETE)
2. Use proper JOINs when needed
3. Be specific with column names
4. Use LIMIT when appropriate
5. Return ONLY the SQL query, no explanations

SQL Query:
"""
        
        # Generate SQL query
        response = llm.invoke(prompt)
        sql_query = response.content.strip()
        
        # Basic validation - ensure it's a SELECT query
        if sql_query.upper().startswith('SELECT'):
            return sql_query
        else:
            return None
            
    except Exception as e:
        print(f"Error generating SQL: {e}")
        return None

@tool
def query_database(query: str) -> str:
    """
    Execute a SQL query on the mock e-commerce database.
    
    Available tables:
    - users: id, name, email, total_spent, created_at
    - products: id, name, price, category, stock, created_at  
    - orders: id, user_id, product_id, quantity, total_price, order_date
    
    Examples of useful queries:
    - "SELECT * FROM users ORDER BY total_spent DESC LIMIT 5" (top spenders)
    - "SELECT * FROM products WHERE category = 'Electronics'" (products by category)
    - "SELECT * FROM orders ORDER BY order_date DESC LIMIT 10" (recent orders)
    
    Args:
        query: The SQL SELECT query to execute
        
    Returns:
        The query results as a formatted string
    """
    result = database_service.execute_query(query)
    
    if not result["success"]:
        return f"Database error: {result['error']}"
    
    if result["count"] == 0:
        return f"SQL: {query}\nNo results found for the query."
    
    return f"SQL: {query}\nQuery results ({result['count']} rows):\n{result['data']}"

@tool
def generate_and_execute_sql(question: str) -> str:
    """
    Generate and execute a SQL query based on a natural language question.
    
    This tool allows the LLM to create custom SQL queries to answer complex questions
    about the e-commerce database.
    
    Available tables and their columns:
    - users: id, name, email, total_spent, created_at
    - products: id, name, price, category, stock, created_at  
    - orders: id, user_id, product_id, quantity, total_price, order_date
    
    Relationships:
    - orders.user_id -> users.id
    - orders.product_id -> products.id
    
    Args:
        question: Natural language question about the database
        
    Returns:
        The SQL query generated and its results
    """
    # Generate SQL query based on the question
    sql_query = generate_sql_from_question(question)
    
    if not sql_query:
        return "I couldn't generate a valid SQL query for your question. Please try rephrasing it."
    
    # Execute the generated query
    result = database_service.execute_query(sql_query)
    
    if not result["success"]:
        return f"Generated SQL: {sql_query}\nDatabase error: {result['error']}"
    
    if result["count"] == 0:
        return f"Generated SQL: {sql_query}\nNo results found for the query."
    
    return f"Generated SQL: {sql_query}\nQuery results ({result['count']} rows):\n{result['data']}"

@tool
def get_top_customers(limit: int = 5) -> str:
    """
    Get the customers who spent the most money.
    
    Args:
        limit: Number of top customers to return (default: 5)
        
    Returns:
        List of top spending customers
    """
    result = database_service.get_top_customers(limit)
    
    if not result["success"]:
        return f"Error getting top customers: {result['error']}"
    
    if result["count"] == 0:
        return f"SQL: {result.get('query', 'N/A')}\nNo customers found."
    
    return f"SQL: {result.get('query', 'N/A')}\n{result['message']}:\n{result['data']}"

@tool
def get_customer_purchases(customer_name: str) -> str:
    """
    Get all products purchased by a specific customer.
    
    Args:
        customer_name: Name of the customer to search for
        
    Returns:
        List of products purchased by the customer
    """
    result = database_service.get_customer_purchases(customer_name)
    
    if not result["success"]:
        return f"Error getting customer purchases: {result['error']}"
    
    if result["count"] == 0:
        return f"SQL: {result.get('query', 'N/A')}\n{result['message']}"
    
    return f"SQL: {result.get('query', 'N/A')}\n{result['message']}:\n{result['data']}"

@tool
def get_products_by_category_tool(category: str) -> str:
    """
    Get all products in a specific category.
    
    Args:
        category: Product category (Electronics, Shoes, Clothing, Accessories)
        
    Returns:
        List of products in the category
    """
    result = database_service.get_products_by_category(category)
    
    if not result["success"]:
        return f"Error getting products by category: {result['error']}"
    
    if result["count"] == 0:
        return f"SQL: {result.get('query', 'N/A')}\n{result['message']}"
    
    return f"SQL: {result.get('query', 'N/A')}\n{result['message']}:\n{result['data']}"

@tool
def get_database_stats() -> str:
    """
    Get general statistics about the database.
    
    Returns:
        Database statistics including user and product counts
    """
    result = database_service.get_database_stats()
    
    if not result["success"]:
        return f"Error getting database stats: {result['error']}"
    
    queries_info = ""
    if "queries" in result:
        queries_info = f"\nQueries executed:\n"
        for query_type, query in result["queries"].items():
            queries_info += f"- {query_type}: {query}\n"
    
    return f"SQL: Multiple queries executed{queries_info}\n{result['message']}:\n{result['data']}"
