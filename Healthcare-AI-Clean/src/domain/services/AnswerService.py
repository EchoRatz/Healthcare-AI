"""Answer service interface."""
from abc import ABC, abstractmethod
from ..entities.Question import Question, Answer


class AnswerService(ABC):
    """Interface for answering questions."""
    
    @abstractmethod
    def answer_question(self, question: Question) -> Answer:
        """Answer a single question."""
        pass
    
    @abstractmethod
    def extract_choice_only(self, ai_response: str) -> str:
        """Extract only choice letters from AI response."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if service is available."""
        pass
    
    @abstractmethod
    def get_service_name(self) -> str:
        """Get service name."""
        pass