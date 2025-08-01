#!/usr/bin/env python3
"""
Quick demonstration of the ChainLang Q&A System
Run this to see the system in action with sample data
"""

import os
import sys
from chainlang_qa_system import ChainLangQASystem

def check_requirements():
    """Check if all required files exist"""
    required_files = [
        'questions.csv',
        'file1.txt',
        'file2.txt', 
        'file3.txt'
    ]
    
    missing = [f for f in required_files if not os.path.exists(f)]
    if missing:
        print(f"❌ Missing required files: {missing}")
        print("Please run this script from the directory containing all sample files.")
        return False
    return True

def demo_individual_questions():
    """Demonstrate answering individual questions"""
    print("🔗 ChainLang Q&A System Demo")
    print("=" * 50)
    
    # Initialize the system
    print("🏗️  Initializing system...")
    knowledge_files = ['file1.txt', 'file2.txt', 'file3.txt']
    qa_system = ChainLangQASystem(knowledge_files, memory_file="demo_memory.json")
    
    # Demo questions that should show different response types
    demo_questions = [
        "What is machine learning?",              # Should find in docs
        "How does supervised learning work?",     # Should find in docs
        "What is quantum computing?",             # Should not be found
        "What is the difference between AI and ML?", # Should find in docs
    ]
    
    print(f"\n🤖 Processing {len(demo_questions)} demo questions:")
    print("-" * 50)
    
    results = []
    for i, question in enumerate(demo_questions, 1):
        print(f"\n🔍 Question {i}: {question}")
        
        result = qa_system.answer_question(question)
        results.append(result)
        
        print(f"📝 Answer: {result.answer}")
        print(f"📊 Source: {result.source} | Confidence: {result.confidence:.1f}")
        
        # Show reasoning steps
        if len(result.reasoning_chain) > 0:
            print(f"🧠 Reasoning: {result.reasoning_chain[-1]}")  # Last reasoning step
    
    return qa_system, results

def demo_memory_learning():
    """Demonstrate the memory learning capability"""
    print(f"\n🧠 Memory Learning Demonstration")
    print("-" * 50)
    
    # Initialize system (will load previous memory if exists)
    knowledge_files = ['file1.txt', 'file2.txt', 'file3.txt'] 
    qa_system = ChainLangQASystem(knowledge_files, memory_file="demo_memory.json")
    
    # Ask a similar question to one we might have answered before
    similar_questions = [
        "What exactly is machine learning?",      # Similar to previous
        "Can you explain machine learning?",     # Another similar one  
        "Define machine learning for me",        # Another variation
    ]
    
    print("Asking similar questions to test memory retrieval:")
    
    for question in similar_questions:
        print(f"\n🔄 Question: {question}")
        result = qa_system.answer_question(question)
        print(f"📝 Answer: {result.answer[:100]}...")
        print(f"📊 Source: {result.source} | Confidence: {result.confidence:.1f}")
        
        if result.source == "memory":
            print("✅ System used memory from previous similar question!")

def demo_csv_processing():
    """Demonstrate full CSV processing"""
    print(f"\n📊 CSV Processing Demonstration")
    print("-" * 50)
    
    knowledge_files = ['file1.txt', 'file2.txt', 'file3.txt']
    qa_system = ChainLangQASystem(knowledge_files, memory_file="demo_memory.json")
    
    print("Processing questions from questions.csv...")
    results = qa_system.process_csv_questions('questions.csv', 'demo_answers.csv')
    
    # Show summary
    doc_answers = sum(1 for r in results if r.source == 'docs')
    memory_answers = sum(1 for r in results if r.source == 'memory') 
    not_found = sum(1 for r in results if r.source == 'not_found')
    avg_confidence = sum(r.confidence for r in results) / len(results)
    
    print(f"\n📈 Processing Complete!")
    print(f"   Total Questions: {len(results)}")
    print(f"   From Documents: {doc_answers}")
    print(f"   From Memory: {memory_answers}")
    print(f"   Not Found: {not_found}")
    print(f"   Avg Confidence: {avg_confidence:.2f}")
    print(f"   Results saved to: demo_answers.csv")
    print(f"   Memory saved to: demo_memory.json")

def main():
    """Run the complete demonstration"""
    if not check_requirements():
        sys.exit(1)
    
    try:
        # Part 1: Individual questions
        qa_system, results = demo_individual_questions()
        
        # Part 2: Memory learning  
        demo_memory_learning()
        
        # Part 3: CSV processing
        demo_csv_processing()
        
        print(f"\n🎉 Demo Complete!")
        print("Files generated:")
        print("  - demo_answers.csv (full results)")
        print("  - demo_memory.json (persistent memory)")
        print("\nTry running the demo again to see how memory improves responses!")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()