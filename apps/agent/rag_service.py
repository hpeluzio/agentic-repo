"""
RAG Service for Document Retrieval
=================================

A simple RAG implementation that searches through company documents
and provides answers based on document content.
"""

import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

class RAGService:
    def __init__(self, documents_path: str = "documents"):
        """Initialize the RAG service with document path."""
        self.documents_path = Path(documents_path)
        self.documents = {}
        self.load_documents()
    
    def load_documents(self):
        """Load all markdown documents from the documents directory."""
        if not self.documents_path.exists():
            print(f"⚠️  Documents directory not found: {self.documents_path}")
            return
        
        for file_path in self.documents_path.rglob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract title from first line or filename
                title = self.extract_title(content, file_path.name)
                
                # Store document with metadata
                self.documents[file_path.stem] = {
                    'title': title,
                    'content': content,
                    'path': str(file_path),
                    'category': file_path.parent.name,
                    'filename': file_path.name
                }
                
            except Exception as e:
                print(f"Error loading document {file_path}: {e}")
        
        print(f"✅ Loaded {len(self.documents)} documents")
    
    def extract_title(self, content: str, filename: str) -> str:
        """Extract title from document content or filename."""
        lines = content.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            if line.startswith('# '):
                return line[2:].strip()
        return filename.replace('.md', '').replace('_', ' ').title()
    
    def search_documents(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Search for relevant documents based on query."""
        query_lower = query.lower()
        results = []
        
        for doc_id, doc in self.documents.items():
            score = 0
            content_lower = doc['content'].lower()
            title_lower = doc['title'].lower()
            
            # Simple scoring based on keyword matches
            # Title matches get higher score
            title_matches = len(re.findall(r'\b' + re.escape(query_lower) + r'\b', title_lower))
            score += title_matches * 3
            
            # Content matches
            content_matches = len(re.findall(r'\b' + re.escape(query_lower) + r'\b', content_lower))
            score += content_matches
            
            # Category matches
            if query_lower in doc['category'].lower():
                score += 2
            
            # Partial matches
            if query_lower in content_lower:
                score += 1
            
            if score > 0:
                results.append({
                    'doc_id': doc_id,
                    'title': doc['title'],
                    'category': doc['category'],
                    'score': score,
                    'content': doc['content'][:500] + "..." if len(doc['content']) > 500 else doc['content']
                })
        
        # Sort by score and return top results
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer a question based on document content."""
        if not self.documents:
            return {
                "success": False,
                "response": "No documents are available for search.",
                "sources": []
            }
        
        # Search for relevant documents
        relevant_docs = self.search_documents(question)
        
        if not relevant_docs:
            return {
                "success": False,
                "response": f"I couldn't find any relevant information about '{question}' in the available documents.",
                "sources": []
            }
        
        # Generate answer based on document content
        answer = self.generate_answer(question, relevant_docs)
        
        return {
            "success": True,
            "response": answer,
            "sources": [
                {
                    "title": doc['title'],
                    "category": doc['category'],
                    "relevance_score": doc['score']
                }
                for doc in relevant_docs
            ]
        }
    
    def generate_answer(self, question: str, docs: List[Dict[str, Any]]) -> str:
        """Generate an answer based on document content."""
        # Combine relevant document content
        combined_content = "\n\n".join([doc['content'] for doc in docs])
        
        # Simple answer generation
        answer = f"Based on the company documents, here's what I found about '{question}':\n\n"
        
        # Extract relevant sections (simplified)
        relevant_sections = self.extract_relevant_sections(question, combined_content)
        
        if relevant_sections:
            answer += relevant_sections
        else:
            # Fallback to first document content
            answer += docs[0]['content'][:800] + "..." if len(docs[0]['content']) > 800 else docs[0]['content']
        
        # Add source information
        answer += f"\n\n📚 Sources: {', '.join([doc['title'] for doc in docs[:2]])}"
        
        return answer
    
    def extract_relevant_sections(self, question: str, content: str) -> str:
        """Extract relevant sections from content based on question."""
        # Simple keyword-based extraction
        question_words = set(question.lower().split())
        lines = content.split('\n')
        relevant_lines = []
        
        for line in lines:
            line_lower = line.lower()
            if any(word in line_lower for word in question_words if len(word) > 3):
                relevant_lines.append(line.strip())
        
        return '\n'.join(relevant_lines[:10])  # Limit to 10 lines
    
    def get_available_documents(self) -> List[Dict[str, str]]:
        """Get list of available documents."""
        return [
            {
                "title": doc['title'],
                "category": doc['category'],
                "filename": doc['filename']
            }
            for doc in self.documents.values()
        ]
    
    def get_document_categories(self) -> List[str]:
        """Get list of document categories."""
        categories = set(doc['category'] for doc in self.documents.values())
        return sorted(list(categories))

# Global RAG service instance
rag_service = None

def get_rag_service() -> RAGService:
    """Get the global RAG service instance."""
    global rag_service
    if rag_service is None:
        rag_service = RAGService()
    return rag_service
