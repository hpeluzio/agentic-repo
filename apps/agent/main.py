"""
FastAPI Service with LangGraph Agent
===================================

This service provides a REST API for the LangGraph agent.
It receives messages from NestJS and returns agent responses.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file in the current directory
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Import our LangGraph agent
from agent import create_graph_workflow

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LangGraph Agent API",
    description="FastAPI service for LangGraph agent",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent = None

def extract_sql_info_from_messages(messages):
    """Extract SQL execution information from agent messages."""
    sql_info = {
        "queries_executed": [],
        "total_execution_time": 0,
        "queries_count": 0
    }
    
    for message in messages:
        if hasattr(message, 'content') and isinstance(message.content, str):
            content = message.content
            
            # Look for SQL-related information in the message content
            if any(keyword in content.lower() for keyword in [
                "query results", "sql:", "top", "customers", "purchases", 
                "products", "database", "select", "from", "where", "comprou",
                "gastaram", "categoria", "preço", "total", "quantidade"
            ]):
                sql_info["queries_count"] += 1
                
                # Try to extract the actual SQL query from the content
                sql_query = None
                if "SQL:" in content:
                    # Extract SQL query after "SQL:"
                    sql_start = content.find("SQL:") + 4
                    # Look for the end of the SQL query (next line or end of content)
                    sql_end = content.find("\n", sql_start)
                    if sql_end == -1:
                        sql_end = len(content)
                    sql_query = content[sql_start:sql_end].strip()
                    
                    # If the query is too short, try to get more lines
                    if len(sql_query) < 50 and sql_end < len(content):
                        # Look for more lines of SQL
                        next_line_start = sql_end + 1
                        next_line_end = content.find("\n", next_line_start)
                        if next_line_end == -1:
                            next_line_end = len(content)
                        next_line = content[next_line_start:next_line_end].strip()
                        
                        # If next line looks like SQL (contains SELECT, FROM, WHERE, etc.)
                        if any(keyword in next_line.upper() for keyword in ["SELECT", "FROM", "WHERE", "JOIN", "ORDER", "GROUP"]):
                            sql_query += " " + next_line
                
                # Try to extract query details from the content
                if ("top" in content.lower() and "customers" in content.lower()) or "gastaram" in content.lower():
                    sql_info["queries_executed"].append({
                        "type": "top_customers",
                        "description": "Get top spending customers",
                        "sql_query": sql_query
                    })
                elif "purchases" in content.lower() or "comprou" in content.lower():
                    sql_info["queries_executed"].append({
                        "type": "customer_purchases", 
                        "description": "Get customer purchases",
                        "sql_query": sql_query
                    })
                elif "products" in content.lower() or "categoria" in content.lower():
                    sql_info["queries_executed"].append({
                        "type": "products_by_category",
                        "description": "Get products by category",
                        "sql_query": sql_query
                    })
                else:
                    sql_info["queries_executed"].append({
                        "type": "custom_query",
                        "description": "Custom database query",
                        "sql_query": sql_query
                    })
    
    return sql_info if sql_info["queries_count"] > 0 else None

class ChatRequest(BaseModel):
    message: str
    timestamp: str = None

class ChatResponse(BaseModel):
    response: str
    timestamp: str
    success: bool
    sql_info: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    agent_loaded: bool

@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup."""
    global agent
    try:
        logger.info("Initializing LangGraph agent...")
        agent = create_graph_workflow()
        logger.info("✅ Agent initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize agent: {e}")
        raise

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if agent is not None else "unhealthy",
        timestamp=datetime.now().isoformat(),
        agent_loaded=agent is not None
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint that processes messages through the LangGraph agent.
    """
    try:
        if agent is None:
            raise HTTPException(
                status_code=503, 
                detail="Agent not initialized"
            )

        if not request.message or request.message.strip() == "":
            raise HTTPException(
                status_code=400, 
                detail="Message cannot be empty"
            )

        logger.info(f"Processing message: {request.message[:100]}...")

        # Process message through LangGraph agent
        thread_id = f"api_session_{datetime.now().timestamp()}"
        
        # Create initial state
        initial_state = {
            "messages": [{"role": "user", "content": request.message}]
        }

        # Run the agent
        result = await agent.ainvoke(initial_state, config={"configurable": {"thread_id": thread_id}})
        
        # Extract response
        if result and "messages" in result:
            last_message = result["messages"][-1]
            response_text = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            # Extract SQL information from messages
            sql_info = extract_sql_info_from_messages(result["messages"])
        else:
            response_text = "I'm sorry, I couldn't process your request."
            sql_info = None

        logger.info("✅ Message processed successfully")

        return ChatResponse(
            response=response_text,
            timestamp=datetime.now().isoformat(),
            success=True,
            sql_info=sql_info
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing message: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "LangGraph Agent API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "chat": "/chat",
            "health": "/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"🚀 Starting FastAPI server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
