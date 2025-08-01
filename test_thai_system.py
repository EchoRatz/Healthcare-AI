"""
Test script for Thai Healthcare Q&A System
Test with sample questions before running on full dataset
"""

from thai_healthcare_qa_system import ThaiHealthcareQASystem
import os
import csv

def test_question_parsing():
    """Test the question parsing functionality"""
    print("🧪 Testing Question Parsing")
    print("-" * 40)
    
    # Initialize system
    knowledge_files = [
        'Healthcare-AI-Refactored/src/infrastructure/results_doc/direct_extraction_corrected.txt',
        'Healthcare-AI-Refactored/src/infrastructure/results_doc2/direct_extraction_corrected.txt',
        'Healthcare-AI-Refactored/src/infrastructure/results_doc3/direct_extraction_corrected.txt'
    ]
    
    qa_system = ThaiHealthcareQASystem(knowledge_files, memory_file="test_memory.json")
    
    # Test sample questions
    sample_questions = [
        "ผมปวดท้องมาก อ้วกด้วย ตอนนี้ตีสองยังมีแผนกไหนเปิดอยู่ไหมครับ?  ก. Endocrinology ข. Orthopedics ค. Emergency ง. Internal Medicine",
        "ยา Clopidogrel mg tablet ในปี 2567 จ่ายในอัตราเท่าใดต่อเม็ดในกรณีผู้ป่วยนอก (OP)?  ก. 2 บาท/เม็ด ข. 3 บาท/เม็ด ค. 4 บาท/เม็ด ง. 5 บาท/เม็ด"
    ]
    
    for i, full_question in enumerate(sample_questions, 1):
        print(f"\n🔍 Test Question {i}:")
        question, choices = qa_system.parse_question(full_question)
        
        print(f"Question: {question}")
        print("Choices:")
        for choice_label, choice_text in choices.items():
            print(f"  {choice_label}. {choice_text}")
        
        # Test reasoning
        result = qa_system._chain_of_thought_reasoning(question, choices)
        print(f"Predicted Answer: {', '.join(result.predicted_answers)}")
        print(f"Confidence: {result.confidence:.3f}")
        print(f"Evidence found: {len(result.evidence)} pieces")

def test_small_subset():
    """Test with a small subset of the actual test file"""
    print("\n📊 Testing with Small Subset")
    print("-" * 40)
    
    # Check if files exist
    test_file = 'Healthcare-AI-Refactored/src/infrastructure/test.csv'
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return
    
    # Create a small test file with first 5 questions
    small_test_file = 'small_test.csv'
    try:
        with open(test_file, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            header = next(reader)
            
            with open(small_test_file, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.writer(outfile)
                writer.writerow(header)
                
                # Write first 5 questions
                for i, row in enumerate(reader):
                    if i >= 5:
                        break
                    writer.writerow(row)
        
        print(f"Created small test file with 5 questions")
        
        # Initialize system
        knowledge_files = [
            'Healthcare-AI-Refactored/src/infrastructure/results_doc/direct_extraction_corrected.txt',
            'Healthcare-AI-Refactored/src/infrastructure/results_doc2/direct_extraction_corrected.txt',
            'Healthcare-AI-Refactored/src/infrastructure/results_doc3/direct_extraction_corrected.txt'
        ]
        
        qa_system = ThaiHealthcareQASystem(knowledge_files, memory_file="test_memory.json")
        
        # Process small subset
        results = qa_system.process_test_file(small_test_file, 'small_submission.csv')
        
        # Show results
        print(f"\n📈 Small Test Results:")
        print(f"Questions processed: {len(results)}")
        print(f"Average confidence: {sum(r.confidence for r in results) / len(results):.3f}")
        
        print(f"\n🔍 Sample Results:")
        for i, result in enumerate(results[:3], 1):
            print(f"{i}. ID {result.id}: {', '.join(result.predicted_answers)} (conf: {result.confidence:.3f})")
        
        # Check output format
        print(f"\n📄 Checking submission format:")
        if os.path.exists('small_submission.csv'):
            with open('small_submission.csv', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"Header: {lines[0].strip()}")
                for i, line in enumerate(lines[1:4], 1):
                    print(f"Row {i}: {line.strip()}")
        
        # Clean up
        if os.path.exists(small_test_file):
            os.remove(small_test_file)
        
    except Exception as e:
        print(f"❌ Error in subset test: {str(e)}")

def check_system_readiness():
    """Check if system is ready for full processing"""
    print("\n🔧 System Readiness Check")
    print("-" * 40)
    
    # Check required files
    required_files = [
        'Healthcare-AI-Refactored/src/infrastructure/test.csv',
        'Healthcare-AI-Refactored/src/infrastructure/results_doc/direct_extraction_corrected.txt',
        'Healthcare-AI-Refactored/src/infrastructure/results_doc2/direct_extraction_corrected.txt',
        'Healthcare-AI-Refactored/src/infrastructure/results_doc3/direct_extraction_corrected.txt'
    ]
    
    all_files_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path) / 1024  # KB
            print(f"✅ {file_path} ({file_size:.1f} KB)")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            all_files_exist = False
    
    if all_files_exist:
        print(f"\n🎉 System is ready for full processing!")
        print(f"Run: python thai_healthcare_qa_system.py")
    else:
        print(f"\n⚠️ Missing required files. Please check file paths.")

def main():
    """Run all tests"""
    print("🏥 Thai Healthcare Q&A System - Testing Suite")
    print("=" * 50)
    
    try:
        # Test 1: Question parsing
        test_question_parsing()
        
        # Test 2: Small subset processing
        test_small_subset()
        
        # Test 3: System readiness check
        check_system_readiness()
        
        print(f"\n✅ Testing completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()