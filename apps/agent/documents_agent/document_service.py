"""
Document Service for AI Agentic System
=====================================

This service provides document processing capabilities using LlamaIndex.
Supports multiple AI models: OpenAI, Google Gemini, and Ollama.
"""

import os
import json
from typing import List, Optional, Dict, Any
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.core.embeddings import MockEmbedding

# Import different LLM providers
try:
    from llama_index.llms.openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from llama_index.llms.ollama import Ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    from llama_index.llms.google_genai import GoogleGenAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class DocumentService:
    def __init__(self, documents_path: str = "documents"):
        """Initialize the document service"""
        self.documents_path = documents_path
        self.index = None
        self.query_engine = None
        self.current_config = None
        
        # Use mock embedding (no external dependencies needed)
        self.embed_model = MockEmbedding(embed_dim=384)
        Settings.embed_model = self.embed_model
        
        print("✅ Document service initialized")
    
    def _initialize_llm(self, model_config: Dict[str, Any]):
        """Initialize the LLM based on the configured provider"""
        provider = model_config['provider'].lower()
        model = model_config['model']
        
        if provider == 'openai':
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI not available. Install: pip install llama-index-llms-openai")
            if not model_config.get('api_key'):
                raise ValueError("OpenAI API key required")
            return OpenAI(model=model, api_key=model_config['api_key'])
        
        elif provider == 'gemini':
            if not GEMINI_AVAILABLE:
                raise ImportError("Gemini not available. Install: pip install llama-index-llms-google-genai")
            if not model_config.get('api_key'):
                raise ValueError("Gemini API key required")
            # Map model names to Google's format
            if model == 'gemini-pro':
                model = 'gemini-1.5-pro'
            elif model == 'gemini-pro-vision':
                model = 'gemini-1.5-pro-latest'
            return GoogleGenAI(model=model, api_key=model_config['api_key'])
        
        elif provider == 'ollama':
            if not OLLAMA_AVAILABLE:
                raise ImportError("Ollama not available. Install: pip install llama-index-llms-ollama")
            return Ollama(model=model, request_timeout=120.0)
        
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def load_documents(self, model_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Load documents from the documents directory and create the index"""
        try:
            # Default configuration
            if not model_config:
                model_config = {
                    "provider": "ollama",
                    "model": "llama3.1:8b",
                    "api_key": None
                }
            
            # Initialize LLM
            llm = self._initialize_llm(model_config)
            Settings.llm = llm
            self.current_config = model_config
            
            # Check if documents directory exists
            if not os.path.exists(self.documents_path):
                return {
                    "success": False,
                    "message": f"Documents directory '{self.documents_path}' not found",
                    "documents_count": 0
                }
            
            # Load documents
            documents = SimpleDirectoryReader(self.documents_path).load_data()
            
            if not documents:
                return {
                    "success": False,
                    "message": f"No documents found in '{self.documents_path}'",
                    "documents_count": 0
                }
            
            # Create index with simple vector store
            self.index = VectorStoreIndex.from_documents(documents)
            
            # Create query engine
            self.query_engine = self.index.as_query_engine()
            
            return {
                "success": True,
                "message": f"Loaded {len(documents)} documents from {self.documents_path}",
                "documents_count": len(documents),
                "model_config": model_config
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error loading documents: {str(e)}",
                "documents_count": 0
            }
    
    def query_documents(self, question: str, model_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Query the document index with a question"""
        try:
            # If new model config provided, reload with new model
            if model_config and model_config != self.current_config:
                load_result = self.load_documents(model_config)
                if not load_result["success"]:
                    return load_result
            
            # If no documents loaded, try to load with default config
            if not self.query_engine:
                load_result = self.load_documents(model_config)
                if not load_result["success"]:
                    return {
                        "success": False,
                        "response": f"No documents loaded. {load_result['message']}",
                        "model_config": self.current_config
                    }
            
            # Query the engine
            response = self.query_engine.query(question)
            
            return {
                "success": True,
                "response": str(response),
                "model_config": self.current_config
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": f"Error querying documents: {str(e)}",
                "model_config": self.current_config
            }
    
    def add_document(self, file_path: str, model_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add a single document to the index"""
        try:
            # If new model config provided, reload with new model
            if model_config and model_config != self.current_config:
                load_result = self.load_documents(model_config)
                if not load_result["success"]:
                    return load_result
            
            # If no index exists, initialize with default config
            if not self.index:
                load_result = self.load_documents(model_config)
                if not load_result["success"]:
                    return load_result
            
            # Load the new document
            documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
            
            if not documents:
                return {
                    "success": False,
                    "message": f"No content found in file: {file_path}"
                }
            
            # Add to existing index
            for doc in documents:
                self.index.insert(doc)
            
            # Recreate query engine to include new document
            self.query_engine = self.index.as_query_engine()
            
            return {
                "success": True,
                "message": f"Added document: {file_path}",
                "documents_count": len(documents)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error adding document: {str(e)}"
            }
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get list of available models and their status"""
        return {
            "ollama": {
                "available": OLLAMA_AVAILABLE,
                "models": ["llama3.1:8b", "llama3.1:70b", "mistral:7b", "codellama:7b"],
                "requires_api_key": False
            },
            "openai": {
                "available": OPENAI_AVAILABLE,
                "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
                "requires_api_key": True
            },
            "gemini": {
                "available": GEMINI_AVAILABLE,
                "models": ["gemini-pro", "gemini-pro-vision"],
                "requires_api_key": True
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current service status"""
        return {
            "documents_loaded": self.index is not None,
            "documents_path": self.documents_path,
            "current_model": self.current_config,
            "available_models": self.get_available_models()
        }
