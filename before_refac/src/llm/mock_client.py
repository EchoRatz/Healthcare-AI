"""
Mock LLM Client - For testing without real LLM.
Small, focused mock implementation.
"""

from typing import Dict, Any
import random

from llm.base_client import BaseLLMClient


class MockLLMClient(BaseLLMClient):
    """Mock LLM client for testing."""
    
    def __init__(self):
        """Initialize mock client."""
        self.responses = [
            "This is a test response from the system based on the retrieved information.",
            "Thank you for your question. Here is a sample answer based on relevant data.",
            "Based on the search results, here is the information found.",
            "The system found relevant information and provides this response."
        ]
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate mock response."""
        return random.choice(self.responses)
    
    def test_connection(self) -> bool:
        """Mock connection test (always returns True)."""
        return True
    
    def get_client_info(self) -> Dict[str, Any]:
        """Get mock client information."""
        return {
            "type": "mock",
            "model": "mock-model",
            "connected": True
        }
