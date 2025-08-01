"""Question repository interface."""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.Question import Question


class QuestionRepository(ABC):
    """Interface for question data access."""
    
    @abstractmethod
    def load_from_csv(self, file_path: str) -> List[Question]:
        """Load questions from CSV file."""
        pass
    
    @abstractmethod
    def save_answers_to_csv(self, results: List[dict], output_path: str, clean_format: bool = False) -> None:
        """Save answers to CSV file."""
        pass
    
    @abstractmethod
    def validate_csv_format(self, file_path: str) -> tuple[bool, str]:
        """Validate CSV file format."""
        pass
    
    @abstractmethod
    def get_question_count(self, file_path: str) -> int:
        """Get total number of questions in file."""
        pass
    
    @abstractmethod
    def preview_questions(self, file_path: str, count: int = 3) -> List[Question]:
        """Preview first few questions from file."""
        pass