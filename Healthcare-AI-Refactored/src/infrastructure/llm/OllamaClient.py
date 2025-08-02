"""Ollama LLM client implementation."""

import requests
from typing import Optional, Dict, Any
import json

from core.interfaces.LLMInterface import LLMInterface
from shared.logging.LoggerMixin import LoggerMixin


class OllamaClient(LLMInterface, LoggerMixin):
    """Ollama LLM client implementation."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "llama2"):
        super().__init__()
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name
        self.session = requests.Session()
        self.parameters = {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "num_predict": 500
        }
    
    def is_available(self) -> bool:
        """Check if Ollama service is available."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            self.logger.debug(f"Ollama service not available: {e}")
            return False
    
    def generate_response(self, prompt: str, context: str = "", **kwargs) -> Optional[str]:
        """Generate response using Ollama."""
        try:
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            # Merge default parameters with kwargs
            options = self.parameters.copy()
            options.update({
                "temperature": kwargs.get("temperature", options["temperature"]),
                "top_p": kwargs.get("top_p", options["top_p"]),
                "top_k": kwargs.get("top_k", options["top_k"]),
                "num_predict": kwargs.get("max_tokens", options["num_predict"])
            })
            
            payload = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": options
            }
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=kwargs.get("timeout", 30)
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                self.logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to generate response: {e}")
            return None
    
    def generate_embedding(self, text: str) -> Optional[list]:
        """Generate text embedding using Ollama."""
        try:
            payload = {
                "model": self.model_name,
                "prompt": text
            }
            
            response = self.session.post(
                f"{self.base_url}/api/embeddings",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("embedding")
            else:
                self.logger.error(f"Ollama embedding error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to generate embedding: {e}")
            return None
    
    def get_token_count(self, text: str) -> int:
        """Get approximate token count for text."""
        try:
            # Simple approximation: ~4 characters per token for most models
            # This is a rough estimate since Ollama doesn't provide a direct tokenize API
            return len(text) // 4
            
        except Exception as e:
            self.logger.error(f"Failed to get token count: {e}")
            return 0
    
    def set_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Set LLM parameters."""
        try:
            # Validate and set parameters
            valid_params = ["temperature", "top_p", "top_k", "num_predict", "max_tokens"]
            
            for key, value in parameters.items():
                if key in valid_params:
                    if key == "max_tokens":
                        self.parameters["num_predict"] = value
                    else:
                        self.parameters[key] = value
                else:
                    self.logger.warning(f"Unknown parameter: {key}")
            
            self.logger.debug(f"Updated parameters: {self.parameters}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set parameters: {e}")
            return False
    
    def list_models(self) -> list:
        """List available models."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return [model["name"] for model in result.get("models", [])]
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to list models: {e}")
            return []
    
    def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama registry."""
        try:
            payload = {"name": model_name}
            
            response = self.session.post(
                f"{self.base_url}/api/pull",
                json=payload,
                timeout=300  # 5 minutes for model download
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Failed to pull model {model_name}: {e}")
            return False
    
    def get_model_info(self, model_name: str = None) -> Optional[Dict[str, Any]]:
        """Get information about a model."""
        try:
            model = model_name or self.model_name
            
            response = self.session.post(
                f"{self.base_url}/api/show",
                json={"name": model},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get model info for {model}: {e}")
            return None
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get current parameters."""
        return self.parameters.copy()
    
    def get_model_name(self) -> str:
        """Get current model name."""
        return self.model_name
    
    def list_available_models(self) -> list:
        """List available models (alias for list_models)."""
        return self.list_models()