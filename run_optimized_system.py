#!/usr/bin/env python3
"""
Run Optimized Healthcare Q&A System
===================================

Simple runner script for the optimized system
"""

import os
import sys
import time
from optimized_healthcare_qa_system import OptimizedHealthcareQA

def main():
    """Main runner function"""
    print("🏥 Optimized Healthcare Q&A System")
    print("=" * 50)
    
    # Check if test file exists
    test_file = "AI/test_answers_with_cache.csv"
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        print("Please ensure the test file exists in the AI/ directory")
        return
    
    # Initialize system
    print("🚀 Initializing optimized system...")
    qa_system = OptimizedHealthcareQA()
    
    # Check LLM availability
    if not qa_system.check_llama31():
        print("❌ No Llama 3.1 or Llama 3.2 available")
        print("Please ensure a Llama model is installed and running:")
        print("  1. Start Ollama service: ollama serve")
        print("  2. Pull preferred model: ollama pull llama3.1")
        print("  3. Or pull alternative: ollama pull llama3.2")
        return
    
    print(f"✅ Using model: {qa_system.model_name}")
    
    # Process questions
    print(f"📊 Processing questions from: {test_file}")
    start_time = time.time()
    
    try:
        results = qa_system.process_questions_optimized(test_file)
        
        if results:
            # Save results
            output_file = "optimized_healthcare_submission.csv"
            qa_system.save_results(results, output_file)
            
            # Print summary
            total_time = time.time() - start_time
            single_answers = [r['answer'] for r in results if len(r['answer']) == 1]
            avg_confidence = sum(r['confidence'] for r in results) / len(results)
            
            print(f"\n🎉 Processing complete!")
            print(f"📈 Performance Summary:")
            print(f"  Total questions: {len(results)}")
            print(f"  Processing time: {total_time/60:.1f} minutes")
            print(f"  Questions per second: {len(results)/total_time:.1f}")
            print(f"  Single-choice answers: {len(single_answers)}/{len(results)} ({len(single_answers)/len(results)*100:.1f}%)")
            print(f"  Average confidence: {avg_confidence:.2f}")
            print(f"  Results saved to: {output_file}")
            
            # Show sample results
            print(f"\n📝 Sample Results:")
            for i, result in enumerate(results[:5]):
                print(f"  Q{result['id']}: {result['answer']} (confidence: {result['confidence']:.2f})")
            
            if len(results) > 5:
                print(f"  ... and {len(results) - 5} more questions")
                
        else:
            print("❌ No results generated")
            
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 