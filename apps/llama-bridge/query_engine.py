#!/usr/bin/env python3
"""
Query Engine for AI Agentic System
Uses LlamaIndex with Ollama (Llama 3.1) for document storage and retrieval
"""

import os
import sys
from typing import List, Optional
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.core.embeddings import MockEmbedding
from llama_index.llms.ollama import Ollama

class QueryEngine:
    def __init__(self):
        """Initialize the query engine with Ollama LLM"""
        try:
            # Initialize Ollama LLM
            self.llm = Ollama(model="llama3.1:8b", request_timeout=120.0)
            
            # Use mock embedding (no external dependencies needed)
            self.embed_model = MockEmbedding(embed_dim=384)
            
            # Set global settings
            Settings.embed_model = self.embed_model
            Settings.llm = self.llm
            
            self.index = None
            self.query_engine = None
            
            print("✅ Initialized with Ollama (Llama 3.1) and mock embeddings")
            
        except Exception as e:
            print(f"❌ Error initializing components: {e}")
            print("Make sure Ollama is running: brew services start ollama")
            sys.exit(1)
    
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

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python query_engine.py <question>")
        print("Example: python query_engine.py 'What is the content of the document?'")
        sys.exit(1)
    
    # Get question from command line arguments
    question = " ".join(sys.argv[1:])
    
    # Initialize query engine
    engine = QueryEngine()
    
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