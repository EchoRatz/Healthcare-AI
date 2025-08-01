"""CSV-based question repository implementation."""
import csv
import os
from typing import List
from ...domain.entities.Question import Question
from ...domain.repositories.QuestionRepository import QuestionRepository
from ...core.services.QuestionParser import QuestionParser


class CsvQuestionRepository(QuestionRepository):
    """CSV implementation of question repository."""
    
    def __init__(self):
        self.parser = QuestionParser()
    
    def load_from_csv(self, file_path: str) -> List[Question]:
        """Load questions from CSV file."""
        questions = []
        
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                question = self.parser.parse_from_text(row['id'], row['question'])
                questions.append(question)
        
        return questions
    
    def save_answers_to_csv(self, results: List[dict], output_path: str, clean_format: bool = False) -> None:
        """Save answers to CSV file."""
        with open(output_path, 'w', encoding='utf-8', newline='') as file:
            if clean_format:
                fieldnames = ["id", "answer"]
                clean_results = [{"id": r["id"], "answer": r["answer"]} for r in results]
            else:
                fieldnames = ["id", "question", "answer"]
                clean_results = results
            
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(clean_results)
    
    def validate_csv_format(self, file_path: str) -> tuple[bool, str]:
        """Validate CSV file format."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                if 'id' not in reader.fieldnames or 'question' not in reader.fieldnames:
                    return False, "CSV must have 'id' and 'question' columns"
                
                # Check first row
                first_row = next(reader, None)
                if not first_row or not first_row['id'] or not first_row['question']:
                    return False, "Empty id or question in first row"
                
                return True, "Valid CSV format"
                
        except Exception as e:
            return False, f"Error reading CSV: {str(e)}"
    
    def get_question_count(self, file_path: str) -> int:
        """Get total number of questions in file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                return sum(1 for _ in reader)
        except Exception:
            return 0
    
    def preview_questions(self, file_path: str, count: int = 3) -> List[Question]:
        """Preview first few questions from file."""
        questions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for i, row in enumerate(reader):
                    if i >= count:
                        break
                    question = self.parser.parse_from_text(row['id'], row['question'])
                    questions.append(question)
        except Exception:
            pass
        
        return questions
    
    def _parse_csv_row(self, row: dict) -> Question:
        """Parse CSV row into Question entity."""
        from core.services.QuestionParser import QuestionParser
        parser = QuestionParser()
        return parser.parse_from_text(row['id'], row['question'])