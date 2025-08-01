"""Main entry point for Healthcare AI."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.config.Config import AppConfig
from shared.logging.LoggerMixin import get_logger
from infrastructure.database.FAISSVectorStore import FAISSVectorStore
from infrastructure.database.Repository.DocumentRepository import DocumentRepository
from infrastructure.database.DataSourceManager import DataSourceManager
from infrastructure.llm.OllamaClient import OllamaClient
from core.use_cases.SearchDocuments import SearchDocuments
from core.use_cases.ProcessQuestion import ProcessQuestion
from presentation.cli.MainCLI import MainCLI


def main():
    """Main entry point."""
    print("🏥 Healthcare-AI System")
    print("=" * 50)
    
    try:
        # Load configuration
        config = AppConfig.from_file("config/app.json")
        logger = get_logger(__name__, config.log_level)
        
        logger.info("Starting Healthcare-AI system")
        
        # Initialize infrastructure
        vector_store = FAISSVectorStore(
            dimension=config.database.vector_dimension,
            index_type=config.database.index_type
        )
        
        document_repo = DocumentRepository(config.database.storage_path)
        
        # Initialize data source manager
        data_source_manager = DataSourceManager()
        
        # Load and index data sources
        print("📚 Loading data sources...")
        documents = data_source_manager.load_all_sources()
        
        if documents:
            # For now, create simple vectors (placeholder)
            # In a real implementation, you'd use an embedding model
            vectors = [[0.1] * config.database.vector_dimension for _ in documents]
            
            vector_store.add_documents(documents, vectors)
            
            for document in documents:
                document_repo.save(document)
                print(f"  ✅ Indexed: {document.id} ({len(document.content):,} chars)")
        else:
            print("  ⚠️  No documents loaded")
        
        llm_client = OllamaClient(
            base_url=config.llm.base_url,
            model_name=config.llm.model_name
        )
        
        # Check LLM availability
        if not llm_client.is_available():
            print("⚠️  Warning: Ollama service not available")
            print("Please start Ollama service: ollama serve")
        
        # Initialize use cases
        search_documents = SearchDocuments(vector_store, None)  # TODO: Add text processor
        process_question = ProcessQuestion(llm_client, search_documents)
        
        # Start CLI
        cli = MainCLI(process_question, config)
        cli.run()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"System error: {e}")
        print(f"❌ System error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()