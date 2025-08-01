"""
Configuration settings for Thai RAG System
"""

import os
from typing import Dict, Any


class Config:
    """Configuration class for Thai RAG System."""

    # File paths
    DEFAULT_TEXT_FILE = "thai_text.txt"
    DEFAULT_INDEX_FILE = "thai_vector_index.faiss"
    DEFAULT_METADATA_FILE = "thai_metadata.json"

    # Redis Config
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 0

    # Vector Database Settings
    VECTOR_DIMENSION = 384  # For paraphrase-multilingual-MiniLM-L12-v2
    SENTENCE_TRANSFORMER_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

    # RAG System Settings
    DEFAULT_TOP_K = 10
    DEFAULT_MIN_RELEVANCE = 0.1
    DEFAULT_DISTANCE_THRESHOLD = 4.0
    MAX_CONTEXT_LENGTH = 2000  # characters

    # LLM Settings
    DEFAULT_LLM_TYPE = "ollama"
    DEFAULT_MODEL = "llama2"
    DEFAULT_OLLAMA_URL = "http://localhost:11434"
    DEFAULT_TIMEOUT = 60  # seconds

    # LLM Generation Parameters
    DEFAULT_MAX_TOKENS = 500
    DEFAULT_TEMPERATURE = 0.3
    DEFAULT_TOP_P = 0.9

    # Thai-optimized models (in order of preference)
    RECOMMENDED_MODELS = [
        "llama3",  # Best overall for Thai
        "mistral",  # Fast and efficient
        "llama2",  # Reliable fallback
        "neural-chat",  # Good for conversations
        "openchat",  # Alternative conversational model
    ]

    # Prompt Templates
    DEFAULT_THAI_PROMPT = """คุณเป็นผู้ช่วยที่ตอบคำถามโดยใช้ข้อมูลที่ให้มา กรุณาทำตามคำแนะนำต่อไปนี้:

1. ตอบคำถามโดยอ้างอิงจากข้อมูलที่ให้มาเท่านั้น
2. หากข้อมูลไม่เพียงพอ ให้บอกว่าต้องการข้อมูลเพิ่มเติม
3. ตอบเป็นภาษาไทยที่เข้าใจง่าย
4. ให้คำตอบที่กระชับและตรงประเด็น

ข้อมูลอ้างอิง:
{context}

คำถาม: {query}

คำตอบ:"""

    BILINGUAL_PROMPT = """You are a helpful assistant that answers questions using only the provided context. Please follow these guidelines:

1. Answer based solely on the provided information
2. If information is insufficient, state that you need more details
3. Respond in the same language as the question (Thai or English)
4. Be concise and direct

Reference Information:
{context}

Question: {query}

Answer:"""

    NO_CONTEXT_RESPONSE_THAI = "ขออภัย ไม่พบข้อมูลที่เกี่ยวข้องกับคำถามของคุณในฐานข้อมูล กรุณาลองถามคำถามอื่นหรือปรับคำถามให้ชัดเจนมากขึ้น"
    NO_CONTEXT_RESPONSE_EN = "Sorry, I couldn't find relevant information for your question in the database. Please try asking a different question or rephrase your query."

    @classmethod
    def get_env_config(cls) -> Dict[str, Any]:
        """Get configuration from environment variables."""
        return {
            "text_file": os.getenv("THAI_RAG_TEXT_FILE", cls.DEFAULT_TEXT_FILE),
            "index_file": os.getenv("THAI_RAG_INDEX_FILE", cls.DEFAULT_INDEX_FILE),
            "metadata_file": os.getenv(
                "THAI_RAG_METADATA_FILE", cls.DEFAULT_METADATA_FILE
            ),
            "ollama_url": os.getenv("OLLAMA_URL", cls.DEFAULT_OLLAMA_URL),
            "default_model": os.getenv("OLLAMA_MODEL", cls.DEFAULT_MODEL),
            "vector_dim": int(os.getenv("VECTOR_DIMENSION", cls.VECTOR_DIMENSION)),
            "top_k": int(os.getenv("RAG_TOP_K", cls.DEFAULT_TOP_K)),
            "min_relevance": float(
                os.getenv("RAG_MIN_RELEVANCE", cls.DEFAULT_MIN_RELEVANCE)
            ),
            "max_tokens": int(os.getenv("LLM_MAX_TOKENS", cls.DEFAULT_MAX_TOKENS)),
            "temperature": float(os.getenv("LLM_TEMPERATURE", cls.DEFAULT_TEMPERATURE)),
        }

    @classmethod
    def create_sample_env_file(cls, filename: str = ".env.example"):
        """Create a sample environment configuration file."""
        env_content = f"""# Thai RAG System Configuration

# File paths
THAI_RAG_TEXT_FILE={cls.DEFAULT_TEXT_FILE}
THAI_RAG_INDEX_FILE={cls.DEFAULT_INDEX_FILE}
THAI_RAG_METADATA_FILE={cls.DEFAULT_METADATA_FILE}

# Ollama settings
OLLAMA_URL={cls.DEFAULT_OLLAMA_URL}
OLLAMA_MODEL={cls.DEFAULT_MODEL}

# Vector database settings
VECTOR_DIMENSION={cls.VECTOR_DIMENSION}

# RAG settings
RAG_TOP_K={cls.DEFAULT_TOP_K}
RAG_MIN_RELEVANCE={cls.DEFAULT_MIN_RELEVANCE}

# LLM generation settings
LLM_MAX_TOKENS={cls.DEFAULT_MAX_TOKENS}
LLM_TEMPERATURE={cls.DEFAULT_TEMPERATURE}
"""

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(env_content)
            print(f"✓ Created sample environment file: {filename}")
        except Exception as e:
            print(f"✗ Error creating environment file: {e}")


# Global configuration instance
config = Config()


# Utility functions for common configurations
def get_thai_optimized_config() -> Dict[str, Any]:
    """Get configuration optimized for Thai text processing."""
    return {
        "top_k": 10,  # More context for Thai
        "min_relevance": 0.1,  # Much lower threshold
        "distance_threshold": 4.0,  # Higher threshold
        "temperature": 0.2,
        "max_tokens": 400,
    }


def get_conversational_config() -> Dict[str, Any]:
    """Get configuration optimized for conversational responses."""
    return {
        "top_k": 3,  # Less context for more focused answers
        "min_relevance": 0.4,  # Higher threshold for quality
        "temperature": 0.5,  # More creative responses
        "max_tokens": 300,
    }


def get_factual_config() -> Dict[str, Any]:
    """Get configuration optimized for factual, precise answers."""
    return {
        "top_k": 10,  # More context for comprehensive answers
        "min_relevance": 0.3,
        "temperature": 0.1,  # Very deterministic
        "max_tokens": 600,  # Longer answers allowed
    }


if __name__ == "__main__":
    # Create sample environment file
    Config.create_sample_env_file()

    # Display current configuration
    print("\n=== Current Configuration ===")
    env_config = Config.get_env_config()
    for key, value in env_config.items():
        print(f"{key}: {value}")

    print(f"\n=== Recommended Models ===")
    for i, model in enumerate(Config.RECOMMENDED_MODELS, 1):
        print(f"{i}. {model}")
