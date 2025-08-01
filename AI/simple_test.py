"""
Simple test for Thai Healthcare Q&A System with letter-only output
"""

from thai_qa_processor import ThaiHealthcareQA


def main():
    """Test the system with simple output format"""
    
    # Example question
    question = """ผมปวดท้องมาก อ้วกด้วย ตอนนี้ตีสองยังมีแผนกไหนเปิดอยู่ไหมครับ?
ก. Endocrinology
ข. Orthopedics
ค. Emergency
ง. Internal Medicine"""

    print("=== Thai Healthcare Q&A System ===")
    print("Output format: Choice letters only (ก, ข, ค, ง)")
    print()
    
    try:
        # Initialize system
        print("Initializing system...")
        qa_system = ThaiHealthcareQA()
        print("System ready!")
        print()
        
        # Test question
        print("Question:")
        print(question)
        print()
        print("Answer:")
        
        answer = qa_system.answer_question(question)
        print(answer)
        print()
        
        print("Expected format: Single letter (e.g., 'ค') or multiple letters (e.g., 'ก, ค')")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nPlease check:")
        print("1. Ollama is running")
        print("2. Models llama3.2 and mxbai-embed-large are installed")
        print("3. Healthcare data files exist in results_doc/ folders")


if __name__ == "__main__":
    main()