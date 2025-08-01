"""Enhanced Chain-of-Thought Reasoning Engine with pre-plan + fetch-all approach."""

import asyncio
import concurrent.futures
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.interfaces.QueryPlannerInterface import QueryPlannerInterface
from core.interfaces.DataConnectorInterface import DataConnectorInterface
from core.interfaces.LLMInterface import LLMInterface
from shared.logging.LoggerMixin import LoggerMixin


class ChainOfThoughtEngine(LoggerMixin):
    """Enhanced reasoning engine with chain-of-thought and batch data retrieval."""
    
    def __init__(self, 
                 query_planner: QueryPlannerInterface,
                 llm_client: LLMInterface,
                 mcp_connector: Optional[DataConnectorInterface] = None,
                 pdf_connector: Optional[DataConnectorInterface] = None,
                 text_connector: Optional[DataConnectorInterface] = None):
        super().__init__()
        self.query_planner = query_planner
        self.llm_client = llm_client
        self.mcp_connector = mcp_connector
        self.pdf_connector = pdf_connector
        self.text_connector = text_connector
        
        # Validate connectors
        self._validate_connectors()
    
    def _validate_connectors(self):
        """Validate that required connectors are available."""
        if not self.query_planner.is_available():
            self.logger.warning("Query planner is not available")
        
        if not self.llm_client.is_available():
            self.logger.warning("LLM client is not available")
    
    def process_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Process a query using the chain-of-thought approach.
        
        This implements the pre-plan + fetch-all strategy:
        1. Planning Phase: Use LLM to create retrieval plan
        2. Pre-Fetching Data: Batch retrieve all needed data
        3. Reasoning Phase: Generate answer with chain-of-thought
        
        Args:
            query: The user's question
            **kwargs: Additional parameters for LLM generation
            
        Returns:
            Dictionary containing the answer and metadata
        """
        try:
            self.logger.info(f"Processing query with chain-of-thought: {query[:100]}...")
            
            # Step 1: Planning Phase
            plan = self.query_planner.plan(query)
            self.logger.info(f"Generated plan: {self._summarize_plan(plan)}")
            
            # Step 2: Pre-Fetching Data (batch retrieval)
            context_data = self._fetch_all_data(plan)
            self.logger.info(f"Retrieved data from {len(context_data)} sources")
            
            # Step 3: Reasoning Phase
            answer = self._generate_chain_of_thought_answer(query, context_data, **kwargs)
            
            # Prepare result
            result = {
                "query": query,
                "answer": answer,
                "plan": plan,
                "context_sources": self._summarize_context_sources(context_data),
                "timestamp": datetime.now().isoformat(),
                "processing_metadata": {
                    "planning_time": getattr(plan, 'planning_time', None),
                    "retrieval_time": getattr(context_data, 'retrieval_time', None),
                    "reasoning_time": getattr(answer, 'reasoning_time', None)
                }
            }
            
            self.logger.info("Successfully processed query with chain-of-thought")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process query: {e}")
            return {
                "query": query,
                "answer": "I encountered an error while processing your question.",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _fetch_all_data(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch all data according to the plan (batch retrieval)."""
        context_data = {
            'mcp': {},
            'pdf': {},
            'text': {},
            'errors': []
        }
        
        # Fetch MCP data
        if self.mcp_connector and plan.get('mcp'):
            try:
                mcp_data = self.mcp_connector.fetch(plan['mcp'])
                context_data['mcp'] = mcp_data
            except Exception as e:
                self.logger.error(f"Failed to fetch MCP data: {e}")
                context_data['errors'].append(f"MCP error: {e}")
        
        # Fetch PDF data
        if self.pdf_connector and plan.get('pdf'):
            try:
                pdf_data = self.pdf_connector.fetch(plan['pdf'])
                context_data['pdf'] = pdf_data
            except Exception as e:
                self.logger.error(f"Failed to fetch PDF data: {e}")
                context_data['errors'].append(f"PDF error: {e}")
        
        # Fetch text data
        if self.text_connector and plan.get('text'):
            try:
                text_data = self.text_connector.fetch(plan['text'])
                context_data['text'] = text_data
            except Exception as e:
                self.logger.error(f"Failed to fetch text data: {e}")
                context_data['errors'].append(f"Text error: {e}")
        
        return context_data
    
    def _generate_chain_of_thought_answer(self, query: str, context_data: Dict[str, Any], **kwargs) -> str:
        """Generate answer using chain-of-thought reasoning."""
        try:
            # Build context string
            context_string = self._build_context_string(context_data)
            
            # Build chain-of-thought prompt
            prompt = self._build_chain_of_thought_prompt(query, context_string)
            
            # Generate response
            response = self.llm_client.generate_response(
                prompt=prompt,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 1000)
            )
            
            if not response:
                return "I was unable to generate a response based on the available information."
            
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to generate chain-of-thought answer: {e}")
            return f"I encountered an error while reasoning about your question: {e}"
    
    def _build_context_string(self, context_data: Dict[str, Any]) -> str:
        """Build a formatted context string from retrieved data."""
        context_parts = []
        
        # Add MCP data
        if context_data.get('mcp'):
            context_parts.append("MCP Data:")
            for endpoint, data in context_data['mcp'].items():
                if data.get('error'):
                    context_parts.append(f"  {endpoint}: Error - {data['error']}")
                else:
                    context_parts.append(f"  {endpoint}: {str(data.get('data', 'No data'))[:500]}...")
            context_parts.append("")
        
        # Add PDF data
        if context_data.get('pdf'):
            context_parts.append("PDF Documents:")
            for file_path, data in context_data['pdf'].items():
                if data.get('error'):
                    context_parts.append(f"  {file_path}: Error - {data['error']}")
                else:
                    context_parts.append(f"  {file_path}: {data.get('text', 'No text')[:500]}...")
            context_parts.append("")
        
        # Add text data
        if context_data.get('text'):
            context_parts.append("Text Files:")
            for file_path, data in context_data['text'].items():
                if data.get('error'):
                    context_parts.append(f"  {file_path}: Error - {data['error']}")
                else:
                    context_parts.append(f"  {file_path}: {data.get('text', 'No text')[:500]}...")
            context_parts.append("")
        
        # Add errors if any
        if context_data.get('errors'):
            context_parts.append("Errors encountered:")
            for error in context_data['errors']:
                context_parts.append(f"  - {error}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _build_chain_of_thought_prompt(self, query: str, context_string: str) -> str:
        """Build the chain-of-thought prompt."""
        return f"""You are an AI assistant with access to multiple data sources. Use the information provided below to answer the user's question.

Use chain-of-thought reasoning: think step by step about what information you need, how to combine it, and what the answer should be.

Question: {query}

Available Information:
{context_string}

Please provide a clear, accurate, and helpful answer based on the information provided. If the information is insufficient, please say so. Show your reasoning process step by step."""
    
    def _summarize_plan(self, plan: Dict[str, Any]) -> Dict[str, int]:
        """Summarize the retrieval plan."""
        return {
            'mcp_requests': len(plan.get('mcp', [])),
            'pdf_requests': len(plan.get('pdf', [])),
            'text_requests': len(plan.get('text', []))
        }
    
    def _summarize_context_sources(self, context_data: Dict[str, Any]) -> Dict[str, int]:
        """Summarize the context sources used."""
        return {
            'mcp_sources': len(context_data.get('mcp', {})),
            'pdf_sources': len(context_data.get('pdf', {})),
            'text_sources': len(context_data.get('text', {})),
            'errors': len(context_data.get('errors', []))
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get information about the system capabilities."""
        return {
            'query_planner': self.query_planner.get_planning_info(),
            'llm_client': {
                'available': self.llm_client.is_available(),
                'model_info': self.llm_client.get_model_info()
            },
            'connectors': {
                'mcp': self.mcp_connector.get_connector_info() if self.mcp_connector else None,
                'pdf': self.pdf_connector.get_connector_info() if self.pdf_connector else None,
                'text': self.text_connector.get_connector_info() if self.text_connector else None
            }
        }
    
    def process_batch(self, queries: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Process multiple queries in batch."""
        results = []
        
        for query in queries:
            try:
                result = self.process_query(query, **kwargs)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to process query in batch: {e}")
                results.append({
                    "query": query,
                    "answer": "Error processing query in batch.",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        return results 