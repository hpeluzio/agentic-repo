"""
Real RAG Service with LLM
========================

A true RAG implementation using:
- OpenAI Embeddings for document vectorization
- ChromaDB for vector storage and retrieval
- OpenAI GPT for answer generation
- LangChain for orchestration
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealRAGService:
    def __init__(self, documents_path: str = "documents", persist_directory: str = "./chroma_db"):
        """Initialize the real RAG service with LLM capabilities."""
        self.documents_path = Path(documents_path)
        self.persist_directory = persist_directory
        
        # Initialize OpenAI components
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="text-embedding-3-small"  # More cost-effective
        )
        
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-3.5-turbo",
            temperature=0.1  # Low temperature for consistent answers
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Initialize vector store
        self.vectorstore = None
        self.qa_chain = None
        
        # Load documents and create vector store
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """Initialize the vector store with documents."""
        try:
            logger.info("🔄 Initializing vector store...")
            
            # Check if vector store already exists
            if os.path.exists(self.persist_directory):
                logger.info("📁 Loading existing vector store...")
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
            else:
                logger.info("📚 Creating new vector store from documents...")
                documents = self._load_documents()
                
                if not documents:
                    logger.warning("⚠️  No documents found to create vector store")
                    return
                
                # Create vector store
                self.vectorstore = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    persist_directory=self.persist_directory
                )
                
                logger.info(f"✅ Vector store created with {len(documents)} document chunks")
            
            # Create QA chain
            self._create_qa_chain()
            
        except Exception as e:
            logger.error(f"❌ Error initializing vector store: {e}")
            raise
    
    def _load_documents(self) -> List[Document]:
        """Load and process documents for vectorization."""
        documents = []
        
        if not self.documents_path.exists():
            logger.warning(f"⚠️  Documents directory not found: {self.documents_path}")
            return documents
        
        for file_path in self.documents_path.rglob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract title from first line or filename
                title = self._extract_title(content, file_path.name)
                
                # Create document with metadata
                doc = Document(
                    page_content=content,
                    metadata={
                        'title': title,
                        'source': str(file_path),
                        'category': file_path.parent.name,
                        'filename': file_path.name
                    }
                )
                
                # Split document into chunks
                chunks = self.text_splitter.split_documents([doc])
                documents.extend(chunks)
                
                logger.info(f"📄 Processed {file_path.name} -> {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Error processing document {file_path}: {e}")
        
        logger.info(f"📚 Total document chunks created: {len(documents)}")
        return documents
    
    def _extract_title(self, content: str, filename: str) -> str:
        """Extract title from document content or filename."""
        lines = content.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            if line.startswith('# '):
                return line[2:].strip()
        return filename.replace('.md', '').replace('_', ' ').title()
    
    def _create_qa_chain(self):
        """Create the QA chain with custom prompt."""
        # Custom prompt template for English prompts with Portuguese response capability
        prompt_template = """
You are an AI assistant specialized in answering questions about company documents.

Context (relevant documents):
{context}

Question: {question}

Instructions:
1. Answer in the same language as the question
2. Use only the information provided in the context
3. If the information is not in the context, say you don't have that information
4. Be clear, concise and helpful
5. Cite relevant documents when appropriate
6. Maintain professional tone

Answer:"""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create retrieval QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}  # Retrieve top 3 most similar chunks
            ),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
        
        logger.info("✅ QA chain created successfully")
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer a question using the RAG pipeline."""
        try:
            if not self.qa_chain:
                return {
                    "success": False,
                    "response": "RAG service not properly initialized. Please check the logs.",
                    "sources": []
                }
            
            logger.info(f"🔍 Processing question: {question[:100]}...")
            
            # Get answer from QA chain
            result = self.qa_chain({"query": question})
            
            # Extract response and sources
            response = result["result"]
            source_docs = result["source_documents"]
            
            # Format sources
            sources = []
            for doc in source_docs:
                sources.append({
                    "title": doc.metadata.get("title", "Unknown"),
                    "category": doc.metadata.get("category", "Unknown"),
                    "source": doc.metadata.get("source", "Unknown"),
                    "relevance_score": 1.0  # ChromaDB doesn't provide scores by default
                })
            
            logger.info(f"✅ Question answered successfully. Sources: {len(sources)}")
            
            return {
                "success": True,
                "response": response,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"❌ Error answering question: {e}")
            return {
                "success": False,
                "response": f"Erro ao processar a pergunta: {str(e)}",
                "sources": []
            }
    
    def get_available_documents(self) -> List[Dict[str, Any]]:
        """Get list of available documents."""
        try:
            if not self.vectorstore:
                return []
            
            # Get all documents from vector store
            all_docs = self.vectorstore.get()
            
            # Extract unique documents
            documents = []
            seen_sources = set()
            
            for i, source in enumerate(all_docs["metadatas"]):
                if source["source"] not in seen_sources:
                    documents.append({
                        "title": source.get("title", "Unknown"),
                        "category": source.get("category", "Unknown"),
                        "source": source.get("source", "Unknown"),
                        "filename": source.get("filename", "Unknown")
                    })
                    seen_sources.add(source["source"])
            
            return documents
            
        except Exception as e:
            logger.error(f"❌ Error getting documents: {e}")
            return []
    
    def get_document_categories(self) -> List[str]:
        """Get list of document categories."""
        try:
            documents = self.get_available_documents()
            categories = list(set(doc["category"] for doc in documents))
            return sorted(categories)
        except Exception as e:
            logger.error(f"❌ Error getting categories: {e}")
            return []

# Global instance
_real_rag_service = None

def get_real_rag_service() -> RealRAGService:
    """Get the global RAG service instance."""
    global _real_rag_service
    if _real_rag_service is None:
        _real_rag_service = RealRAGService()
    return _real_rag_service
