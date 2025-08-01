"""Use case for setting up vector database."""
from ...domain.repositories.DocumentRepository import DocumentRepository


class SetupVectorDatabase:
    """Use case for database initialization."""
    
    def __init__(self, document_repo: DocumentRepository):
        self.document_repo = document_repo
    
    def execute(self) -> bool:
        """Setup vector database with healthcare documents."""
        try:
            print("🔧 Setting up vector database...")
            
            # Setup vector store
            self.document_repo.setup_vector_store()
            
            # Load and add documents if needed
            documents = self.document_repo.load_documents()
            
            if documents:
                print(f"📚 Loading {len(documents)} documents...")
                self.document_repo.add_documents(documents)
            
            doc_count = self.document_repo.get_document_count()
            print(f"✅ Vector database ready with {doc_count} documents")
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting up database: {e}")
            return False
    
    def test_search(self, query: str = "สิทธิประกัน") -> bool:
        """Test database search functionality."""
        try:
            results = self.document_repo.search_documents(query, top_k=3)
            print(f"🔍 Test search found {len(results)} results")
            return len(results) > 0
            
        except Exception as e:
            print(f"❌ Error testing search: {e}")
            return False