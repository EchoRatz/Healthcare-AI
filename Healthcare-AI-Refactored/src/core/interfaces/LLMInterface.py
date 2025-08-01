"""LLM client interface."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class LLMInterface(ABC):
    """Abstract interface for LLM clients."""
    
    @abstractmethod
    def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate response from LLM."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if LLM service is available."""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        pass
    
    @abstractmethod
    def set_parameters(self, **kwargs) -> None:
        """Set model parameters."""
        pass
    
    @abstractmethod
    def get_token_count(self, text: str) -> int:
        """Get token count for text."""
        pass