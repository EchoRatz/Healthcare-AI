import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class SearchResult:
    text: str
    distance: float
    relevance_score: float


class ThaiTextVectorDatabase:

    def __init__(self, vector_dim: int = 384):
        self.vector_dim = vector_dim
        self.index = faiss.IndexFlatL2(vector_dim)
        self.vectors = []
        self.metadata = []
        # Use multilingual model that supports Thai
        self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        print(f"Initialized vector database with dimension {vector_dim}")

    def add_text(self, text: str, metadata: Optional[str] = None) -> None:
        if not text.strip():
            return

        vector = self.model.encode(text, convert_to_numpy=True)
        self.index.add(np.array([vector], dtype=np.float32))
        self.vectors.append(vector)
        self.metadata.append(metadata or text)

    def add_texts_from_file(self, filepath: str, encoding: str = "utf-8") -> int:
        count = 0
        try:
            with open(filepath, "r", encoding=encoding) as file:
                for line in file:
                    line = line.strip()
                    if line:
                        self.add_text(line)
                        count += 1
            print(f"Added {count} texts from {filepath}")
        except FileNotFoundError:
            print(f"Error: File {filepath} not found")
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")

        return count

    def search(
        self, query_text: str, k: int = 5, distance_threshold: float = 2.0
    ) -> List[SearchResult]:
        if self.size() == 0:
            return []

        query_vector = self.model.encode(query_text, convert_to_numpy=True)
        query_vector = np.array([query_vector], dtype=np.float32)
        distances, indices = self.index.search(query_vector, min(k, self.size()))

        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and distances[0][i] <= distance_threshold:
                # Convert distance to relevance score
                relevance_score = max(0, 1 - (distances[0][i] / distance_threshold))
                results.append(
                    SearchResult(
                        text=self.metadata[idx],
                        distance=float(distances[0][i]),
                        relevance_score=float(relevance_score),
                    )
                )

        return results

    def size(self) -> int:
        return len(self.vectors)

    def save(
        self,
        index_file: str = "vector_index.faiss",
        metadata_file: str = "metadata.json",
    ) -> None:
        try:
            faiss.write_index(self.index, index_file)
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            print(f"Database saved to {index_file} and {metadata_file}")
        except Exception as e:
            print(f"Error saving database: {e}")

    def load(
        self,
        index_file: str = "vector_index.faiss",
        metadata_file: str = "metadata.json",
    ) -> bool:
        try:
            self.index = faiss.read_index(index_file)
            with open(metadata_file, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
            print(f"Database loaded from {index_file} and {metadata_file}")
            print(f"Loaded {self.size()} entries")
            return True
        except FileNotFoundError:
            print(f"Database files not found. Will create new database.")
            return False
        except Exception as e:
            print(f"Error loading database: {e}")
            return False

    def get_stats(self) -> dict:
        return {
            "total_entries": self.size(),
            "vector_dimension": self.vector_dim,
            "index_type": "L2 (Euclidean distance)",
        }
