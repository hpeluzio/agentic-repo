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

# Import document agent
from documents_agent.document_service import DocumentService

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
document_service = None

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

# Document Agent Models
class DocumentQueryRequest(BaseModel):
    question: str
    model_configuration: Optional[Dict[str, Any]] = None

class DocumentQueryResponse(BaseModel):
    success: bool
    response: str
    model_configuration: Optional[Dict[str, Any]] = None
    timestamp: str

class DocumentLoadRequest(BaseModel):
    model_configuration: Optional[Dict[str, Any]] = None

class DocumentLoadResponse(BaseModel):
    success: bool
    message: str
    documents_count: int
    model_configuration: Optional[Dict[str, Any]] = None
    timestamp: str

class DocumentAddRequest(BaseModel):
    file_path: str
    model_configuration: Optional[Dict[str, Any]] = None

class DocumentAddResponse(BaseModel):
    success: bool
    message: str
    documents_count: Optional[int] = None
    timestamp: str

@app.on_event("startup")
async def startup_event():
    """Initialize the agents on startup."""
    global agent, document_service
    try:
        logger.info("Initializing LangGraph agent...")
        agent = create_graph_workflow()
        logger.info("✅ LangGraph agent initialized successfully")
        
        logger.info("Initializing Document service...")
        document_service = DocumentService()
        logger.info("✅ Document service initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if agent is not None and document_service is not None else "unhealthy",
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

# Document Agent Endpoints
@app.post("/documents/query", response_model=DocumentQueryResponse)
async def query_documents(request: DocumentQueryRequest):
    """
    Query documents using the document agent.
    """
    try:
        if document_service is None:
            raise HTTPException(
                status_code=503,
                detail="Document service not initialized"
            )

        if not request.question or request.question.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty"
            )

        logger.info(f"Processing document query: {request.question[:100]}...")

        # Query the document service
        result = document_service.query_documents(request.question, request.model_configuration)

        logger.info("✅ Document query processed successfully")

        return DocumentQueryResponse(
            success=result["success"],
            response=result["response"],
            model_configuration=result.get("model_config"),
            timestamp=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing document query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/documents/load", response_model=DocumentLoadResponse)
async def load_documents(request: DocumentLoadRequest):
    """
    Load documents from the documents directory.
    """
    try:
        if document_service is None:
            raise HTTPException(
                status_code=503,
                detail="Document service not initialized"
            )

        logger.info("Loading documents...")

        # Load documents
        result = document_service.load_documents(request.model_configuration)

        logger.info("✅ Documents loading completed")

        return DocumentLoadResponse(
            success=result["success"],
            message=result["message"],
            documents_count=result["documents_count"],
            model_configuration=result.get("model_config"),
            timestamp=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error loading documents: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/documents/add", response_model=DocumentAddResponse)
async def add_document(request: DocumentAddRequest):
    """
    Add a single document to the index.
    """
    try:
        if document_service is None:
            raise HTTPException(
                status_code=503,
                detail="Document service not initialized"
            )

        if not request.file_path or request.file_path.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="File path cannot be empty"
            )

        logger.info(f"Adding document: {request.file_path}")

        # Add document
        result = document_service.add_document(request.file_path, request.model_configuration)

        logger.info("✅ Document addition completed")

        return DocumentAddResponse(
            success=result["success"],
            message=result["message"],
            documents_count=result.get("documents_count"),
            timestamp=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error adding document: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/documents/models")
async def get_available_models():
    """
    Get available models for document processing.
    """
    try:
        if document_service is None:
            raise HTTPException(
                status_code=503,
                detail="Document service not initialized"
            )

        models = document_service.get_available_models()
        return {
            "success": True,
            "models": models,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error getting available models: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/documents/status")
async def get_document_status():
    """
    Get document service status.
    """
    try:
        if document_service is None:
            raise HTTPException(
                status_code=503,
                detail="Document service not initialized"
            )

        status = document_service.get_status()
        return {
            "success": True,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error getting document status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Unified AI Agent API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "database_agent": {
                "chat": "/chat",
                "health": "/health"
            },
            "document_agent": {
                "query": "/documents/query",
                "load": "/documents/load",
                "add": "/documents/add",
                "models": "/documents/models",
                "status": "/documents/status"
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
