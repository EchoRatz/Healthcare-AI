"""Test configuration."""
import pytest
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def sample_question_data():
    """Sample question data for testing."""
    return {
        'id': '1',
        'question': 'ผมปวดท้องมาก อ้วกด้วย ตอนนี้ตีสองยังมีแผนกไหนเปิดอยู่ไหมครับ?  ก. Endocrinology ข. Orthopedics ค. Emergency ง. Internal Medicine',
        'answer': 'ค'
    }


@pytest.fixture
def sample_questions_csv(tmp_path):
    """Create temporary CSV file for testing."""
    import csv
    
    csv_file = tmp_path / "test_questions.csv"
    
    questions = [
        {'id': '1', 'question': 'Test question 1? ก. A ข. B ค. C ง. D', 'answer': ''},
        {'id': '2', 'question': 'Test question 2? ก. A ข. B ค. C ง. D', 'answer': ''},
    ]
    
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'question', 'answer'])
        writer.writeheader()
        writer.writerows(questions)
    
    return str(csv_file)