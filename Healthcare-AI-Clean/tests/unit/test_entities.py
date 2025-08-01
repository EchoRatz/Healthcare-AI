"""Test domain entities."""
import pytest
from datetime import datetime
from src.domain.entities.Question import Question, Answer
from src.domain.entities.ProcessingResult import ProcessingStats, BatchResult
from src.domain.entities.CacheEntry import CacheEntry


class TestQuestion:
    """Test Question entity."""
    
    def test_question_creation(self):
        """Test question creation."""
        choices = {"ก": "Option A", "ข": "Option B"}
        question = Question(id="1", text="Test question?", choices=choices)
        
        assert question.id == "1"
        assert question.text == "Test question?"
        assert question.choices == choices
        assert question.has_choices()
    
    def test_formatted_choices(self):
        """Test formatted choices output."""
        choices = {"ก": "Option A", "ข": "Option B"}
        question = Question(id="1", text="Test?", choices=choices)
        
        formatted = question.get_formatted_choices()
        assert "ก. Option A" in formatted
        assert "ข. Option B" in formatted


class TestAnswer:
    """Test Answer entity."""
    
    def test_answer_creation(self):
        """Test answer creation."""
        answer = Answer(question_id="1", answer="ก", confidence=0.8)
        
        assert answer.question_id == "1"
        assert answer.answer == "ก"
        assert answer.confidence == 0.8
        assert answer.is_multiple_choice()
    
    def test_non_multiple_choice_answer(self):
        """Test non-multiple choice answer."""
        answer = Answer(question_id="1", answer="Some explanation")
        
        assert not answer.is_multiple_choice()


class TestProcessingStats:
    """Test ProcessingStats entity."""
    
    def test_stats_creation(self):
        """Test stats creation."""
        start_time = datetime.now()
        stats = ProcessingStats(
            total_questions=10,
            successful=8,
            errors=2,
            start_time=start_time
        )
        
        assert stats.total_questions == 10
        assert stats.successful == 8
        assert stats.errors == 2
        assert stats.success_rate == 80.0
    
    def test_duration_calculation(self):
        """Test duration calculation."""
        start_time = datetime.now()
        end_time = datetime.now()
        
        stats = ProcessingStats(
            total_questions=1,
            successful=1,
            errors=0,
            start_time=start_time,
            end_time=end_time
        )
        
        assert stats.duration >= 0


class TestCacheEntry:
    """Test CacheEntry entity."""
    
    def test_cache_entry_creation(self):
        """Test cache entry creation."""
        entry = CacheEntry(
            id="test1",
            fact_type="medication",
            key="Aspirin price",
            value="10 baht per tablet",
            relevance_score=8.0
        )
        
        assert entry.id == "test1"
        assert entry.fact_type == "medication"
        assert entry.key == "Aspirin price"
        assert entry.value == "10 baht per tablet"
        assert entry.relevance_score == 8.0
    
    def test_cache_entry_dict_conversion(self):
        """Test dictionary conversion."""
        entry = CacheEntry(
            id="test1",
            fact_type="medication",
            key="Aspirin",
            value="10 baht",
            timestamp=datetime.now()
        )
        
        entry_dict = entry.to_dict()
        reconstructed = CacheEntry.from_dict(entry_dict)
        
        assert reconstructed.id == entry.id
        assert reconstructed.fact_type == entry.fact_type
        assert reconstructed.key == entry.key
        assert reconstructed.value == entry.value