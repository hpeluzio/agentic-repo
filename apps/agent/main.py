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
            # Look for SQL execution patterns
            if "SQL Query:" in message.content:
                # Extract SQL query information
                sql_info["queries_executed"].append({
                    "type": "custom_query",
                    "description": "Custom database query",
                    "sql_query": message.content.split("SQL Query:")[-1].strip() if "SQL Query:" in message.content else None
                })
                sql_info["queries_count"] += 1
    
    return sql_info

# Pydantic models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    success: bool
    response: str
    timestamp: str
    sql_info: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    agent_loaded: bool

@app.on_event("startup")
async def startup_event():
    """Initialize the agents on startup."""
    global agent
    try:
        logger.info("Initializing LangGraph agent...")
        agent = create_graph_workflow()
        logger.info("✅ LangGraph agent initialized successfully")
        
        # Document service disabled - LlamaIndex removed
        logger.info("⚠️  Document service disabled - LlamaIndex removed")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
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

        # Process the message through the agent
        thread_id = f"api_session_{datetime.now().timestamp()}"
        result = agent.invoke(
            {"messages": [("user", request.message)]},
            config={"configurable": {"thread_id": thread_id}}
        )
        
        # Extract the response
        if result and "messages" in result:
            messages = result["messages"]
            if messages:
                last_message = messages[-1]
                response_text = last_message.content if hasattr(last_message, 'content') else str(last_message)
            else:
                response_text = "No response generated"
        else:
            response_text = "No response generated"

        # Extract SQL information
        sql_info = extract_sql_info_from_messages(result.get("messages", []))

        logger.info("✅ Message processed successfully")

        return ChatResponse(
            success=True,
            response=response_text,
            timestamp=datetime.now().isoformat(),
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
        "message": "LangGraph Agent API",
        "version": "1.0.0",
        "endpoints": {
            "database_agent": {
                "chat": "/chat",
                "health": "/health"
            },
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
