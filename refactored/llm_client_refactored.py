#!/usr/bin/env python3
"""
LLM Client Interface and Implementations

This module provides a clean, extensible interface for various Language Model clients
with built-in error handling, logging, and Thai language optimization.

Author: Healthcare-AI Team
Date: 2025-08-01
Version: 3.0.0
"""

import requests
import logging
from typing import Optional, Dict, Any, List, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)


class LLMClientType(Enum):
    """Supported LLM client types."""
    OLLAMA = "ollama"
    MOCK = "mock"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class LLMResponse:
    """Response from an LLM client."""
    
    text: str
    model: str
    tokens_used: int = 0
    processing_time: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class LLMConfig:
    """Configuration for LLM clients."""
    
    model: str = "llama2"
    temperature: float = 0.7
    max_tokens: int = 500
    timeout: int = 60
    base_url: str = ""
    api_key: Optional[str] = None
    
    # Thai-specific settings
    thai_prompt_prefix: str = "ตอบเป็นภาษาไทย: "
    use_thai_optimization: bool = True


class LLMClient(ABC):
    """Abstract base class for Language Model clients."""

    def __init__(self, config: LLMConfig):
        """Initialize the LLM client with configuration."""
        self.config = config
    
    @abstractmethod
    def generate(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """Generate text from a prompt."""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the client can connect to the LLM service."""
        pass
    
    def chat(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> str:
        """
        Generate response for a chat conversation.
        Default implementation converts to single prompt.
        """
        # Convert messages to single prompt
        prompt_parts = []
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            prompt_parts.append(f"{role}: {content}")
        
        prompt = "\n".join(prompt_parts)
        return self.generate(prompt, **kwargs)
    
    def _optimize_thai_prompt(self, prompt: str) -> str:
        """Optimize prompt for Thai language generation."""
        if not self.config.use_thai_optimization:
            return prompt
        
        # Add Thai instruction if not already present
        if not any(thai_word in prompt.lower() for thai_word in ["ไทย", "thai", "ภาษาไทย"]):
            prompt = self.config.thai_prompt_prefix + prompt
        
        return prompt


class OllamaClient(LLMClient):
    """Client for Ollama local LLM inference."""

    def __init__(
        self,
        config: Optional[LLMConfig] = None,
        base_url: str = "http://localhost:11434",
        model: str = "llama2",
        timeout: int = 60,
    ):
        """
        Initialize Ollama client.
        
        Args:
            config: LLM configuration object
            base_url: Base URL for Ollama API
            model: Model name to use
            timeout: Request timeout in seconds
        """
        if config is None:
            config = LLMConfig(
                model=model,
                base_url=base_url,
                timeout=timeout
            )
        
        super().__init__(config)
        self.session = requests.Session()
        
        logger.info(f"Initialized Ollama client: {self.config.base_url}")

    def test_connection(self) -> bool:
        """Test connection to Ollama server."""
        try:
            response = self.session.get(
                f"{self.config.base_url}/api/tags", 
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama connection test failed: {e}")
            return False

    def list_models(self) -> List[str]:
        """List available models."""
        try:
            response = self.session.get(
                f"{self.config.base_url}/api/tags",
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
            
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

    def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama registry."""
        try:
            response = self.session.post(
                f"{self.config.base_url}/api/pull",
                json={"name": model_name},
                timeout=300  # Longer timeout for model pulling
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            return False

    def generate(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None, 
        temperature: Optional[float] = None, 
        **kwargs
    ) -> str:
        """Generate text using Ollama."""
        
        # Optimize for Thai if enabled
        optimized_prompt = self._optimize_thai_prompt(prompt)
        
        # Use config defaults if not specified
        max_tokens = max_tokens or self.config.max_tokens
        temperature = temperature or self.config.temperature
        
        payload = {
            "model": self.config.model,
            "prompt": optimized_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                **kwargs
            }
        }

        try:
            response = self.session.post(
                f"{self.config.base_url}/api/generate",
                json=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            generated_text = data.get("response", "")
            
            logger.debug(f"Generated {len(generated_text)} characters")
            return generated_text
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Ollama API request failed: {e}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        except Exception as e:
            error_msg = f"Unexpected error in Ollama generation: {e}"
            logger.error(error_msg)
            return f"Error: {error_msg}"

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat with Ollama using conversation format."""
        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", self.config.temperature),
                "num_predict": kwargs.get("max_tokens", self.config.max_tokens)
            }
        }

        try:
            response = self.session.post(
                f"{self.config.base_url}/api/chat",
                json=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("message", {}).get("content", "")
            
        except Exception as e:
            logger.error(f"Ollama chat failed: {e}")
            return f"Error in chat: {e}"


class MockLLMClient(LLMClient):
    """Mock LLM client for testing without actual LLM."""

    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize mock client."""
        if config is None:
            config = LLMConfig(model="mock")
        
        super().__init__(config)
        
        # Predefined responses for testing
        self.responses = {
            "default": "นี่คือคำตอบจำลองจากระบบทดสอบ",
            "greeting": "สวัสดีครับ ยินดีที่ได้ช่วยเหลือ",
            "healthcare": "เรื่องเกี่ยวกับสุขภาพนี้ควรปรึกษาแพทย์เพื่อความปลอดภัย",
            "error": "ขออภัย ไม่สามารถตอบคำถามนี้ได้"
        }
        
        logger.info("Initialized Mock LLM client")

    def test_connection(self) -> bool:
        """Mock connection test always succeeds."""
        return True

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate mock response based on prompt content."""
        prompt_lower = prompt.lower()
        
        # Simple keyword-based response selection
        if any(word in prompt_lower for word in ["สวัสดี", "hello", "hi"]):
            return self.responses["greeting"]
        elif any(word in prompt_lower for word in ["สุขภาพ", "โรง", "แพทย์", "ยา"]):
            return self.responses["healthcare"]
        elif any(word in prompt_lower for word in ["error", "ผิดพลาด"]):
            return self.responses["error"]
        else:
            return f"{self.responses['default']} สำหรับคำถาม: {prompt[:50]}..."


class OpenAIClient(LLMClient):
    """Client for OpenAI API (placeholder for future implementation)."""
    
    def __init__(self, config: Optional[LLMConfig] = None, api_key: Optional[str] = None):
        """Initialize OpenAI client."""
        if config is None:
            config = LLMConfig(
                model="gpt-3.5-turbo",
                api_key=api_key
            )
        
        super().__init__(config)
        logger.info("OpenAI client initialized (placeholder)")
    
    def test_connection(self) -> bool:
        """Test OpenAI API connection."""
        # Placeholder implementation
        return False
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate using OpenAI API."""
        # Placeholder implementation
        return "OpenAI integration not yet implemented"


def create_llm_client(
    client_type: Union[str, LLMClientType] = LLMClientType.MOCK,
    config: Optional[LLMConfig] = None,
    **kwargs
) -> LLMClient:
    """
    Factory function to create LLM clients.

    Args:
        client_type: Type of client to create
        config: LLM configuration
        **kwargs: Additional arguments for the client

    Returns:
        LLMClient instance
        
    Raises:
        ValueError: If client_type is not supported
    """
    if isinstance(client_type, str):
        try:
            client_type = LLMClientType(client_type.lower())
        except ValueError:
            raise ValueError(f"Unsupported client type: {client_type}")
    
    if client_type == LLMClientType.OLLAMA:
        return OllamaClient(config, **kwargs)
    elif client_type == LLMClientType.MOCK:
        return MockLLMClient(config)
    elif client_type == LLMClientType.OPENAI:
        return OpenAIClient(config, **kwargs)
    else:
        raise ValueError(f"Unsupported client type: {client_type}")


# Thai-optimized model recommendations
THAI_OPTIMIZED_MODELS = {
    "ollama": {
        "llama2": {
            "name": "llama2",
            "description": "General purpose, decent Thai support",
            "size": "7B parameters",
            "thai_rating": 3
        },
        "llama3": {
            "name": "llama3", 
            "description": "Improved version, better multilingual support",
            "size": "8B parameters",
            "thai_rating": 4
        },
        "mistral": {
            "name": "mistral",
            "description": "Fast and efficient, good Thai support",
            "size": "7B parameters", 
            "thai_rating": 3
        },
        "openchat": {
            "name": "openchat",
            "description": "Good conversational model with Thai support",
            "size": "7B parameters",
            "thai_rating": 4
        }
    }
}


def get_thai_model_recommendations(client_type: str = "ollama") -> Dict[str, Any]:
    """Get model recommendations for Thai language processing."""
    return THAI_OPTIMIZED_MODELS.get(client_type, {})


def setup_ollama_thai_environment():
    """Provide setup instructions for Ollama with Thai support."""
    instructions = """
    🇹🇭 Ollama Setup for Thai Language Processing:
    
    1. Install Ollama:
       curl -fsSL https://ollama.ai/install.sh | sh
    
    2. Pull recommended Thai-capable models:
       ollama pull llama3       # Best overall Thai support
       ollama pull openchat     # Good for conversations
       ollama pull mistral      # Fast and efficient
    
    3. Test Thai generation:
       ollama run llama3 "สวัสดีครับ แนะนำตัวเองหน่อย"
    
    4. For better Thai performance, consider:
       - Using specific Thai prompts
       - Setting temperature to 0.7-0.9
       - Enabling Thai prompt optimization
    """
    
    return instructions


# Example usage and testing
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(level=logging.INFO)
    
    # Test mock client
    print("Testing Mock LLM Client:")
    mock_client = create_llm_client("mock")
    
    test_prompts = [
        "สวัสดีครับ",
        "อาการปวดหัวควรทำอย่างไร",
        "เกิดข้อผิดพลาด"
    ]
    
    for prompt in test_prompts:
        response = mock_client.generate(prompt)
        print(f"Q: {prompt}")
        print(f"A: {response}\n")
    
    # Test Ollama client (if available)
    print("Testing Ollama Client:")
    try:
        ollama_client = create_llm_client("ollama")
        if ollama_client.test_connection():
            print("✅ Ollama connection successful")
            response = ollama_client.generate("สวัสดีครับ")
            print(f"Ollama response: {response}")
        else:
            print("❌ Ollama not available")
    except Exception as e:
        print(f"❌ Ollama test failed: {e}")
    
    # Show Thai model recommendations
    print("\n🇹🇭 Thai Model Recommendations:")
    recommendations = get_thai_model_recommendations()
    for model_name, info in recommendations.items():
        print(f"- {model_name}: {info['description']} (Thai Rating: {info['thai_rating']}/5)")
    
    print("\n" + setup_ollama_thai_environment())
