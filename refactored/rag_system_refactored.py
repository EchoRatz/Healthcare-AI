#!/usr/bin/env python3
"""
Thai RAG System - Retrieval-Augmented Generation for Thai Text

This module provides a clean, efficient RAG (Retrieval-Augmented Generation)
system specifically optimized for Thai language processing.

Author: Healthcare-AI Team
Date: 2025-08-01
Version: 3.0.0
"""

import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime

from vector_database import ThaiTextVectorDatabase, SearchResult
from llm_client import LLMClient

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class RAGResponse:
    """Response from the RAG system."""
    
    answer: str
    query: str
    sources: List[SearchResult] = field(default_factory=list)
    confidence: float = 0.0
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "answer": self.answer,
            "query": self.query,
            "sources": [
                {
                    "text": source.text,
                    "relevance_score": source.relevance_score,
                    "distance": source.distance
                }
                for source in self.sources
            ],
            "confidence": self.confidence,
            "processing_time": self.processing_time,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class RAGConfig:
    """Configuration for the RAG system."""
    
    # Search parameters
    default_top_k: int = 5
    min_relevance_threshold: float = 0.3
    distance_threshold: float = 2.0
    
    # Context parameters
    max_context_length: int = 2000
    context_overlap: int = 100
    
    # Generation parameters
    default_temperature: float = 0.7
    max_tokens: int = 500
    
    # Prompt templates
    default_prompt_template: str = """ใช้ข้อมูลที่ให้มาด้านล่างเพื่อตอบคำถาม:

คำถาม: {query}

ข้อมูลอ้างอิง:
{context}

คำตอบ:"""
    
    no_context_template: str = """คำถาม: {query}

ไม่พบข้อมูลที่เกี่ยวข้องในฐานข้อมูล กรุณาตอบตามความรู้ทั่วไปของคุณ:"""


