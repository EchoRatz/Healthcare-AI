"""Question parsing service."""
import re
from typing import Dict
from ...domain.entities.Question import Question


class QuestionParser:
    """Service to parse question text into structured format."""
    
    def parse_from_text(self, question_id: str, question_text: str) -> Question:
        """Parse question text into Question entity."""
        text = question_text.strip()
        
        if "\n" not in text and any(letter in text for letter in ["ก.", "ข.", "ค.", "ง."]):
            return self._parse_single_line_format(question_id, text)
        else:
            return self._parse_multi_line_format(question_id, text)
    
    def _parse_single_line_format(self, question_id: str, text: str) -> Question:
        """Parse single-line format."""
        choices = {}
        
        # Find all Thai choice patterns
        choice_pattern = r"([ก-ง])\.\s*(.+?)(?=\s+[ก-ง]\.|$)"
        matches = re.findall(choice_pattern, text)
        
        for letter, choice_text in matches:
            choices[letter] = choice_text.strip()
        
        # Extract question part
        first_choice_match = re.search(r"\s+([ก-ง])\.", text)
        if first_choice_match:
            question = text[:first_choice_match.start()].strip()
        else:
            question = text.strip()
        
        return Question(id=question_id, text=question, choices=choices)
    
    def _parse_multi_line_format(self, question_id: str, text: str) -> Question:
        """Parse multi-line format."""
        lines = text.split("\n")
        question_lines = []
        choices = {}
        current_section = "question"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            choice_match = re.match(r"^([ก-ง])[.\s]*(.+)", line)
            if choice_match:
                current_section = "choices"
                choice_letter = choice_match.group(1)
                choice_text = choice_match.group(2)
                choices[choice_letter] = choice_text
            elif current_section == "question":
                question_lines.append(line)
        
        question = " ".join(question_lines)
        return Question(id=question_id, text=question, choices=choices)
    
    def format_choices_for_prompt(self, choices: Dict[str, str]) -> str:
        """Format choices for AI prompt."""
        formatted = []
        for letter in ["ก", "ข", "ค", "ง"]:
            if letter in choices:
                formatted.append(f"{letter}. {choices[letter]}")
        return "\n".join(formatted)