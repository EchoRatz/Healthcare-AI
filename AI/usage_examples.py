#!/usr/bin/env python3
"""
Usage Examples for Thai Healthcare Q&A System
Shows how to use both single questions and batch processing
"""

# NOTE: Make sure to install dependencies first:
# pip install langchain-ollama langchain-chroma langchain-core

from thai_qa_processor import ThaiHealthcareQA


def example_single_question():
    """Example: Answer a single question"""
    
    print("🔍 Example: Single Question")
    print("=" * 50)
    
    question = """ผมปวดท้องมาก อ้วกด้วย ตอนนี้ตีสองยังมีแผนกไหนเปิดอยู่ไหมครับ?
ก. Endocrinology
ข. Orthopedics  
ค. Emergency
ง. Internal Medicine"""

    try:
        qa_system = ThaiHealthcareQA()
        answer = qa_system.answer_question(question)
        print(f"Question: {question.split('?')[0]}?")
        print(f"Answer: {answer}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure Ollama is running and models are installed")


def example_batch_processing():
    """Example: Batch process CSV file"""
    
    print("\n📊 Example: Batch Processing")
    print("=" * 50)
    
    try:
        qa_system = ThaiHealthcareQA()
        
        # Process all questions from test.csv
        print("Processing all questions from test.csv...")
        qa_system.process_csv_questions("test.csv", "my_answers.csv")
        
        print("✅ Complete! Results saved to my_answers.csv")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure:")
        print("- Ollama is running")
        print("- Models are installed (llama3.2, mxbai-embed-large)")  
        print("- test.csv file exists")


def example_batch_with_custom_settings():
    """Example: Batch processing with custom settings"""
    
    print("\n⚙️  Example: Custom Batch Processing")
    print("=" * 50)
    
    try:
        qa_system = ThaiHealthcareQA()
        
        # Process with smaller batches for better monitoring
        print("Processing with batch size 5...")
        qa_system.process_csv_batch(
            csv_file_path="test.csv",
            batch_size=5,
            output_file_path="custom_answers.csv"
        )
        
        print("✅ Complete with detailed batch tracking!")
        
    except Exception as e:
        print(f"Error: {e}")


def show_file_formats():
    """Show expected CSV file formats"""
    
    print("\n📄 CSV File Formats")
    print("=" * 50)
    
    print("Input CSV format:")
    print("id,question,answer")
    print("1,ผมปวดท้อง? ก. A ข. B ค. C ง. D,")
    print("2,ยาอะไร? ก. X ข. Y ค. Z ง. W,")
    
    print("\nOutput CSV format:")
    print("id,question,answer")
    print("1,ผมปวดท้อง? ก. A ข. B ค. C ง. D,ค")
    print("2,ยาอะไร? ก. X ข. Y ค. Z ง. W,ข")
    
    print("\nAnswer format: Only choice letters (ก, ข, ค, ง)")


def main():
    """Run all examples"""
    
    print("🎯 Thai Healthcare Q&A System - Usage Examples")
    print("=" * 60)
    
    # Show file formats first
    show_file_formats()
    
    # Single question example
    example_single_question()
    
    # Batch processing examples
    example_batch_processing()
    example_batch_with_custom_settings()
    
    print("\n" + "=" * 60)
    print("📚 For more information, see README_THAI_QA.md")
    print("🚀 To process your test.csv: python batch_test_processor.py")


if __name__ == "__main__":
    main()