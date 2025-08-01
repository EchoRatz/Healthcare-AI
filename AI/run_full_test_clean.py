#!/usr/bin/env python3
"""
Process the complete test.csv (500 questions) with clean CSV output format
"""

from thai_qa_processor import ThaiHealthcareQA

def main():
    """Process all 500 questions from test.csv with clean output format"""
    print("🚀 Processing Complete test.csv Dataset")
    print("=" * 60)
    print("📋 Output Format: Clean CSV with ONLY id,answer columns")
    print("📝 Questions: All 500 from test.csv")
    print("🧠 Features: Intelligent knowledge caching enabled")
    print("=" * 60)
    
    # Initialize the Thai Healthcare Q&A system
    qa_system = ThaiHealthcareQA()
    
    # Show initial cache
    print("\n📊 Initial Knowledge Cache:")
    qa_system.show_cache_stats()
    
    print("\n🎯 Starting full dataset processing...")
    print("⏱️  This may take 30-60 minutes depending on your system")
    print("💾 Progress will be saved every 50 questions")
    
    try:
        # Process all questions with clean format
        qa_system.process_csv_questions(
            csv_file_path='test.csv',
            output_file_path='test_answers_final.csv',
            clean_format=True  # 🎯 This generates ONLY id,answer columns
        )
        
        print("\n🎉 SUCCESS! Full dataset processed!")
        print("📄 Output file: test_answers_final.csv")
        print("📊 Format: Clean CSV with id,answer columns only")
        
        # Show final knowledge gained
        print("\n📚 Final Knowledge Cache:")
        qa_system.show_cache_stats()
        
        # Export all learned knowledge
        qa_system.export_cache_to_text("complete_learned_knowledge.txt")
        print("💾 Complete learned knowledge saved to: complete_learned_knowledge.txt")
        
    except KeyboardInterrupt:
        print("\n⏸️  Processing interrupted by user")
        print("💾 Partial results should be saved in test_answers_final.csv")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure Ollama is running and models are available")

if __name__ == "__main__":
    main()