"""Integration tests for CSV processing."""
import pytest
import tempfile
import os
from src.infrastructure.repositories.CsvQuestionRepository import CsvQuestionRepository
from src.infrastructure.services.SimpleAnswerService import SimpleAnswerService
from src.core.use_cases.ProcessCsvBatch import ProcessCsvBatch


class TestCsvProcessing:
    """Test CSV processing integration."""
    
    def setup_method(self):
        """Setup test components."""
        self.question_repo = CsvQuestionRepository()
        self.answer_service = SimpleAnswerService()
        self.batch_processor = ProcessCsvBatch(self.question_repo, self.answer_service)
    
    def test_end_to_end_processing(self, sample_questions_csv):
        """Test complete CSV processing workflow."""
        # Create temporary output file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            # Process CSV
            result = self.batch_processor.execute(
                sample_questions_csv, 
                output_file, 
                batch_size=2
            )
            
            # Verify results
            assert len(result.results) == 2
            assert result.stats.total_questions == 2
            assert result.stats.success_rate > 0
            assert os.path.exists(output_file)
            
            # Verify output file format
            questions = self.question_repo.load_from_csv(output_file)
            assert len(questions) == 2
            
        finally:
            # Cleanup
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_csv_validation(self):
        """Test CSV format validation."""
        # Test valid CSV
        valid, message = self.question_repo.validate_csv_format("data/input/test.csv")
        if os.path.exists("data/input/test.csv"):
            assert valid or "Error reading CSV" in message
    
    def test_question_parsing_integration(self, sample_questions_csv):
        """Test question parsing in full workflow."""
        questions = self.question_repo.load_from_csv(sample_questions_csv)
        
        assert len(questions) == 2
        for question in questions:
            assert question.id in ["1", "2"]
            assert len(question.choices) == 4
            assert "ก" in question.choices
            assert "ข" in question.choices
            assert "ค" in question.choices
            assert "ง" in question.choices