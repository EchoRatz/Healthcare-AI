#!/usr/bin/env python3
"""
Final script to process all 500 questions from test.csv
Output: Clean CSV with only id,answer columns containing choice letters only
"""

from thai_qa_processor import ThaiHealthcareQA
import time

def main():
    """Process complete test.csv with clean choice-letter-only output"""
    print("🎯 FINAL PROCESSING: Complete test.csv Dataset")
    print("=" * 60)
    print("📋 Format: Clean CSV with ONLY id,answer columns")
    print("✅ Answers: ONLY choice letters (ก, ข, ค, ง)")
    print("📝 Questions: All 500 from test.csv") 
    print("🧠 AI: Intelligent caching enabled")
    print("=" * 60)
    
    # Initialize system
    qa_system = ThaiHealthcareQA()
    
    # Show current knowledge
    print(f"\n📚 Current Knowledge Cache:")
    qa_system.show_cache_stats()
    
    print(f"\n🚀 Starting complete dataset processing...")
    print(f"⏱️  Estimated time: 45-90 minutes")
    print(f"💾 Auto-saves progress every 50 questions")
    print(f"🎯 Output: test_answers_final_clean.csv")
    
    start_time = time.time()
    
    try:
        # Process all 500 questions
        qa_system.process_csv_questions(
            csv_file_path='test.csv',
            output_file_path='test_answers_final_clean.csv',
            clean_format=True  # 🎯 Clean CSV: only id,answer columns
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n🎉 COMPLETE SUCCESS!")
        print(f"⏱️  Total processing time: {total_time/60:.1f} minutes")
        print(f"📄 Output file: test_answers_final_clean.csv")
        print(f"📊 Format: Clean CSV with choice letters only")
        
        # Show final knowledge gained
        print(f"\n📚 Final Knowledge Accumulated:")
        qa_system.show_cache_stats()
        
        # Export complete learned knowledge
        qa_system.export_cache_to_text("complete_healthcare_knowledge.txt")
        print(f"💾 Complete knowledge exported to: complete_healthcare_knowledge.txt")
        
        print(f"\n📋 Your files are ready:")
        print(f"   ✅ test_answers_final_clean.csv - Your final answers")
        print(f"   📚 complete_healthcare_knowledge.txt - All learned facts")
        print(f"   💾 knowledge_cache.json - AI knowledge database")
        
    except KeyboardInterrupt:
        print(f"\n⏸️  Processing interrupted by user")
        print(f"💾 Partial results saved in test_answers_final_clean.csv")
        print(f"🔄 You can resume by running this script again")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"💡 Make sure Ollama is running and models are available")

if __name__ == "__main__":
    main()