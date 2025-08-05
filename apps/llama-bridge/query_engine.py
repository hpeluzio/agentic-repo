#!/usr/bin/env python3
"""
Query Engine for AI Agentic System
Supports multiple AI models: OpenAI, Gemini, and Ollama (Llama 3.1)
"""

import os
import sys
import json
from typing import List, Optional
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

class QueryEngine:
    def __init__(self, model_config: dict = None):
        """Initialize the query engine with specified model configuration"""
        try:
            # Default configuration
            self.config = model_config or {
                "provider": "ollama",
                "model": "llama3.1:8b",
                "api_key": None
            }
            
            # Initialize LLM based on provider
            self.llm = self._initialize_llm()
            
            # Use mock embedding (no external dependencies needed)
            self.embed_model = MockEmbedding(embed_dim=384)
            
            # Set global settings
            Settings.embed_model = self.embed_model
            Settings.llm = self.llm
            
            self.index = None
            self.query_engine = None
            
            print(f"✅ Initialized with {self.config['provider'].upper()} ({self.config['model']}) and mock embeddings")
            
        except Exception as e:
            print(f"❌ Error initializing components: {e}")
            if self.config['provider'] == 'ollama':
                print("Make sure Ollama is running: brew services start ollama")
            elif self.config['provider'] == 'openai':
                print("Please set your OPENAI_API_KEY environment variable")
            elif self.config['provider'] == 'gemini':
                print("Please set your GEMINI_API_KEY environment variable")
            sys.exit(1)
    
    def _initialize_llm(self):
        """Initialize the LLM based on the configured provider"""
        provider = self.config['provider'].lower()
        model = self.config['model']
        
        if provider == 'openai':
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI not available. Install: pip install llama-index-llms-openai")
            if not self.config.get('api_key'):
                raise ValueError("OpenAI API key required")
            return OpenAI(model=model, api_key=self.config['api_key'])
        
        elif provider == 'gemini':
            if not GEMINI_AVAILABLE:
                raise ImportError("Gemini not available. Install: pip install llama-index-llms-google-genai")
            if not self.config.get('api_key'):
                raise ValueError("Gemini API key required")
            # Map model names to Google's format
            if model == 'gemini-pro':
                model = 'gemini-1.5-pro'
            elif model == 'gemini-pro-vision':
                model = 'gemini-1.5-pro-latest'
            return GoogleGenAI(model=model, api_key=self.config['api_key'])
        
        elif provider == 'ollama':
            if not OLLAMA_AVAILABLE:
                raise ImportError("Ollama not available. Install: pip install llama-index-llms-ollama")
            return Ollama(model=model, request_timeout=120.0)
        
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def load_documents(self, directory_path: str) -> None:
        """Load documents from a directory and create the index"""
        try:
            # Load documents
            documents = SimpleDirectoryReader(directory_path).load_data()
            
            # Create index with simple vector store
            self.index = VectorStoreIndex.from_documents(documents)
            
            # Create query engine
            self.query_engine = self.index.as_query_engine()
            
            print(f"✅ Loaded {len(documents)} documents from {directory_path}")
            
        except Exception as e:
            print(f"❌ Error loading documents: {e}")
            sys.exit(1)
    
    def query(self, question: str) -> str:
        """Query the document index with a question"""
        if not self.query_engine:
            return "❌ No documents loaded. Please load documents first."
        
        try:
            response = self.query_engine.query(question)
            return str(response)
        except Exception as e:
            return f"❌ Error querying: {e}"
    
    def add_document(self, file_path: str) -> None:
        """Add a single document to the index"""
        try:
            documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
            
            if not self.index:
                self.index = VectorStoreIndex.from_documents(documents)
                self.query_engine = self.index.as_query_engine()
            else:
                # Add to existing index
                for doc in documents:
                    self.index.insert(doc)
            
            print(f"✅ Added document: {file_path}")
            
        except Exception as e:
            print(f"❌ Error adding document: {e}")

def get_available_models():
    """Get list of available models and their status"""
    models = {
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
    return models

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python query_engine.py <question> [--model <provider:model>] [--api-key <key>]")
        print("Examples:")
        print("  python query_engine.py 'What is the content?'")
        print("  python query_engine.py 'What is the content?' --model ollama:llama3.1:8b")
        print("  python query_engine.py 'What is the content?' --model openai:gpt-3.5-turbo --api-key sk-...")
        print("  python query_engine.py 'What is the content?' --model gemini:gemini-pro --api-key AIza...")
        print("\nAvailable models:")
        models = get_available_models()
        for provider, info in models.items():
            status = "✅" if info['available'] else "❌"
            print(f"  {status} {provider}: {', '.join(info['models'])}")
        sys.exit(1)
    
    # Parse command line arguments
    question = sys.argv[1]
    model_config = {"provider": "ollama", "model": "llama3.1:8b", "api_key": None}
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--model" and i + 1 < len(sys.argv):
            model_spec = sys.argv[i + 1]
            if ":" in model_spec:
                provider, model = model_spec.split(":", 1)
                model_config["provider"] = provider
                model_config["model"] = model
            i += 2
        elif sys.argv[i] == "--api-key" and i + 1 < len(sys.argv):
            model_config["api_key"] = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    # Initialize query engine
    engine = QueryEngine(model_config)
    
    # Check if documents directory exists (relative to script location)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(script_dir, "documents")
    
    if os.path.exists(docs_dir):
        engine.load_documents(docs_dir)
    else:
        print(f"⚠️  Documents directory '{docs_dir}' not found.")
        print("Create a 'documents' folder and add your files there.")
        sys.exit(1)
    
    # Query the engine
    print(f"\n🤖 Query: {question}")
    print("-" * 50)
    response = engine.query(question)
    print(response)

if __name__ == "__main__":
    main() 