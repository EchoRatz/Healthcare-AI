"""Test question parser."""
import pytest
from src.core.services.QuestionParser import QuestionParser


class TestQuestionParser:
    """Test QuestionParser service."""
    
    def setup_method(self):
        """Setup test method."""
        self.parser = QuestionParser()
    
    def test_single_line_parsing(self):
        """Test single line question parsing."""
        question_text = "ผมปวดท้อง ควรไปแผนกไหน? ก. Emergency ข. Internal Medicine ค. Surgery ง. Cardiology"
        
        question = self.parser.parse_from_text("1", question_text)
        
        assert question.id == "1"
        assert "ผมปวดท้อง ควรไปแผนกไหน?" in question.text
        assert len(question.choices) == 4
        assert question.choices["ก"] == "Emergency"
        assert question.choices["ข"] == "Internal Medicine"
    
    def test_multi_line_parsing(self):
        """Test multi-line question parsing."""
        question_text = """ยาแอสไพรินมีราคาเท่าใด?
ก. 10 บาท
ข. 20 บาท
ค. 30 บาท
ง. 40 บาท"""
        
        question = self.parser.parse_from_text("2", question_text)
        
        assert question.id == "2"
        assert "ยาแอสไพรินมีราคาเท่าใด?" in question.text
        assert len(question.choices) == 4
        assert question.choices["ก"] == "10 บาท"
        assert question.choices["ข"] == "20 บาท"
    
    def test_format_choices_for_prompt(self):
        """Test formatting choices for AI prompt."""
        choices = {"ก": "Option A", "ข": "Option B", "ค": "Option C"}
        
        formatted = self.parser.format_choices_for_prompt(choices)
        
        assert "ก. Option A" in formatted
        assert "ข. Option B" in formatted
        assert "ค. Option C" in formatted