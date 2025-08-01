#!/usr/bin/env python3
"""
Quick test to demonstrate clean CSV format output (id,answer only)
"""

from thai_qa_processor import ThaiHealthcareQA

def test_clean_format():
    """Test with clean CSV output format"""
    print("🧪 Testing Clean CSV Format Output")
    print("=" * 50)
    print("This will generate CSV with ONLY id,answer columns")
    print("(matching the format shown in your image)")
    print("=" * 50)
    
    # Initialize the system
    qa_system = ThaiHealthcareQA()
    
    # Process first 10 questions with clean format
    print("\n🚀 Processing first 10 questions from test.csv...")
    
    # Read first 10 questions only for demo
    import csv
    with open('test.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        first_10 = []
        for i, row in enumerate(reader):
            if i >= 10:  # Only first 10
                break
            first_10.append(row)
    
    # Write to temp file
    with open('temp_10_questions.csv', 'w', encoding='utf-8', newline='') as file:
        fieldnames = ['id', 'question', 'answer']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(first_10)
    
    # Process with clean format
    qa_system.process_csv_questions(
        'temp_10_questions.csv', 
        'test_answers_clean_format.csv',
        clean_format=True  # This generates ONLY id,answer columns
    )
    
    print("\n✅ Complete! Check the output files:")
    print("📄 test_answers_clean_format.csv - Clean format (id,answer only)")
    
    # Clean up temp file
    import os
    if os.path.exists('temp_10_questions.csv'):
        os.remove('temp_10_questions.csv')

if __name__ == "__main__":
    test_clean_format()