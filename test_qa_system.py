"""
Test script for the ChainLang Q&A System
"""

from chainlang_qa_system import ChainLangQASystem
import os

def test_individual_questions():
    """Test the system with individual questions"""
    print("🧪 Testing ChainLang Q&A System")
    print("=" * 40)
    
    # Initialize system
    knowledge_files = ['file1.txt', 'file2.txt', 'file3.txt']
    qa_system = ChainLangQASystem(knowledge_files)
    
    # Test questions
    test_questions = [
        "What is machine learning?",
        "How does reinforcement learning work?", 
        "What are the benefits of blockchain?",  # This should not be found
        "What is the difference between AI and ML?"
    ]
    
    print(f"\nTesting {len(test_questions)} individual questions:\n")
    
    for i, question in enumerate(test_questions, 1):
        print(f"Question {i}: {question}")
        result = qa_system.answer_question(question)
        print(f"Answer: {result.answer}")
        print(f"Source: {result.source} (Confidence: {result.confidence:.2f})")
        print(f"Reasoning Chain: {len(result.reasoning_chain)} steps")
        print("-" * 60)
    
    # Test memory functionality
    print("\n🧠 Testing Memory Functionality:")
    print("Asking a similar question to test memory retrieval...")
    
    similar_question = "What exactly is machine learning?"
    result = qa_system.answer_question(similar_question)
    print(f"Question: {similar_question}")
    print(f"Answer: {result.answer}")
    print(f"Source: {result.source}")
    
    return qa_system

def test_csv_processing():
    """Test processing questions from CSV file"""
    print("\n📊 Testing CSV Processing:")
    print("=" * 40)
    
    # Check if files exist
    required_files = ['questions.csv', 'file1.txt', 'file2.txt', 'file3.txt']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        print("Please ensure all required files are present.")
        return
    
    # Initialize system
    knowledge_files = ['file1.txt', 'file2.txt', 'file3.txt']
    qa_system = ChainLangQASystem(knowledge_files)
    
    # Process CSV
    results = qa_system.process_csv_questions('questions.csv', 'test_answers.csv')
    
    # Print summary
    print(f"\n📈 Test Results Summary:")
    print(f"Total questions: {len(results)}")
    print(f"Found in documents: {sum(1 for r in results if r.source == 'docs')}")
    print(f"Found in memory: {sum(1 for r in results if r.source == 'memory')}")
    print(f"Not found: {sum(1 for r in results if r.source == 'not_found')}")
    
    # Show some examples
    print(f"\n🔍 Example Results:")
    for i, result in enumerate(results[:3]):  # Show first 3
        print(f"{i+1}. Q: {result.question[:50]}...")
        print(f"   A: {result.answer[:100]}...")
        print(f"   Source: {result.source}")

if __name__ == "__main__":
    # Run individual tests first
    qa_system = test_individual_questions()
    
    # Then test CSV processing
    test_csv_processing()
    
    print("\n✅ Testing completed! Check 'test_answers.csv' for full results.")
    print("Check 'qa_memory.json' to see the accumulated Q&A memory.")