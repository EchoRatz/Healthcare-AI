"""FAISS-based vector store implementation."""

import pickle
from pathlib import Path
from typing import List, Optional, Tuple
import numpy as np
import faiss

from core.interfaces.VectorStoreInterface import VectorStoreInterface
from core.entities.Document import Document
from shared.logging.LoggerMixin import LoggerMixin


class FAISSVectorStore(VectorStoreInterface, LoggerMixin):
    """FAISS-based vector store implementation."""
    
    def __init__(self, dimension: int = 384, index_type: str = "IndexFlatL2"):
        super().__init__()
        self.dimension = dimension
        self.index_type = index_type
        self.index = None
        self.documents = {}
        self.vector_to_doc_id = {}
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize FAISS index."""
        try:
            if self.index_type == "IndexFlatL2":
                self.index = faiss.IndexFlatL2(self.dimension)
            elif self.index_type == "IndexIVFFlat":
                quantizer = faiss.IndexFlatL2(self.dimension)
                self.index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
            else:
                self.index = faiss.IndexFlatL2(self.dimension)
            
            self.logger.debug(f"Initialized FAISS index: {self.index_type}")
        except Exception as e:
            self.logger.error(f"Failed to initialize FAISS index: {e}")
            raise
    
    def add_documents(self, documents: List[Document], vectors: List[List[float]]) -> bool:
        """Add documents with their vectors."""
        try:
            if len(documents) != len(vectors):
                raise ValueError("Number of documents must match number of vectors")
            
            # Convert vectors to numpy array
            vector_array = np.array(vectors, dtype=np.float32)
            
            # Add vectors to index
            start_id = self.index.ntotal
            self.index.add(vector_array)
            
            # Store document mappings
            for i, document in enumerate(documents):
                vector_id = start_id + i
                self.documents[document.id] = document
                self.vector_to_doc_id[vector_id] = document.id
            
            self.logger.debug(f"Added {len(documents)} documents to vector store")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add documents: {e}")
            return False
    
    def search(self, query_vector: List[float], top_k: int = 5) -> List[Tuple[Document, float]]:
        """Search for similar documents."""
        try:
            if self.index.ntotal == 0:
                return []
            
            # Convert query to numpy array
            query_array = np.array([query_vector], dtype=np.float32)
            
            # Search
            distances, indices = self.index.search(query_array, top_k)
            
            # Convert results
            results = []
            for i, (distance, index) in enumerate(zip(distances[0], indices[0])):
                if index == -1:  # No more results
                    break
                
                doc_id = self.vector_to_doc_id.get(index)
                if doc_id and doc_id in self.documents:
                    document = self.documents[doc_id]
                    results.append((document, float(distance)))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []
    
    # Required abstract methods from VectorStoreInterface
    def add_vectors(self, vectors: List[List[float]], metadata: List[dict] = None) -> bool:
        """Add vectors to the store."""
        try:
            if metadata is None:
                metadata = [{}] * len(vectors)
            
            # Create dummy documents from metadata
            documents = []
            for i, meta in enumerate(metadata):
                doc = Document(
                    content=meta.get('content', f'Document {i}'),
                    metadata=meta,
                    doc_id=meta.get('id', f'doc_{len(self.documents)}_{i}')
                )
                documents.append(doc)
            
            return self.add_documents(documents, vectors)
            
        except Exception as e:
            self.logger.error(f"Failed to add vectors: {e}")
            return False
    
    def search_vectors(self, query_vector: List[float], top_k: int = 5) -> List[Tuple[List[float], float, dict]]:
        """Search for similar vectors."""
        try:
            if self.index.ntotal == 0:
                return []
            
            # Convert query to numpy array
            query_array = np.array([query_vector], dtype=np.float32)
            
            # Search
            distances, indices = self.index.search(query_array, top_k)
            
            # Convert results
            results = []
            for i, (distance, index) in enumerate(zip(distances[0], indices[0])):
                if index == -1:  # No more results
                    break
                
                doc_id = self.vector_to_doc_id.get(index)
                if doc_id and doc_id in self.documents:
                    document = self.documents[doc_id]
                    # Return the vector (reconstruct or store separately), distance, and metadata
                    results.append((query_vector, float(distance), document.metadata))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Vector search failed: {e}")
            return []
    
    def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector by ID."""
        return self.delete_document(vector_id)
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document from the store."""
        try:
            if document_id not in self.documents:
                return False
            
            # Remove from documents
            del self.documents[document_id]
            
            # Remove from vector mapping
            vector_ids_to_remove = [vid for vid, doc_id in self.vector_to_doc_id.items() if doc_id == document_id]
            for vid in vector_ids_to_remove:
                del self.vector_to_doc_id[vid]
            
            self.logger.debug(f"Deleted document {document_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete document {document_id}: {e}")
            return False
    
    def save(self, path: str) -> bool:
        """Save index to disk."""
        return self.save_to_disk(path)
    
    def load(self, path: str) -> bool:
        """Load index from disk."""
        return self.load_from_disk(path)
    
    def size(self) -> int:
        """Get the number of vectors in the store."""
        return len(self.documents)
    
    def save_to_disk(self, path: str) -> bool:
        """Save index to disk."""
        try:
            path_obj = Path(path)
            path_obj.mkdir(parents=True, exist_ok=True)
            
            # Save FAISS index
            index_path = path_obj / "faiss.index"
            faiss.write_index(self.index, str(index_path))
            
            # Save metadata
            metadata = {
                'documents': {doc_id: {
                    'id': doc.id,
                    'content': doc.content,
                    'metadata': doc.metadata
                } for doc_id, doc in self.documents.items()},
                'vector_to_doc_id': self.vector_to_doc_id,
                'dimension': self.dimension,
                'index_type': self.index_type
            }
            
            metadata_path = path_obj / "metadata.pkl"
            with open(metadata_path, 'wb') as f:
                pickle.dump(metadata, f)
            
            self.logger.debug(f"Saved vector store to {path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save to disk: {e}")
            return False
    
    def load_from_disk(self, path: str) -> bool:
        """Load index from disk."""
        try:
            path_obj = Path(path)
            
            if not path_obj.exists():
                return False
            
            # Load FAISS index
            index_path = path_obj / "faiss.index"
            if index_path.exists():
                self.index = faiss.read_index(str(index_path))
            
            # Load metadata
            metadata_path = path_obj / "metadata.pkl"
            if metadata_path.exists():
                with open(metadata_path, 'rb') as f:
                    metadata = pickle.load(f)
                
                # Restore documents
                self.documents = {}
                for doc_id, doc_data in metadata['documents'].items():
                    document = Document(
                        content=doc_data['content'],
                        metadata=doc_data['metadata'],
                        doc_id=doc_data['id']
                    )
                    self.documents[doc_id] = document
                
                self.vector_to_doc_id = metadata['vector_to_doc_id']
                self.dimension = metadata['dimension']
                self.index_type = metadata['index_type']
            
            self.logger.debug(f"Loaded vector store from {path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load from disk: {e}")
            return False
    
    def get_document_count(self) -> int:
        """Get total number of documents."""
        return len(self.documents)
    
    def clear(self) -> bool:
        """Clear all documents and vectors."""
        try:
            self.documents.clear()
            self.vector_to_doc_id.clear()
            self._initialize_index()
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear vector store: {e}")
            return False