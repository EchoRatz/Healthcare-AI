import requests
import json
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from the LLM."""
        pass


class OllamaClient(LLMClient):
    """Client for Ollama local LLM inference."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama2",
        timeout: int = 60,
    ):
        """
        Initialize Ollama client.

        Args:
            base_url: Ollama server URL
            model: Model name (e.g., 'llama2', 'llama3', 'mistral', 'codellama')
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.session = requests.Session()

        # Test connection
        if not self.test_connection():
            print(f"Warning: Cannot connect to Ollama at {base_url}")
            print("Make sure Ollama is running: ollama serve")

    def test_connection(self) -> bool:
        """Test connection to Ollama server."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def list_models(self) -> list:
        """List available models."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            print(f"Error listing models: {e}")
        return []

    def pull_model(self, model_name: str) -> bool:
        """
        Pull/download a model.

        Args:
            model_name: Name of the model to pull

        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Pulling model {model_name}...")
            response = self.session.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                timeout=300,  # 5 minutes for model download
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error pulling model {model_name}: {e}")
            return False

    def generate(
        self, prompt: str, max_tokens: int = 500, temperature: float = 0.3, **kwargs
    ) -> str:
        """
        Generate response using Ollama.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            **kwargs: Additional parameters

        Returns:
            Generated response text
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                    **kwargs,
                },
            }

            response = self.session.post(
                f"{self.base_url}/api/generate", json=payload, timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("response", "").strip()
            else:
                error_msg = f"Ollama API error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('error', 'Unknown error')}"
                except:
                    pass
                return f"Error: {error_msg}"

        except requests.exceptions.Timeout:
            return "Error: Request timed out. Try reducing max_tokens or increasing timeout."
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama. Make sure it's running on the correct port."
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def chat(self, messages: list, **kwargs) -> str:
        """
        Chat interface for conversation-style interactions.

        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters

        Returns:
            Generated response text
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": kwargs,
            }

            response = self.session.post(
                f"{self.base_url}/api/chat", json=payload, timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("content", "").strip()
            else:
                return f"Error: Ollama chat API error: {response.status_code}"

        except Exception as e:
            return f"Error in chat: {str(e)}"


class MockLLMClient(LLMClient):
    """Mock LLM client for testing without actual LLM."""

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate a mock response."""
        if "ไม่พบข้อมูล" in prompt or "no context" in prompt.lower():
            return "ขออภัย ไม่สามารถตอบคำถามนี้ได้เนื่องจากไม่มีข้อมูลที่เกี่ยวข้อง"

        # Simple mock response based on context
        return """ตามข้อมูลที่ได้รับ ฉันพบว่าหัวข้อนี้มีความสำคัญและเกี่ยวข้องกับการดำเนินชีวิตประจำวัน 

ข้อมูลที่ให้มาแสดงให้เห็นถึงคุณค่าและความสำคัญของเรื่องนี้ในหลายๆ ด้าน

(นี่คือการตอบสนองจาก Mock LLM Client เพื่อการทดสอบ)"""


def create_llm_client(client_type: str = "ollama", **kwargs) -> LLMClient:
    """
    Factory function to create LLM clients.

    Args:
        client_type: Type of client ('ollama', 'mock')
        **kwargs: Additional arguments for the client

    Returns:
        LLMClient instance
    """
    if client_type.lower() == "ollama":
        return OllamaClient(**kwargs)
    elif client_type.lower() == "mock":
        return MockLLMClient()
    else:
        raise ValueError(f"Unknown client type: {client_type}")


# Recommended Thai-capable models for Ollama
THAI_MODELS = {
    "llama2": "General purpose, decent Thai support",
    "llama3": "Improved version, better multilingual",
    "mistral": "Fast and efficient, good Thai support",
    "codellama": "Code-focused but can handle Thai text",
    "neural-chat": "Optimized for conversations",
    "openchat": "Good conversational model",
}


def setup_ollama_recommendations():
    """Print recommendations for setting up Ollama with Thai support."""
    print("=== Ollama Setup Recommendations ===")
    print("\n1. Install Ollama:")
    print("   Visit: https://ollama.ai")
    print("   Or use: curl -fsSL https://ollama.ai/install.sh | sh")

    print("\n2. Start Ollama server:")
    print("   ollama serve")

    print("\n3. Recommended models for Thai:")
    for model, desc in THAI_MODELS.items():
        print(f"   ollama pull {model}  # {desc}")

    print(f"\n4. Test with:")
    print("   ollama run llama2 'สวัสดีครับ'")

    print("\n5. Default server runs on: http://localhost:11434")


if __name__ == "__main__":
    setup_ollama_recommendations()
