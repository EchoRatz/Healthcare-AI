"""
Text Processor Module - Handles text processing and embedding generation.
Small, focused class that only deals with text processing.
"""

import numpy as np
from typing import List, Optional
from sentence_transformers import SentenceTransformer

from utils.logger import get_logger

logger = get_logger(__name__)


class TextProcessor:
    """Handles text preprocessing and embedding generation."""
    
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """Initialize text processor with embedding model."""
        self.model_name = model_name
        
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"Initialized text processor with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            raise
    
    def encode_text(self, text: str) -> np.ndarray:
        """Generate embedding for single text."""
        try:
            if not text or not text.strip():
                logger.warning("Empty text provided for encoding")
                return np.zeros(self.model.get_sentence_embedding_dimension())
            
            embedding = self.model.encode(text.strip())
            return embedding
            
        except Exception as e:
            logger.error(f"Text encoding failed: {e}")
            return np.zeros(self.model.get_sentence_embedding_dimension())
    
    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts."""
        try:
            # Filter out empty texts
            valid_texts = [text.strip() for text in texts if text and text.strip()]
            
            if not valid_texts:
                logger.warning("No valid texts provided for encoding")
                return np.array([])
            
            embeddings = self.model.encode(valid_texts)
            logger.debug(f"Encoded {len(valid_texts)} texts")
            return embeddings
            
        except Exception as e:
            logger.error(f"Batch text encoding failed: {e}")
            return np.array([])
    
    def preprocess_text(self, text: str) -> str:
        """Basic text preprocessing."""
        try:
            # Basic cleaning
            text = text.strip()
            # Remove excessive whitespace
            text = ' '.join(text.split())
            return text
        except Exception as e:
            logger.error(f"Text preprocessing failed: {e}")
            return text
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        try:
            return self.model.get_sentence_embedding_dimension()
        except:
            return 384  # Default dimension
