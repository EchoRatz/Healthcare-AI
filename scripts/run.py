#!/usr/bin/env python3
"""
Main Application Runner
Simple entry point that coordinates all modules.
"""

import sys
from pathlib import Path

# Add both src and project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))
sys.path.append(str(project_root))

# Remove 'src.' prefix from imports since src is in the path
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
        # Create metadata for each text
        metadata_list = []
        for i, text in enumerate(texts):
            metadata_list.append({
                "source": "sample_data.txt",
                "index": i,
                "length": len(text),
                "loaded_at": str(Path(data_file).stat().st_mtime),
                "text": text
            })
        
        count = search_engine.add_texts_from_list(texts, metadata_list)
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
            
            # Create metadata for basic examples
            sample_metadata = []
            for i, text in enumerate(sample_texts):
                sample_metadata.append({
                    "source": "basic_examples",
                    "index": i,
                    "category": "general",
                    "length": len(text)
                })
            
            count = search_engine.add_texts_from_list(sample_texts, sample_metadata)
        
        print(f"System ready with {count} documents")
        
        # Interactive mode
        print("\n" + "="*50)
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
                query = input("\nQuestion: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                elif query.lower() == 'help':
                    print("\nAvailable commands:")
                    print("• Ask questions in Thai or English")
                    print("• 'stats' - System statistics")
                    print("• 'quit' - Exit program")
                    continue
                elif query.lower() == 'stats':
                    info = rag.get_pipeline_info()
                    print("\nSystem Statistics:")
                    print(f"• Total documents: {info['search_engine_stats']['total_texts']}")
                    print(f"• Vector dimension: {info['search_engine_stats']['vector_dimension']}")
                    print(f"• LLM client: {info['llm_info']['type'] if info['llm_info'] else 'None'}")
                    continue
                
                if not query:
                    continue
                
                # Process the question
                print("Searching for relevant information...")
                result = rag.answer_question(query)
                
                print("\nAnswer:")
                print("-" * 30)
                print(result["answer"])
                print(f"\nConfidence: {result['confidence']:.2f}")
                print(f"References used: {result['num_context_used']}")
                
                if result["context"]:
                    print("\nReferenced information:")
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
    
    print("\nThank you for using Healthcare-AI!")


if __name__ == "__main__":
    main()
