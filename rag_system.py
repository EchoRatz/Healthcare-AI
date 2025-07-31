from typing import List, Dict, Any, Optional
import numpy as np
from vector_database import ThaiTextVectorDatabase, SearchResult
from llm_client import LLMClient


class ThaiRAGSystem:
    """RAG (Retrieval-Augmented Generation) system for Thai text."""

    def __init__(
        self, vector_db: ThaiTextVectorDatabase, llm_client: Optional[LLMClient] = None
    ):
        """
        Initialize RAG system.

        Args:
            vector_db: Vector database instance
            llm_client: LLM client for generation
        """
        self.vector_db = vector_db
        self.llm_client = llm_client

        # Configuration
        self.default_top_k = 5
        self.default_min_relevance = 0.3
        self.default_distance_threshold = 2.0
        self.max_context_length = 2000  # characters

    def retrieve_context(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_relevance: Optional[float] = None,
        distance_threshold: Optional[float] = None,
    ) -> List[str]:
        """
        Retrieve relevant context from vector database.

        Args:
            query: Query text
            top_k: Number of results to retrieve
            min_relevance: Minimum relevance score
            distance_threshold: Maximum distance threshold

        Returns:
            List of relevant context strings
        """
        top_k = top_k or self.default_top_k
        min_relevance = min_relevance or self.default_min_relevance
        distance_threshold = distance_threshold or self.default_distance_threshold

        # Search for relevant documents
        results = self.vector_db.search(
            query, k=top_k, distance_threshold=distance_threshold
        )

        # Filter by relevance score
        relevant_results = [r for r in results if r.relevance_score >= min_relevance]

        # Sort by relevance score (highest first)
        relevant_results.sort(key=lambda x: x.relevance_score, reverse=True)

        # Extract text and limit total context length
        context_texts = []
        total_length = 0

        for result in relevant_results:
            text = result.text.strip()
            if total_length + len(text) <= self.max_context_length:
                context_texts.append(text)
                total_length += len(text)
            else:
                break

        return context_texts

    def generate_prompt(
        self, query: str, context: List[str], prompt_template: Optional[str] = None
    ) -> str:
        """
        Generate prompt for LLM with retrieved context.

        Args:
            query: User question
            context: Retrieved context
            prompt_template: Custom prompt template

        Returns:
            Complete prompt for LLM
        """
        if not context:
            return self._generate_no_context_prompt(query)

        context_text = "\n".join([f"- {ctx}" for ctx in context])

        if prompt_template:
            return prompt_template.format(context=context_text, query=query)

        # Default Thai prompt template
        prompt = f"""คุณเป็นผู้ช่วยที่ตอบคำถามโดยใช้ข้อมูลที่ให้มา กรุณาทำตามคำแนะนำต่อไปนี้:

1. ตอบคำถามโดยอ้างอิงจากข้อมูลที่ให้มาเท่านั้น
2. หากข้อมูลไม่เพียงพอ ให้บอกว่าต้องการข้อมูลเพิ่มเติม
3. ตอบเป็นภาษาไทยที่เข้าใจง่าย
4. ให้คำตอบที่กระชับและตรงประเด็น

ข้อมูลอ้างอิง:
{context_text}

คำถาม: {query}

คำตอบ:"""

        return prompt

    def _generate_no_context_prompt(self, query: str) -> str:
        """Generate prompt when no relevant context is found."""
        return f"""คำถาม: {query}

ขออภัย ไม่พบข้อมูลที่เกี่ยวข้องกับคำถามของคุณในฐานข้อมูล กรุณาลองถามคำถามอื่นหรือปรับคำถามให้ชัดเจนมากขึ้น

คำตอบ: ไม่พบข้อมูลที่เกี่ยวข้อง"""

    def answer_question(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_relevance: Optional[float] = None,
        distance_threshold: Optional[float] = None,
        prompt_template: Optional[str] = None,
        llm_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Complete RAG pipeline: retrieve context and generate answer.

        Args:
            query: User question
            top_k: Number of context items to retrieve
            min_relevance: Minimum relevance score
            distance_threshold: Maximum distance threshold
            prompt_template: Custom prompt template
            llm_params: Parameters for LLM generation

        Returns:
            Dictionary with answer, context, confidence, and metadata
        """
        # Step 1: Retrieve relevant context
        context = self.retrieve_context(query, top_k, min_relevance, distance_threshold)

        # Step 2: Generate prompt
        prompt = self.generate_prompt(query, context, prompt_template)

        # Step 3: Generate answer
        if self.llm_client:
            llm_params = llm_params or {}
            answer = self.llm_client.generate(prompt, **llm_params)
        else:
            # Fallback without LLM
            if context:
                answer = f"ตามข้อมูลที่พบ:\n\n" + "\n\n".join(context)
            else:
                answer = "ขออภัย ไม่พบข้อมูลที่เกี่ยวข้องกับคำถามของคุณในฐานข้อมูล"

        # Step 4: Calculate confidence and gather metadata
        search_results = self.vector_db.search(query, k=top_k or self.default_top_k)

        if search_results:
            avg_confidence = np.mean(
                [
                    r.relevance_score
                    for r in search_results
                    if r.relevance_score
                    >= (min_relevance or self.default_min_relevance)
                ]
            )
            max_relevance = max([r.relevance_score for r in search_results])
        else:
            avg_confidence = 0.0
            max_relevance = 0.0

        return {
            "answer": answer.strip(),
            "context": context,
            "confidence": (
                float(avg_confidence) if avg_confidence == avg_confidence else 0.0
            ),  # Handle NaN
            "max_relevance": float(max_relevance),
            "num_context_used": len(context),
            "query": query,
            "has_llm": self.llm_client is not None,
        }

    def batch_answer(self, queries: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Answer multiple questions in batch.

        Args:
            queries: List of questions
            **kwargs: Parameters passed to answer_question

        Returns:
            List of answer dictionaries
        """
        results = []
        for query in queries:
            try:
                result = self.answer_question(query, **kwargs)
                results.append(result)
            except Exception as e:
                results.append(
                    {
                        "answer": f"เกิดข้อผิดพลาด: {str(e)}",
                        "context": [],
                        "confidence": 0.0,
                        "max_relevance": 0.0,
                        "num_context_used": 0,
                        "query": query,
                        "has_llm": self.llm_client is not None,
                        "error": str(e),
                    }
                )

        return results

    def get_system_info(self) -> Dict[str, Any]:
        """Get information about the RAG system."""
        return {
            "vector_db_size": self.vector_db.size(),
            "vector_db_stats": self.vector_db.get_stats(),
            "has_llm_client": self.llm_client is not None,
            "llm_client_type": (
                type(self.llm_client).__name__ if self.llm_client else None
            ),
            "default_settings": {
                "top_k": self.default_top_k,
                "min_relevance": self.default_min_relevance,
                "distance_threshold": self.default_distance_threshold,
                "max_context_length": self.max_context_length,
            },
        }

    def update_settings(self, **kwargs) -> None:
        """
        Update default settings.

        Args:
            **kwargs: Settings to update (top_k, min_relevance, etc.)
        """
        if "top_k" in kwargs:
            self.default_top_k = kwargs["top_k"]
        if "min_relevance" in kwargs:
            self.default_min_relevance = kwargs["min_relevance"]
        if "distance_threshold" in kwargs:
            self.default_distance_threshold = kwargs["distance_threshold"]
        if "max_context_length" in kwargs:
            self.max_context_length = kwargs["max_context_length"]
