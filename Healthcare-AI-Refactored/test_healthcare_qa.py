#!/usr/bin/env python3
"""
Simple test script to process healthcare Q&A with a few questions.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_healthcare_qa():
    """Test healthcare Q&A processing with a few questions."""
    try:
        print("Testing healthcare Q&A processing...")
        
        from src.scripts.process_healthcare_qa import HealthcareQAProcessor
        
        # Create processor
        processor = HealthcareQAProcessor()
        
        # Test with just 2 questions
        processor.run(
            input_file="src/infrastructure/test.csv",
            output_file="test_output_small.csv",
            batch_size=1,
            max_questions=2
        )
        
        return True
        
    except Exception as e:
        print(f"Error testing healthcare Q&A: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("HEALTHCARE Q&A TEST")
    print("=" * 60)
    
    success = test_healthcare_qa()
    
    print("\n" + "=" * 60)
    print("TEST RESULT")
    print("=" * 60)
    print(f"Healthcare Q&A: {'✅ PASS' if success else '❌ FAIL'}")
    print("=" * 60) 