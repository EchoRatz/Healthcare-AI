"""
RAG Pipeline - Orchestrates retrieval and generation.
Small, focused class that coordinates RAG operations.
"""

from typing import Dict, Any, List, Optional
from database.search_engine import SearchEngine
from llm.base_client import BaseLLMClient
from utils.logger import get_logger

logger = get_logger(__name__)


class RAGPipeline:
    """Main RAG pipeline that orchestrates retrieval and generation."""
    
    def __init__(self, search_engine: SearchEngine, llm_client: Optional[BaseLLMClient] = None):
        """Initialize RAG pipeline."""
        self.search_engine = search_engine
        self.llm_client = llm_client
        
        logger.info("Initialized RAG pipeline")
    
    def answer_question(self, query: str, top_k: int = 5, min_relevance: float = 0.3) -> Dict[str, Any]:
        """Answer a question using RAG pipeline."""
        try:
            # Step 1: Retrieve relevant documents
            results = self.search_engine.search(query, k=top_k, min_relevance=min_relevance)
            
            # Step 2: Prepare context
            context_texts = [result.text for result in results]
            context = "\n\n".join(context_texts) if context_texts else ""
            
            # Step 3: Generate answer
            if self.llm_client and context:
                prompt = f"""Based on the following context, please answer the question.

Context:
{context}

Question: {query}

Answer:"""
                answer = self.llm_client.generate(prompt)
            else:
                # Fallback answer
                if context:
                    answer = f"Based on available information: {context[:200]}..." if len(context) > 200 else f"Based on available information: {context}"
                else:
                    answer = "Sorry, no relevant information found for your question."
            
            # Step 4: Calculate confidence
            confidence = self._calculate_confidence(context, len(results))
            
            return {
                "query": query,
                "answer": answer,
                "context": context_texts,
                "confidence": confidence,
                "num_context_used": len(results)
            }
            
        except Exception as e:
            logger.error(f"RAG pipeline failed: {e}")
            return {
                "query": query,
                "answer": "Sorry, an error occurred while processing your question.",
                "context": [],
                "confidence": 0.0,
                "num_context_used": 0,
                "error": str(e)
            }
    
    def _calculate_confidence(self, context: str, num_results: int) -> float:
        """Calculate confidence score."""
        if not context:
            return 0.1
        
        if num_results >= 3 and len(context) > 100:
            return 0.8
        elif num_results >= 2 and len(context) > 50:
            return 0.6
        elif num_results >= 1:
            return 0.4
        else:
            return 0.2
    
    def batch_answer(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Answer multiple questions."""
        results = []
        for query in queries:
            result = self.answer_question(query)
            results.append(result)
        
        logger.info(f"Processed {len(queries)} questions in batch")
        return results
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get pipeline information."""
        return {
            "search_engine_stats": self.search_engine.get_stats(),
            "has_llm": self.llm_client is not None,
            "llm_info": self.llm_client.get_client_info() if self.llm_client else None
        }
