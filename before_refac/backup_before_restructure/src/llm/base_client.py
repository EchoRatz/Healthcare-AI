"""
Base LLM Client - Abstract interface for LLM clients.
Small, focused interface definition.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from prompt."""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if client can connect to LLM service."""
        pass
    
    @abstractmethod
    def get_client_info(self) -> Dict[str, Any]:
        """Get client information."""
        pass
