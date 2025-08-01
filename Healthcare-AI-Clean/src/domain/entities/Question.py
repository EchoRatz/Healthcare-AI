"""Question entity for healthcare Q&A system."""
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Question:
    """Question entity with multiple choice options."""
    id: str
    text: str
    choices: Dict[str, str]
    correct_answer: Optional[str] = None
    
    def get_formatted_choices(self) -> str:
        """Format choices for display."""
        formatted = []
        for letter in ["ก", "ข", "ค", "ง"]:
            if letter in self.choices:
                formatted.append(f"{letter}. {self.choices[letter]}")
        return "\n".join(formatted)
    
    def has_choices(self) -> bool:
        """Check if question has multiple choices."""
        return len(self.choices) > 0


@dataclass
class Answer:
    """Answer entity."""
    question_id: str
    answer: str
    confidence: float = 0.0
    processing_time: float = 0.0
    
    def is_multiple_choice(self) -> bool:
        """Check if answer is a multiple choice letter."""
        return self.answer.strip() in ["ก", "ข", "ค", "ง"]