class ThaiRAGSystem:
    """
    Advanced RAG (Retrieval-Augmented Generation) system for Thai text.
    
    This system combines vector-based retrieval with language model generation
    to provide accurate, contextual answers to Thai language queries.
    
    Features:
    - Semantic search in Thai text corpus
    - Context-aware answer generation
    - Configurable retrieval and generation parameters
    - Comprehensive logging and error handling
    """
    
    def __init__(
        self, 
        vector_db: ThaiTextVectorDatabase, 
        llm_client: Optional[LLMClient] = None,
        config: Optional[RAGConfig] = None
    ):
        """
        Initialize the Thai RAG system.
        
        Args:
            vector_db: Vector database for retrieval
            llm_client: Language model client for generation
            config: RAG system configuration
        """
        self.vector_db = vector_db
        self.llm_client = llm_client
        self.config = config or RAGConfig()
        
        logger.info("Thai RAG System initialized")
        logger.info(f"Vector DB size: {self.vector_db.size()}")
        logger.info(f"LLM client: {'Available' if self.llm_client else 'Not configured'}")
    
    def retrieve_context(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_relevance: Optional[float] = None,
        distance_threshold: Optional[float] = None,
    ) -> List[SearchResult]:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: The search query
            top_k: Number of results to retrieve
            min_relevance: Minimum relevance score
            distance_threshold: Maximum distance threshold
            
        Returns:
            List of relevant SearchResult objects
        """
        # Use config defaults if not specified
        top_k = top_k or self.config.default_top_k
        min_relevance = min_relevance or self.config.min_relevance_threshold
        distance_threshold = distance_threshold or self.config.distance_threshold
        
        try:
            results = self.vector_db.search(
                query=query,
                k=top_k,
                distance_threshold=distance_threshold,
                min_relevance=min_relevance
            )
            
            logger.debug(f"Retrieved {len(results)} context items for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            return []
    
    def generate_prompt(
        self, 
        query: str, 
        context_results: List[SearchResult], 
        template: Optional[str] = None
    ) -> str:
        """
        Generate a prompt for the language model.
        
        Args:
            query: The user query
            context_results: Retrieved context results
            template: Custom prompt template
            
        Returns:
            Formatted prompt string
        """
        if not context_results:
            template = template or self.config.no_context_template
            return template.format(query=query)
        
        # Use default template if none provided
        template = template or self.config.default_prompt_template
        
        # Format context
        context_texts = []
        total_length = 0
        
        for result in context_results:
            text = result.text
            
            # Check context length limit
            if total_length + len(text) > self.config.max_context_length:
                # Truncate to fit
                remaining_length = self.config.max_context_length - total_length
                if remaining_length > 100:  # Only add if meaningful length remains
                    text = text[:remaining_length] + "..."
                    context_texts.append(f"- {text}")
                break
            
            context_texts.append(f"- {text}")
            total_length += len(text)
        
        context = "\n".join(context_texts)
        
        return template.format(query=query, context=context)
    
    def generate_answer(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate an answer using the language model.
        
        Args:
            prompt: The formatted prompt
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional generation parameters
            
        Returns:
            Generated answer text
        """
        if not self.llm_client:
            logger.warning("No LLM client configured")
            return "ไม่สามารถสร้างคำตอบได้ เนื่องจากไม่มีการตั้งค่า Language Model"
        
        try:
            # Use config defaults if not specified
            temperature = temperature or self.config.default_temperature
            max_tokens = max_tokens or self.config.max_tokens
            
            answer = self.llm_client.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return answer.strip()
            
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            return f"เกิดข้อผิดพลาดในการสร้างคำตอบ: {str(e)}"
    
    def answer_question(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_relevance: Optional[float] = None,
        distance_threshold: Optional[float] = None,
        prompt_template: Optional[str] = None,
        **generation_kwargs
    ) -> RAGResponse:
        """
        Answer a question using the RAG pipeline.
        
        Args:
            query: The user question
            top_k: Number of context items to retrieve
            min_relevance: Minimum relevance threshold
            distance_threshold: Maximum distance threshold
            prompt_template: Custom prompt template
            **generation_kwargs: Additional generation parameters
            
        Returns:
            RAGResponse object with answer and metadata
        """
        start_time = datetime.now()
        
        try:
            # Step 1: Retrieve relevant context
            context_results = self.retrieve_context(
                query=query,
                top_k=top_k,
                min_relevance=min_relevance,
                distance_threshold=distance_threshold
            )
            
            # Step 2: Generate prompt
            prompt = self.generate_prompt(
                query=query,
                context_results=context_results,
                template=prompt_template
            )
            
            # Step 3: Generate answer
            answer = self.generate_answer(prompt, **generation_kwargs)
            
            # Calculate confidence based on context quality
            confidence = self._calculate_confidence(context_results)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            response = RAGResponse(
                answer=answer,
                query=query,
                sources=context_results,
                confidence=confidence,
                processing_time=processing_time,
                metadata={
                    "context_count": len(context_results),
                    "prompt_length": len(prompt),
                    "answer_length": len(answer)
                }
            )
            
            logger.info(f"Question answered in {processing_time:.2f}s, confidence: {confidence:.2f}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to answer question: {e}")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return RAGResponse(
                answer=f"เกิดข้อผิดพลาด: {str(e)}",
                query=query,
                sources=[],
                confidence=0.0,
                processing_time=processing_time,
                metadata={"error": str(e)}
            )
    
    def batch_answer(
        self, 
        queries: List[str], 
        **kwargs
    ) -> List[RAGResponse]:
        """
        Answer multiple questions in batch.
        
        Args:
            queries: List of questions
            **kwargs: Arguments passed to answer_question
            
        Returns:
            List of RAGResponse objects
        """
        results = []
        
        logger.info(f"Processing batch of {len(queries)} questions")
        
        for i, query in enumerate(queries):
            logger.debug(f"Processing question {i+1}/{len(queries)}: {query[:50]}...")
            
            response = self.answer_question(query, **kwargs)
            results.append(response)
        
        logger.info("Batch processing completed")
        return results
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        db_stats = self.vector_db.get_stats()
        
        return {
            "system_name": "Thai RAG System",
            "version": "3.0.0",
            "vector_database": {
                "size": db_stats.total_entries,
                "dimension": db_stats.vector_dimension,
                "model": db_stats.model_name,
                "memory_usage_mb": db_stats.memory_usage_mb,
                "categories": db_stats.categories
            },
            "llm_client": {
                "configured": self.llm_client is not None,
                "type": type(self.llm_client).__name__ if self.llm_client else None
            },
            "configuration": {
                "default_top_k": self.config.default_top_k,
                "min_relevance_threshold": self.config.min_relevance_threshold,
                "distance_threshold": self.config.distance_threshold,
                "max_context_length": self.config.max_context_length
            }
        }
    
    def update_config(self, **kwargs) -> None:
        """Update system configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.info(f"Updated config: {key} = {value}")
            else:
                logger.warning(f"Unknown config parameter: {key}")
    
    def _calculate_confidence(self, context_results: List[SearchResult]) -> float:
        """Calculate confidence score based on context quality."""
        if not context_results:
            return 0.0
        
        # Base confidence on average relevance and number of results
        avg_relevance = sum(r.relevance_score for r in context_results) / len(context_results)
        result_factor = min(1.0, len(context_results) / self.config.default_top_k)
        
        return min(1.0, avg_relevance * result_factor)


def create_thai_rag_system(
    vector_db: ThaiTextVectorDatabase,
    llm_client: Optional[LLMClient] = None,
    **config_kwargs
) -> ThaiRAGSystem:
    """
    Factory function to create a Thai RAG system.
    
    Args:
        vector_db: Vector database instance
        llm_client: Language model client
        **config_kwargs: Configuration parameters
        
    Returns:
        ThaiRAGSystem instance
    """
    config = RAGConfig(**config_kwargs) if config_kwargs else RAGConfig()
    return ThaiRAGSystem(vector_db, llm_client, config)


# Example usage and testing
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(level=logging.INFO)
    
    from vector_database import create_thai_vector_database
    from llm_client import MockLLMClient
    
    # Create vector database with sample data
    db = create_thai_vector_database()
    
    sample_texts = [
        "โรงพยาบาลมีแผนกฉุกเฉินเปิด 24 ชั่วโมง",
        "สิทธิการรักษาพยาบาลในระบบประกันสุขภาพแห่งชาติ",
        "การตรวจสุขภาพประจำปีสำหรับผู้สูงอายุ",
        "ยาและการใช้ยาอย่างปลอดภัย",
        "การป้องกันโรคติดเชื้อไวรัส"
    ]
    
    for text in sample_texts:
        db.add_text(text, {"category": "healthcare"})
    
    # Create RAG system with mock LLM
    llm_client = MockLLMClient()
    rag_system = create_thai_rag_system(db, llm_client)
    
    # Test question answering
    query = "โรงพยาบาลเปิดกี่โมง"
    response = rag_system.answer_question(query)
    
    print("RAG System Test:")
    print(f"Question: {response.query}")
    print(f"Answer: {response.answer}")
    print(f"Confidence: {response.confidence:.2f}")
    print(f"Sources: {len(response.sources)}")
    
    # Print system info
    info = rag_system.get_system_info()
    print(f"\nSystem Info:")
    print(f"- Vector DB size: {info['vector_database']['size']}")
    print(f"- LLM configured: {info['llm_client']['configured']}")
