"""Test answer extractor."""
import pytest
from src.core.services.AnswerExtractor import AnswerExtractor


class TestAnswerExtractor:
    """Test AnswerExtractor service."""
    
    def setup_method(self):
        """Setup test method."""
        self.extractor = AnswerExtractor()
    
    def test_extract_single_choice(self):
        """Test extracting single choice."""
        responses = [
            "ตอบ: ก",
            "คำตอบ ข",
            '"ค"',
            "ง",
            "ตอบคือ ก"
        ]
        
        expected = ["ก", "ข", "ค", "ง", "ก"]
        
        for response, expected_answer in zip(responses, expected):
            result = self.extractor.extract_choice_only(response)
            assert result == expected_answer
    
    def test_extract_no_answer(self):
        """Test extracting no answer response."""
        responses = [
            "ไม่มีคำตอบที่ถูกต้อง",
            "ไม่มีข้อใดถูกต้อง",
            "ไม่พบข้อมูล"
        ]
        
        for response in responses:
            result = self.extractor.extract_choice_only(response)
            assert result == "ไม่มีคำตอบที่ถูกต้อง"
    
    def test_validate_answer_format(self):
        """Test answer format validation."""
        valid_answers = ["ก", "ข", "ค", "ง", "ไม่มีคำตอบที่ถูกต้อง"]
        invalid_answers = ["A", "1", "อื่นๆ", ""]
        
        for answer in valid_answers:
            assert self.extractor.validate_answer_format(answer)
        
        for answer in invalid_answers:
            assert not self.extractor.validate_answer_format(answer)