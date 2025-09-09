"""
FastAPI Service with LangGraph Agent
===================================

This service provides a REST API for the LangGraph agent.
It receives messages from NestJS and returns agent responses.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from real_rag_service import get_real_rag_service

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

async def route_query(message: str, user_role: str) -> dict:
    """Use LLM to decide which agent(s) to use for the query."""
    
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.1,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    router_prompt = f"""
You are a smart router that decides which AI agent to use for user queries.

User Role: {user_role}
Query: "{message}"

Available Agents:
1. DATABASE: For queries about data, metrics, analytics, customers, products, orders, sales, revenue, statistics, counts, etc.
2. RAG: For queries about company policies, procedures, benefits, documents, HR information, company culture, mission, vision, etc.
3. BOTH: For queries that need both data and document information.

Examples:
- "How many products do we have?" → DATABASE
- "What is our vacation policy?" → RAG
- "How many employees do we have and what is our mission?" → BOTH
- "What are our top customers?" → DATABASE
- "How do I submit an expense report?" → RAG
- "Show me our revenue and company values" → BOTH

Respond with ONLY one word:
- DATABASE: Query is about data/analytics/statistics
- RAG: Query is about documents/policies/procedures
- BOTH: Query needs both data and documents

Response:"""

    try:
        response = llm.invoke(router_prompt)
        decision = response.content.strip().upper()
        
        return {
            "agent": decision.lower(),
            "confidence": "high",
            "reasoning": f"LLM determined this is a {decision} query"
        }
        
    except Exception as e:
        logger.error(f"Error in LLM routing: {e}")
        # Fallback to RAG if LLM fails
        return {"agent": "rag", "confidence": "low", "reasoning": "Fallback due to error"}

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    user_role: Optional[str] = None

class ChatResponse(BaseModel):
    success: bool
    response: str
    timestamp: str
    sql_info: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    agent_loaded: bool

class RagRequest(BaseModel):
    message: str

class RagResponse(BaseModel):
    success: bool
    response: str
    timestamp: str
    sources: Optional[List[Dict[str, Any]]] = None

class SmartResponse(BaseModel):
    success: bool
    response: str
    timestamp: str
    agent_used: str
    routing_info: Optional[Dict[str, Any]] = None
    sql_info: Optional[Dict[str, Any]] = None
    sources: Optional[List[Dict[str, Any]]] = None

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
        
        # Add role context to the message
        user_role = request.user_role or "employee"
        
        if user_role == "employee":
            role_context = f"[SECURITY: Employee Role - RESTRICTED ACCESS] You are an employee with limited access. You can only provide general, non-sensitive information. DO NOT provide financial data, revenue, profit, salary information, or any confidential business metrics. If asked for sensitive information, politely decline and suggest contacting a manager or admin. "
        elif user_role == "manager":
            role_context = f"[SECURITY: Manager Role - MODERATE ACCESS] You are a manager with moderate access. You can provide business metrics and team information, but avoid highly sensitive financial data like exact revenue, profit margins, or personal salary information. "
        else:  # admin
            role_context = f"[SECURITY: Admin Role - FULL ACCESS] You are an administrator with full access to all data. You can provide comprehensive information including financial and sensitive data. "
        
        enhanced_message = role_context + f"User question: {request.message}"
        
        result = agent.invoke(
            {"messages": [HumanMessage(content=enhanced_message)]},
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

@app.post("/rag", response_model=RagResponse)
async def rag_chat(request: RagRequest):
    """
    RAG endpoint that answers questions based on company documents.
    """
    try:
        if not request.message or request.message.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty"
            )

        logger.info(f"Processing RAG query: {request.message[:100]}...")

        # Get RAG service
        rag_service = get_real_rag_service()
        
        # Process the question
        result = rag_service.answer_question(request.message)

        logger.info("✅ RAG query processed successfully")

        return RagResponse(
            success=result["success"],
            response=result["response"],
            timestamp=datetime.now().isoformat(),
            sources=result.get("sources", [])
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing RAG query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/rag/documents")
async def get_documents():
    """Get list of available documents."""
    try:
        rag_service = get_real_rag_service()
        documents = rag_service.get_available_documents()
        categories = rag_service.get_document_categories()
        
        return {
            "success": True,
            "documents": documents,
            "categories": categories,
            "total_documents": len(documents)
        }
    except Exception as e:
        logger.error(f"❌ Error getting documents: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/smart", response_model=SmartResponse)
async def smart_chat(request: ChatRequest):
    """
    Smart agent that automatically routes between Database and RAG agents.
    """
    try:
        if not request.message or request.message.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty"
            )

        logger.info(f"Processing Smart query: {request.message[:100]}...")

        # LLM Router - decide which agent to use
        routing_decision = await route_query(request.message, request.user_role or "employee")
        agent_used = routing_decision["agent"]
        
        logger.info(f"🧠 LLM Router decision: {agent_used} (confidence: {routing_decision['confidence']})")

        if agent_used == "database":
            # Route to Database Agent
            result = await chat(request)
            return SmartResponse(
                success=result.success,
                response=result.response,
                timestamp=result.timestamp,
                agent_used="database",
                routing_info=routing_decision,
                sql_info=result.sql_info
            )
            
        elif agent_used == "rag":
            # Route to RAG Agent
            rag_request = RagRequest(message=request.message)
            result = await rag_chat(rag_request)
            return SmartResponse(
                success=result.success,
                response=result.response,
                timestamp=result.timestamp,
                agent_used="rag",
                routing_info=routing_decision,
                sources=result.sources
            )
            
        else:  # both
            # Combine both responses
            db_result = await chat(request)
            rag_request = RagRequest(message=request.message)
            rag_result = await rag_chat(rag_request)
            
            combined_response = f"**Database Information:**\n{db_result.response}\n\n**Document Information:**\n{rag_result.response}"
            
            return SmartResponse(
                success=True,
                response=combined_response,
                timestamp=datetime.now().isoformat(),
                agent_used="both",
                routing_info=routing_decision,
                sql_info=db_result.sql_info,
                sources=rag_result.sources
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing Smart query: {e}")
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
            "rag_agent": {
                "chat": "/rag",
                "documents": "/rag/documents"
            },
            "smart_agent": {
                "chat": "/smart"
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
