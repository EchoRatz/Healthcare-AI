"""Document repository implementation."""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any

from core.entities.Document import Document
from shared.logging.LoggerMixin import LoggerMixin


class DocumentRepository(LoggerMixin):
    """Repository for managing documents."""
    
    def __init__(self, storage_path: str = "data/documents"):
        super().__init__()
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def save(self, document: Document) -> bool:
        """Save a document."""
        try:
            file_path = self.storage_path / f"{document.id}.json"
            
            # Convert document to dict
            doc_dict = {
                'id': document.id,
                'content': document.content,
                'metadata': document.metadata,
                'created_at': document.created_at.isoformat() if hasattr(document, 'created_at') and document.created_at else None
            }
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(doc_dict, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Saved document {document.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save document {document.id}: {e}")
            return False
    
    def load(self, document_id: str) -> Optional[Document]:
        """Load a document by ID."""
        try:
            file_path = self.storage_path / f"{document_id}.json"
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                doc_dict = json.load(f)
            
            # Create document from dict
            document = Document(
                content=doc_dict['content'],
                metadata=doc_dict.get('metadata', {}),
                doc_id=doc_dict['id']
            )
            
            return document
            
        except Exception as e:
            self.logger.error(f"Failed to load document {document_id}: {e}")
            return None
    
    def load_all(self) -> List[Document]:
        """Load all documents."""
        documents = []
        
        try:
            for file_path in self.storage_path.glob("*.json"):
                document_id = file_path.stem
                document = self.load(document_id)
                if document:
                    documents.append(document)
            
            self.logger.debug(f"Loaded {len(documents)} documents")
            return documents
            
        except Exception as e:
            self.logger.error(f"Failed to load documents: {e}")
            return []
    
    def delete(self, document_id: str) -> bool:
        """Delete a document."""
        try:
            file_path = self.storage_path / f"{document_id}.json"
            
            if file_path.exists():
                file_path.unlink()
                self.logger.debug(f"Deleted document {document_id}")
                return True
            else:
                self.logger.warning(f"Document {document_id} not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to delete document {document_id}: {e}")
            return False
    
    def exists(self, document_id: str) -> bool:
        """Check if document exists."""
        file_path = self.storage_path / f"{document_id}.json"
        return file_path.exists()
    
    def count(self) -> int:
        """Get total number of documents."""
        try:
            return len(list(self.storage_path.glob("*.json")))
        except Exception as e:
            self.logger.error(f"Failed to count documents: {e}")
            return 0