"""Database setup entry point."""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from infrastructure.services.OllamaEmbeddings import OllamaEmbeddingService
from infrastructure.repositories.ChromaDocumentRepository import ChromaDocumentRepository
from infrastructure.config.Settings import settings
from core.use_cases.SetupVectorDatabase import SetupVectorDatabase


def main():
    """Setup vector database with healthcare documents."""
    print("🔧 Healthcare AI - Database Setup")
    print("=" * 50)
    
    try:
        # Initialize embedding service
        print("🚀 Initializing embedding service...")
        embedding_service = OllamaEmbeddingService(settings.ollama_embedding_model)
        
        if not embedding_service.is_available():
            print("❌ Ollama embedding service not available")
            print("💡 Make sure Ollama is running and models are installed:")
            print(f"   ollama pull {settings.ollama_embedding_model}")
            return
        
        print("✅ Embedding service ready")
        
        # Initialize document repository
        print("📚 Setting up document repository...")
        embeddings_instance = embedding_service.get_embeddings_instance()
        document_repo = ChromaDocumentRepository(embeddings_instance, settings.vector_db_path)
        
        # Setup database
        setup_use_case = SetupVectorDatabase(document_repo)
        
        if setup_use_case.execute():
            print("🎉 Database setup completed successfully!")
            
            # Test search
            if setup_use_case.test_search():
                print("✅ Database search test passed")
            else:
                print("⚠️  Database search test failed")
        else:
            print("❌ Database setup failed")
    
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        print("💡 Troubleshooting:")
        print("   1. Make sure Ollama is running")
        print("   2. Install required models: ollama pull llama3.2 && ollama pull mxbai-embed-large")
        print("   3. Check if healthcare documents exist in data/results_doc/")


if __name__ == "__main__":
    main()