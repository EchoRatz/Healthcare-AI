"""Chroma vector database implementation."""
import os
import re
from typing import List, Dict, Any
from langchain_chroma import Chroma
from langchain_core.documents import Document
from ...domain.repositories.DocumentRepository import DocumentRepository


class ChromaDocumentRepository(DocumentRepository):
    """Chroma implementation of document repository."""
    
    def __init__(self, embeddings, db_location: str = "./data/cache/thai_healthcare_db"):
        self.embeddings = embeddings
        self.db_location = db_location
        self.vector_store = None
        self.retriever = None
    
    def load_documents(self) -> List[Dict[str, Any]]:
        """Load healthcare documents from files."""
        documents = []
        
        healthcare_files = [
            "data/results_doc/GPTCleaned_1.txt",
            "data/results_doc/GPTCleaned_2.txt",
            "data/results_doc/GPTCleaned_3.txt",
        ]
        
        for file_path in healthcare_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Split content by pages
                    pages = re.split(r"--- Page \d+ ---", content)
                    
                    for i, page_content in enumerate(pages):
                        if page_content.strip():
                            doc = Document(
                                page_content=page_content.strip(),
                                metadata={
                                    "source": file_path,
                                    "page": i,
                                    "type": "healthcare_guide",
                                },
                            )
                            documents.append(doc)
                
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
        
        return documents
    
    def setup_vector_store(self) -> None:
        """Setup vector database."""
        add_documents = not os.path.exists(self.db_location)
        
        if add_documents:
            print("Creating new vector database...")
            documents = self.load_documents()
            
            if not documents:
                raise ValueError("No healthcare documents found!")
            
            self.vector_store = Chroma(
                collection_name="thai_healthcare",
                persist_directory=self.db_location,
                embedding_function=self.embeddings,
            )
            
            self.vector_store.add_documents(documents=documents)
            print("Documents added to vector database")
        else:
            print("Loading existing vector database...")
            self.vector_store = Chroma(
                collection_name="thai_healthcare",
                persist_directory=self.db_location,
                embedding_function=self.embeddings,
            )
        
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
    
    def search_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search documents by query."""
        if not self.retriever:
            return []
        
        try:
            results = self.retriever.get_relevant_documents(query)
            return [{"content": doc.page_content, "metadata": doc.metadata} for doc in results[:top_k]]
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents to vector store."""
        if self.vector_store and documents:
            self.vector_store.add_documents(documents=documents)
    
    def get_document_count(self) -> int:
        """Get total number of documents."""
        if self.vector_store:
            try:
                return self.vector_store._collection.count()
            except Exception:
                return 0
        return 0