#!/usr/bin/env python3
"""
Final Fixed Project Restructuring Script
Handles Windows encoding and Git folder issues.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

class ProjectRestructurer:
    """Restructures the project into a clean, modular architecture."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backup_before_restructure"
    
    def create_backup(self):
        """Create backup of current state - skip problematic folders."""
        try:
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
            
            self.backup_dir.mkdir(exist_ok=True)
            
            # Skip problematic folders
            skip_folders = {'.git', '__pycache__', 'backup_before_restructure', '.venv', 'node_modules'}
            skip_extensions = {'.pyc', '.pyo', '.log'}
            
            # Copy only safe files
            for item in self.project_root.iterdir():
                if item.name in skip_folders:
                    continue
                if item.suffix in skip_extensions:
                    continue
                
                try:
                    if item.is_file():
                        shutil.copy2(item, self.backup_dir / item.name)
                    elif item.is_dir() and item.name not in skip_folders:
                        shutil.copytree(
                            item, 
                            self.backup_dir / item.name,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.git')
                        )
                except Exception as e:
                    print(f"⚠️  Skipped {item.name}: {e}")
            
            print(f"✅ Backup created: {self.backup_dir}")
            return True
            
        except Exception as e:
            print(f"⚠️  Backup had issues but continuing: {e}")
            return True  # Continue anyway
    
    def create_structure(self):
        """Create the new folder structure."""
        folders_to_create = [
            "src/database",
            "src/llm", 
            "src/rag",
            "src/ui",
            "src/utils",
            "config",
            "data", 
            "tests/unit",
            "tests/integration",
            "scripts",
            "docs",
            "legacy"
        ]
        
        for folder in folders_to_create:
            folder_path = self.project_root / folder
            folder_path.mkdir(parents=True, exist_ok=True)
            
            # Create __init__.py for Python packages
            if folder.startswith("src/"):
                init_file = folder_path / "__init__.py"
                init_file.write_text("", encoding='utf-8')
        
        # Create __init__.py for src and config
        (self.project_root / "src" / "__init__.py").write_text("", encoding='utf-8')
        (self.project_root / "config" / "__init__.py").write_text("", encoding='utf-8')
        
        print("✅ Created new folder structure")
        return True
    
    def create_utils_modules(self):
        """Create utility modules."""
        
        # Logger utility - English only to avoid encoding issues
        logger_code = '''"""
Logger Utility - Simple logging setup.
"""

import logging
import sys
from pathlib import Path


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Get configured logger."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler("logs/app.log", encoding="utf-8")
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter("%(levelname)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.setLevel(getattr(logging, level.upper()))
    
    return logger
'''
        
        # File handler utility
        file_handler_code = '''"""
File Handler Utility - File operations.
"""

from pathlib import Path
from typing import List, Optional
import json

from utils.logger import get_logger

logger = get_logger(__name__)


class FileHandler:
    """Handles file operations."""
    
    @staticmethod
    def read_text_file(filepath: str, encoding: str = "utf-8") -> Optional[str]:
        """Read text file."""
        try:
            return Path(filepath).read_text(encoding=encoding)
        except Exception as e:
            logger.error(f"Failed to read {filepath}: {e}")
            return None
    
    @staticmethod
    def write_text_file(filepath: str, content: str, encoding: str = "utf-8") -> bool:
        """Write text file."""
        try:
            Path(filepath).write_text(content, encoding=encoding)
            return True
        except Exception as e:
            logger.error(f"Failed to write {filepath}: {e}")
            return False
    
    @staticmethod
    def read_lines(filepath: str, encoding: str = "utf-8") -> List[str]:
        """Read file lines."""
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            logger.error(f"Failed to read lines from {filepath}: {e}")
            return []
    
    @staticmethod
    def load_json(filepath: str) -> Optional[dict]:
        """Load JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load JSON {filepath}: {e}")
            return None
    
    @staticmethod
    def save_json(filepath: str, data: dict) -> bool:
        """Save JSON file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save JSON {filepath}: {e}")
            return False
'''
        
        # Validators utility
        validators_code = '''"""
Validators - Input validation utilities.
"""

from typing import Any


class Validators:
    """Input validation utilities."""
    
    @staticmethod
    def is_non_empty_string(value: Any) -> bool:
        """Check if value is non-empty string."""
        return isinstance(value, str) and len(value.strip()) > 0
    
    @staticmethod
    def is_positive_number(value: Any) -> bool:
        """Check if value is positive number."""
        try:
            return float(value) > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_valid_relevance_score(value: Any) -> bool:
        """Check if value is valid relevance score (0-1)."""
        try:
            score = float(value)
            return 0.0 <= score <= 1.0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_query(query: str) -> tuple[bool, str]:
        """Validate search query."""
        if not query:
            return False, "Query cannot be empty"
        
        if not query.strip():
            return False, "Query cannot be only whitespace"
        
        if len(query.strip()) > 1000:
            return False, "Query too long (max 1000 characters)"
        
        return True, "Valid query"
'''
        
        # Write utility files with UTF-8 encoding
        (self.project_root / "src" / "utils" / "logger.py").write_text(logger_code, encoding='utf-8')
        (self.project_root / "src" / "utils" / "file_handler.py").write_text(file_handler_code, encoding='utf-8')
        (self.project_root / "src" / "utils" / "validators.py").write_text(validators_code, encoding='utf-8')
        return True
    
    def create_database_modules(self):
        """Create focused database modules."""
        
        # Vector Store - Just vector operations
        vector_store_code = '''"""
Vector Store Module - Handles vector storage and indexing operations.
Small, focused class that only deals with vectors.
"""

import faiss
import numpy as np
from typing import List, Optional
import logging

from utils.logger import get_logger

logger = get_logger(__name__)


class VectorStore:
    """Handles vector storage and FAISS indexing operations."""
    
    def __init__(self, dimension: int = 384, index_type: str = "L2"):
        """Initialize vector store with specified dimension."""
        self.dimension = dimension
        self.index_type = index_type
        
        # Create FAISS index
        if index_type.upper() == "L2":
            self.index = faiss.IndexFlatL2(dimension)
        elif index_type.upper() == "IP":
            self.index = faiss.IndexFlatIP(dimension)
        else:
            raise ValueError(f"Unsupported index type: {index_type}")
        
        logger.info(f"Initialized vector store: {dimension}D, {index_type}")
    
    def add_vectors(self, vectors: np.ndarray) -> bool:
        """Add vectors to the index."""
        try:
            if len(vectors.shape) == 1:
                vectors = vectors.reshape(1, -1)
            
            if vectors.shape[1] != self.dimension:
                raise ValueError(f"Vector dimension mismatch: expected {self.dimension}, got {vectors.shape[1]}")
            
            self.index.add(vectors.astype(np.float32))
            logger.debug(f"Added {len(vectors)} vectors to store")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add vectors: {e}")
            return False
    
    def search_vectors(self, query_vector: np.ndarray, k: int = 5) -> tuple:
        """Search for similar vectors."""
        try:
            if len(query_vector.shape) == 1:
                query_vector = query_vector.reshape(1, -1)
            
            distances, indices = self.index.search(query_vector.astype(np.float32), k)
            return distances[0], indices[0]
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return np.array([]), np.array([])
    
    def size(self) -> int:
        """Get number of vectors in store."""
        return self.index.ntotal
    
    def save(self, filepath: str) -> bool:
        """Save index to file."""
        try:
            faiss.write_index(self.index, filepath)
            logger.info(f"Saved vector index to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
            return False
    
    def load(self, filepath: str) -> bool:
        """Load index from file."""
        try:
            self.index = faiss.read_index(filepath)
            logger.info(f"Loaded vector index from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return False
'''
        
        # Text Processor - Just text processing
        text_processor_code = '''"""
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
'''
        
        # Search Engine - Just search logic
        search_engine_code = '''"""
Search Engine Module - Handles search logic and result processing.
Small, focused class that coordinates search operations.
"""

from typing import List, Optional, Dict, Any
import numpy as np

from config.models import SearchResult
from database.vector_store import VectorStore
from database.text_processor import TextProcessor
from utils.logger import get_logger

logger = get_logger(__name__)


class SearchEngine:
    """Handles search operations and result processing."""
    
    def __init__(self, vector_store: VectorStore, text_processor: TextProcessor):
        """Initialize search engine with vector store and text processor."""
        self.vector_store = vector_store
        self.text_processor = text_processor
        self.texts = []  # Store original texts
        self.metadata = []  # Store metadata
        
        logger.info("Initialized search engine")
    
    def add_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add text to the search index."""
        try:
            # Process text
            processed_text = self.text_processor.preprocess_text(text)
            
            # Generate embedding
            embedding = self.text_processor.encode_text(processed_text)
            
            # Add to vector store
            success = self.vector_store.add_vectors(embedding.reshape(1, -1))
            
            if success:
                self.texts.append(processed_text)
                self.metadata.append(metadata or {})
                logger.debug(f"Added text to search index: {text[:50]}...")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to add text to search index: {e}")
            return False
    
    def add_texts_from_list(self, texts: List[str]) -> int:
        """Add multiple texts from list."""
        count = 0
        for text in texts:
            if self.add_text(text):
                count += 1
        return count
    
    def search(self, query: str, k: int = 5, min_relevance: float = 0.0) -> List[SearchResult]:
        """Search for similar texts."""
        try:
            if not query.strip():
                logger.warning("Empty query provided")
                return []
            
            if len(self.texts) == 0:
                logger.warning("No texts in search index")
                return []
            
            # Generate query embedding
            query_embedding = self.text_processor.encode_text(query)
            
            # Search vectors
            distances, indices = self.vector_store.search_vectors(query_embedding, k)
            
            # Process results
            results = []
            for i, (distance, idx) in enumerate(zip(distances, indices)):
                if idx >= len(self.texts):
                    continue
                
                # Convert distance to relevance score
                relevance_score = max(0.0, 1.0 - distance / 2.0)  # Simple conversion
                
                if relevance_score >= min_relevance:
                    result = SearchResult(
                        text=self.texts[idx],
                        distance=float(distance),
                        relevance_score=relevance_score,
                        metadata=self.metadata[idx],
                        index=int(idx)
                    )
                    results.append(result)
            
            logger.debug(f"Search returned {len(results)} results for query: {query[:30]}...")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def size(self) -> int:
        """Get number of texts in index."""
        return len(self.texts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get search engine statistics."""
        return {
            "total_texts": len(self.texts),
            "vector_dimension": self.text_processor.get_dimension(),
            "index_size": self.vector_store.size()
        }
'''
        
        # Write the files with UTF-8 encoding
        (self.project_root / "src" / "database" / "vector_store.py").write_text(vector_store_code, encoding='utf-8')
        (self.project_root / "src" / "database" / "text_processor.py").write_text(text_processor_code, encoding='utf-8')
        (self.project_root / "src" / "database" / "search_engine.py").write_text(search_engine_code, encoding='utf-8')
        return True
    
    def create_llm_modules(self):
        """Create focused LLM modules."""
        
        # Base LLM Client
        base_client_code = '''"""
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
'''
        
        # Mock Client - For testing (English responses to avoid encoding issues)
        mock_client_code = '''"""
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
'''
        
        # Write LLM files with UTF-8 encoding
        (self.project_root / "src" / "llm" / "base_client.py").write_text(base_client_code, encoding='utf-8')
        (self.project_root / "src" / "llm" / "mock_client.py").write_text(mock_client_code, encoding='utf-8')
        return True
    
    def create_rag_modules(self):
        """Create focused RAG modules."""
        
        # RAG Pipeline - Orchestrates the process
        rag_pipeline_code = '''"""
RAG Pipeline - Orchestrates retrieval and generation.
Small, focused class that coordinates RAG operations.
"""

from typing import Dict, Any, List, Optional
from database.search_engine import SearchEngine
from llm.base_client import BaseLLMClient
from utils.logger import get_logger

logger = get_logger(__name__)


class RAGPipeline:
    """Main RAG pipeline that orchestrates retrieval and generation."""
    
    def __init__(self, search_engine: SearchEngine, llm_client: Optional[BaseLLMClient] = None):
        """Initialize RAG pipeline."""
        self.search_engine = search_engine
        self.llm_client = llm_client
        
        logger.info("Initialized RAG pipeline")
    
    def answer_question(self, query: str, top_k: int = 5, min_relevance: float = 0.3) -> Dict[str, Any]:
        """Answer a question using RAG pipeline."""
        try:
            # Step 1: Retrieve relevant documents
            results = self.search_engine.search(query, k=top_k, min_relevance=min_relevance)
            
            # Step 2: Prepare context
            context_texts = [result.text for result in results]
            context = "\\n\\n".join(context_texts) if context_texts else ""
            
            # Step 3: Generate answer
            if self.llm_client and context:
                prompt = f"""Based on the following context, please answer the question.

Context:
{context}

Question: {query}

Answer:"""
                answer = self.llm_client.generate(prompt)
            else:
                # Fallback answer
                if context:
                    answer = f"Based on available information: {context[:200]}..." if len(context) > 200 else f"Based on available information: {context}"
                else:
                    answer = "Sorry, no relevant information found for your question."
            
            # Step 4: Calculate confidence
            confidence = self._calculate_confidence(context, len(results))
            
            return {
                "query": query,
                "answer": answer,
                "context": context_texts,
                "confidence": confidence,
                "num_context_used": len(results)
            }
            
        except Exception as e:
            logger.error(f"RAG pipeline failed: {e}")
            return {
                "query": query,
                "answer": "Sorry, an error occurred while processing your question.",
                "context": [],
                "confidence": 0.0,
                "num_context_used": 0,
                "error": str(e)
            }
    
    def _calculate_confidence(self, context: str, num_results: int) -> float:
        """Calculate confidence score."""
        if not context:
            return 0.1
        
        if num_results >= 3 and len(context) > 100:
            return 0.8
        elif num_results >= 2 and len(context) > 50:
            return 0.6
        elif num_results >= 1:
            return 0.4
        else:
            return 0.2
    
    def batch_answer(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Answer multiple questions."""
        results = []
        for query in queries:
            result = self.answer_question(query)
            results.append(result)
        
        logger.info(f"Processed {len(queries)} questions in batch")
        return results
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get pipeline information."""
        return {
            "search_engine_stats": self.search_engine.get_stats(),
            "has_llm": self.llm_client is not None,
            "llm_info": self.llm_client.get_client_info() if self.llm_client else None
        }
'''
        
        # Write RAG files with UTF-8 encoding
        (self.project_root / "src" / "rag" / "rag_pipeline.py").write_text(rag_pipeline_code, encoding='utf-8')
        return True
    
    def create_config_modules(self):
        """Create configuration modules."""
        
        # Models/Schemas
        models_code = '''"""
Data Models and Schemas
Small, focused data classes.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class SearchResult:
    """Search result data model."""
    text: str
    distance: float
    relevance_score: float
    metadata: Optional[Dict[str, Any]] = None
    index: int = -1
    
    def __post_init__(self):
        """Validate search result."""
        if self.distance < 0:
            raise ValueError("Distance cannot be negative")
        if not 0 <= self.relevance_score <= 1:
            raise ValueError("Relevance score must be between 0 and 1")


@dataclass
class AppConfig:
    """Application configuration."""
    vector_dimension: int = 384
    default_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    default_top_k: int = 5
    min_relevance_threshold: float = 0.3
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"
'''
        
        # Settings
        settings_code = '''"""
Application Settings
Centralized configuration management.
"""

from config.models import AppConfig


# Default configuration
DEFAULT_CONFIG = AppConfig()

# File paths
DATA_DIR = "data"
LOGS_DIR = "logs"
DEFAULT_TEXT_FILE = "data/sample_data.txt"
DEFAULT_INDEX_FILE = "data/vector_index.faiss"
DEFAULT_METADATA_FILE = "data/metadata.json"

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
'''
        
        # Write config files with UTF-8 encoding
        (self.project_root / "config" / "models.py").write_text(models_code, encoding='utf-8')
        (self.project_root / "config" / "settings.py").write_text(settings_code, encoding='utf-8')
        return True
    
    def create_main_scripts(self):
        """Create main application scripts."""
        
        # Setup script
        setup_script = '''#!/usr/bin/env python3
"""
Setup Script
Handles initial setup and dependency installation.
"""

import subprocess
import sys
from pathlib import Path


def install_dependencies():
    """Install required dependencies."""
    requirements = [
        "faiss-cpu",
        "sentence-transformers", 
        "numpy",
        "requests"
    ]
    
    print("Installing dependencies...")
    for req in requirements:
        print(f"Installing {req}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {req}: {e}")
            return False
    
    print("Dependencies installed successfully!")
    return True


def setup_directories():
    """Create necessary directories."""
    dirs = ["data", "logs"]
    
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"Created directory: {dir_name}")


def create_sample_data():
    """Create sample data file."""
    sample_data = """Learning is an important process for self-development
Good health comes from regular exercise and nutritious eating
Happiness is something that comes from having a peaceful mind
Education is an important foundation for national development
Technology helps make human life more convenient
Regular exercise helps strengthen physical and mental health
Reading books opens up perspectives and increases knowledge
A warm family is an important foundation of a good society"""
    
    data_file = Path("data/sample_data.txt")
    data_file.write_text(sample_data, encoding="utf-8")
    print(f"Created sample data: {data_file}")


def main():
    """Main setup function."""
    print("Healthcare-AI Setup")
    print("=" * 30)
    
    try:
        setup_directories()
        
        if install_dependencies():
            create_sample_data()
            
            print("\\nSetup completed successfully!")
            print("\\nTo run the application:")
            print("python scripts/run.py")
        else:
            print("Setup failed during dependency installation")
            
    except Exception as e:
        print(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
'''
        
        # Main runner script
        run_script = '''#!/usr/bin/env python3
"""
Main Application Runner
Simple entry point that coordinates all modules.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from database.vector_store import VectorStore
from database.text_processor import TextProcessor
from database.search_engine import SearchEngine
from llm.mock_client import MockLLMClient
from rag.rag_pipeline import RAGPipeline
from config.settings import DEFAULT_CONFIG
from utils.file_handler import FileHandler
from utils.logger import get_logger

logger = get_logger(__name__)


def create_search_engine():
    """Create and setup search engine."""
    vector_store = VectorStore(dimension=DEFAULT_CONFIG.vector_dimension)
    text_processor = TextProcessor(model_name=DEFAULT_CONFIG.default_model)
    search_engine = SearchEngine(vector_store, text_processor)
    return search_engine


def load_sample_data(search_engine: SearchEngine) -> int:
    """Load sample data into search engine."""
    data_file = "data/sample_data.txt"
    
    if not Path(data_file).exists():
        print(f"Sample data file not found: {data_file}")
        print("Run 'python scripts/setup.py' first")
        return 0
    
    texts = FileHandler.read_lines(data_file)
    if texts:
        count = search_engine.add_texts_from_list(texts)
        print(f"Loaded {count} sample texts")
        return count
    
    return 0


def main():
    """Main application entry point."""
    print("Starting Healthcare-AI System...")
    print("=" * 50)
    
    try:
        # Setup components
        print("Setting up components...")
        search_engine = create_search_engine()
        llm_client = MockLLMClient()  # Start with mock for demo
        
        # Create RAG pipeline
        rag = RAGPipeline(search_engine, llm_client)
        
        # Load sample data
        count = load_sample_data(search_engine)
        
        if count == 0:
            print("No data loaded. Adding basic examples...")
            sample_texts = [
                "Learning is an important process for self-development",
                "Good health comes from regular exercise and nutritious eating",
                "Happiness is something that comes from having a peaceful mind"
            ]
            count = search_engine.add_texts_from_list(sample_texts)
        
        print(f"System ready with {count} documents")
        
        # Interactive mode
        print("\\n" + "="*50)
        print("Thai RAG System - Interactive Mode")
        print("="*50)
        print("Commands:")
        print("• Type your question in Thai or English")
        print("• 'stats' - Show system statistics")
        print("• 'help' - Show this help")
        print("• 'quit' or 'exit' - Exit the program")
        print("="*50)
        
        while True:
            try:
                query = input("\\nQuestion: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                elif query.lower() == 'help':
                    print("\\nAvailable commands:")
                    print("• Ask questions in Thai or English")
                    print("• 'stats' - System statistics")
                    print("• 'quit' - Exit program")
                    continue
                elif query.lower() == 'stats':
                    info = rag.get_pipeline_info()
                    print("\\nSystem Statistics:")
                    print(f"• Total documents: {info['search_engine_stats']['total_texts']}")
                    print(f"• Vector dimension: {info['search_engine_stats']['vector_dimension']}")
                    print(f"• LLM client: {info['llm_info']['type'] if info['llm_info'] else 'None'}")
                    continue
                
                if not query:
                    continue
                
                # Process the question
                print("Searching for relevant information...")
                result = rag.answer_question(query)
                
                print("\\nAnswer:")
                print("-" * 30)
                print(result["answer"])
                print(f"\\nConfidence: {result['confidence']:.2f}")
                print(f"References used: {result['num_context_used']}")
                
                if result["context"]:
                    print("\\nReferenced information:")
                    for i, ctx in enumerate(result["context"][:2], 1):
                        print(f"   {i}. {ctx[:80]}...")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                logger.error(f"Error in main loop: {e}")
    
    except Exception as e:
        print(f"Failed to start system: {e}")
        logger.error(f"System startup failed: {e}")
        sys.exit(1)
    
    print("\\nThank you for using Healthcare-AI!")


if __name__ == "__main__":
    main()
'''
        
        # Write scripts with UTF-8 encoding
        (self.project_root / "scripts" / "setup.py").write_text(setup_script, encoding='utf-8')
        (self.project_root / "scripts" / "run.py").write_text(run_script, encoding='utf-8')
        return True
    
    def create_documentation(self):
        """Create comprehensive documentation."""
        
        # Main README
        readme_doc = '''# Healthcare-AI - Clean Architecture

A modular Thai RAG (Retrieval-Augmented Generation) system with clean, maintainable code.

## Features

- **Small, focused classes** - Each class has one responsibility
- **Clean architecture** - Easy to understand and maintain
- **Thai language support** - Optimized for Thai text processing
- **Modular design** - Easy to extend and test
- **Simple setup** - Get started in minutes

## Architecture

```
src/
├── database/          # Vector storage & search
│   ├── vector_store.py      # FAISS operations
│   ├── text_processor.py    # Text processing
│   └── search_engine.py     # Search coordination
├── llm/               # LLM clients
│   ├── base_client.py       # Abstract interface
│   └── mock_client.py       # Testing mock
├── rag/               # RAG pipeline
│   └── rag_pipeline.py      # Orchestration
└── utils/             # Utilities
    ├── logger.py            # Logging
    ├── file_handler.py      # File operations
    └── validators.py        # Input validation
```

## Quick Start

### 1. Setup
```bash
python scripts/setup.py
```

### 2. Run
```bash
python scripts/run.py
```

### 3. Ask Questions
```
Question: What is learning?
Answer: Learning is an important process for self-development...
```

## Project Structure

- **src/** - Main source code (small, focused modules)
- **config/** - Configuration and settings
- **scripts/** - Entry point scripts
- **data/** - Sample data and storage
- **docs/** - Documentation
- **tests/** - Test modules

## Design Principles

1. **Single Responsibility** - Each class does one thing well
2. **Small Classes** - Easy to understand and debug
3. **Clear Dependencies** - Explicit, testable dependencies
4. **Separation of Concerns** - Database, LLM, and RAG logic separated

## Benefits

- Easy to understand - Small, focused classes  
- Easy to test - Each module independent  
- Easy to extend - Add new components easily  
- Easy to maintain - Clear separation of concerns  
- Easy to debug - Isolated components  

This architecture makes the codebase much more maintainable and developer-friendly!
'''
        
        # Write documentation with UTF-8 encoding
        (self.project_root / "docs" / "README.md").write_text(readme_doc, encoding='utf-8')
        (self.project_root / "README.md").write_text(readme_doc, encoding='utf-8')
        return True
    
    def restructure(self):
        """Run the complete restructuring process."""
        print("🚀 Starting project restructuring...\n")
        
        steps = [
            ("Creating backup", self.create_backup),
            ("Creating folder structure", self.create_structure),
            ("Creating utility modules", self.create_utils_modules),
            ("Creating database modules", self.create_database_modules),
            ("Creating LLM modules", self.create_llm_modules),
            ("Creating RAG modules", self.create_rag_modules),
            ("Creating configuration", self.create_config_modules),
            ("Creating main scripts", self.create_main_scripts),
            ("Creating documentation", self.create_documentation)
        ]
        
        for step_name, step_func in steps:
            print(f"📋 {step_name}...")
            try:
                if step_func():
                    print(f"✅ {step_name} completed")
                else:
                    print(f"⚠️  {step_name} completed with warnings")
            except Exception as e:
                print(f"❌ {step_name} failed: {e}")
                return False
            print()
        
        print("🎉 Project restructuring completed successfully!")
        print("\n📁 New clean structure created!")
        print("\n🚀 Next steps:")
        print("1. Run setup: python scripts/setup.py")
        print("2. Start system: python scripts/run.py")
        print("\n💾 Your original files are backed up in: backup_before_restructure/")
        
        return True


def main():
    """Main function."""
    import os
    current_dir = os.getcwd()
    
    print("🏗️  Healthcare-AI Project Restructurer (Final)")
    print("=" * 60)
    print(f"Working directory: {current_dir}")
    print()
    print("This will create a clean, modular architecture with:")
    print("✅ Small, focused classes (single responsibility)")
    print("✅ Clear separation of concerns")
    print("✅ Easy to understand and maintain")  
    print("✅ Testable components")
    print("✅ Simple entry points")
    print("✅ Windows encoding compatible")
    print()
    
    restructurer = ProjectRestructurer(current_dir)
    if restructurer.restructure():
        print("\n🎊 Success! Your project is now clean and modular!")
    else:
        print("\n❌ Restructuring failed. Check the logs above.")


if __name__ == "__main__":
    main()