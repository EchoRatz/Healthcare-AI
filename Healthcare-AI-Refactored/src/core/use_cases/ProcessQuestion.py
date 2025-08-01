"""Process question use case."""

from typing import Optional, List, Dict, Any
from datetime import datetime

from core.entities.Document import Document
from core.interfaces.LLMInterface import LLMInterface
from core.use_cases.SearchDocuments import SearchDocuments
from shared.logging.LoggerMixin import get_logger


class ProcessQuestion:
    """Use case for processing questions using LLM and document search."""
    
    def __init__(self, llm_client: LLMInterface, search_documents: SearchDocuments):
        self.llm_client = llm_client
        self.search_documents = search_documents
        self.logger = get_logger(__name__)
    
    def process(self, question: str, context_size: int = 3, **kwargs) -> Dict[str, Any]:
        """Process a question and generate response."""
        try:
            self.logger.info(f"Processing question: {question[:100]}...")
            
            # Search for relevant documents
            relevant_docs = self.search_documents.search_by_query(question, context_size)
            
            if not relevant_docs:
                self.logger.warning("No relevant documents found")
                return {
                    "question": question,
                    "answer": "I couldn't find any relevant information to answer your question.",
                    "sources": [],
                    "confidence": 0.0,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Build context from relevant documents
            context = self._build_context(relevant_docs)
            
            # Generate response using LLM
            response = self.llm_client.generate_response(
                prompt=self._build_prompt(question),
                context=context,
                **kwargs
            )
            
            if not response:
                self.logger.error("Failed to generate LLM response")
                return {
                    "question": question,
                    "answer": "I encountered an error while generating the response.",
                    "sources": [],
                    "confidence": 0.0,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Calculate confidence based on document relevance
            confidence = self._calculate_confidence(relevant_docs)
            
            # Prepare sources
            sources = [
                {
                    "document_id": doc.id,
                    "relevance_score": float(score),
                    "content_preview": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                    "metadata": doc.metadata
                }
                for doc, score in relevant_docs
            ]
            
            result = {
                "question": question,
                "answer": response,
                "sources": sources,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Successfully processed question with {len(sources)} sources")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process question: {e}")
            return {
                "question": question,
                "answer": "An error occurred while processing your question.",
                "sources": [],
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _build_context(self, relevant_docs: List[tuple]) -> str:
        """Build context string from relevant documents."""
        context_parts = []
        
        for i, (doc, score) in enumerate(relevant_docs, 1):
            context_parts.append(f"Document {i} (relevance: {score:.3f}):")
            context_parts.append(doc.content)
            context_parts.append("")  # Empty line for separation
        
        return "\n".join(context_parts)
    
    def _build_prompt(self, question: str) -> str:
        """Build the prompt for the LLM."""
        return f"""Based on the provided context documents, please answer the following question. 
If the context doesn't contain enough information to answer the question, please say so.

Question: {question}

Please provide a clear, accurate, and helpful answer based on the context provided."""
    
    def _calculate_confidence(self, relevant_docs: List[tuple]) -> float:
        """Calculate confidence score based on document relevance."""
        if not relevant_docs:
            return 0.0
        
        # Simple confidence calculation based on top document score and number of documents
        top_score = relevant_docs[0][1] if relevant_docs else 0.0
        doc_count_factor = min(len(relevant_docs) / 3.0, 1.0)  # More docs = higher confidence up to 3
        
        # Normalize score (assuming lower distance = higher relevance)
        # This is a placeholder - actual calculation would depend on your distance metric
        normalized_score = max(0.0, 1.0 - (top_score / 100.0))
        
        confidence = (normalized_score * 0.7) + (doc_count_factor * 0.3)
        return min(max(confidence, 0.0), 1.0)  # Clamp between 0 and 1
    
    def process_batch(self, questions: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Process multiple questions."""
        results = []
        
        for question in questions:
            try:
                result = self.process(question, **kwargs)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to process question in batch: {e}")
                results.append({
                    "question": question,
                    "answer": "Error processing question in batch.",
                    "sources": [],
                    "confidence": 0.0,
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e)
                })
        
        return results