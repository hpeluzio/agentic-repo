#!/usr/bin/env python3
"""
Query Engine for AI Agentic System
Uses LlamaIndex with ChromaDB for document storage and retrieval
"""

import os
import sys
from typing import List, Optional
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
import chromadb
from chromadb.config import Settings as ChromaSettings

class QueryEngine:
    def __init__(self, persist_dir: str = "./chroma_db"):
        """Initialize the query engine with ChromaDB persistence"""
        self.persist_dir = persist_dir
        self.chroma_client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.chroma_client.get_or_create_collection("documents")
        self.vector_store = ChromaVectorStore(chroma_collection=self.collection)
        
        # Initialize OpenAI components
        self.embed_model = OpenAIEmbedding()
        self.llm = OpenAI(model="gpt-3.5-turbo")
        
        # Set global settings
        Settings.embed_model = self.embed_model
        Settings.llm = self.llm
        
        self.index = None
        self.query_engine = None
    
    def load_documents(self, directory_path: str) -> None:
        """Load documents from a directory and create the index"""
        try:
            # Load documents
            documents = SimpleDirectoryReader(directory_path).load_data()
            
            # Create index
            self.index = VectorStoreIndex.from_documents(
                documents, 
                vector_store=self.vector_store
            )
            
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
                self.index = VectorStoreIndex.from_documents(
                    documents, 
                    vector_store=self.vector_store
                )
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
    
    # Check if documents directory exists
    docs_dir = "./documents"
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