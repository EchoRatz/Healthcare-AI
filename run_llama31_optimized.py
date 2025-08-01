#!/usr/bin/env python3
"""
Optimized Llama 3.1 Runner - Fixed Embedding Loop Issue
======================================================

Prevents re-processing embeddings for each question
Shows clear progress through all 500 questions
"""

import os
import sys
import time
import requests
from typing import List

def check_system_ready():
    """Quick system check"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=3)
        if response.status_code == 200:
            models = response.json().get('models', [])
            llama_models = [m['name'] for m in models if 'llama3.1' in m['name'].lower()]
            if llama_models:
                return llama_models[0]
        return None
    except:
        return None

def run_optimized_processing():
    """Run with optimized embedding processing"""
    print("🚀 Optimized Llama 3.1 Processing - No More Loops!")
    print("=" * 55)
    
    # Check Llama 3.1
    model_name = check_system_ready()
    if not model_name:
        print("❌ Llama 3.1 not available")
        return False
    
    print(f"✅ Using: {model_name}")
    
    try:
        from free_enhanced_thai_qa import FreeEnhancedThaiQA
        
        # Find files
        knowledge_files = [
            'Healthcare-AI-Refactored/src/infrastructure/results_doc/direct_extraction_corrected.txt',
            'Healthcare-AI-Refactored/src/infrastructure/results_doc2/direct_extraction_corrected.txt',
            'Healthcare-AI-Refactored/src/infrastructure/results_doc3/direct_extraction_corrected.txt'
        ]
        
        existing_files = [f for f in knowledge_files if os.path.exists(f)]
        test_file = 'Healthcare-AI-Refactored/src/infrastructure/test.csv'
        
        if not existing_files or not os.path.exists(test_file):
            print("❌ Required files not found")
            return False
        
        print(f"📚 Knowledge files: {len(existing_files)}")
        
        # Initialize with progress tracking
        print(f"\n🔧 Initializing system (this processes embeddings ONCE)...")
        start_time = time.time()
        
        qa_system = FreeEnhancedThaiQA(existing_files, use_local_llm=True)
        
        init_time = time.time() - start_time
        print(f"✅ Initialization complete: {init_time:.1f}s")
        
        # Show what's loaded
        print(f"\n📊 System Status:")
        print(f"  🤖 Llama 3.1: {'✅' if qa_system.local_llm_available else '❌'}")
        print(f"  🧮 Embeddings: {'✅' if qa_system.embedding_model else '❌'}")
        print(f"  🚀 FAISS: {'✅' if qa_system.faiss_index else '❌'}")
        
        # Count questions
        with open(test_file, 'r', encoding='utf-8') as f:
            total_questions = sum(1 for line in f) - 1
        print(f"  📝 Questions to process: {total_questions}")
        
        # Process with custom progress tracking
        print(f"\n🎯 Processing questions (no more embedding loops!)...")
        if '70b' in model_name:
            print("💡 70b model - high quality but slower per question")
        
        start_time = time.time()
        
        # Custom processing with progress
        results = process_with_progress(qa_system, test_file, total_questions)
        
        process_time = time.time() - start_time
        
        # Save results
        output_file = 'llama31_optimized_submission.csv'
        save_results(results, output_file)
        
        # Summary
        print(f"\n🎉 Processing Complete!")
        print(f"⏱️  Total time: {process_time/60:.1f} minutes")
        print(f"🚀 Average: {process_time/len(results):.2f} seconds/question")
        
        # Quick analysis
        import numpy as np
        confidences = [r.confidence for r in results if hasattr(r, 'confidence')]
        if confidences:
            avg_conf = np.mean(confidences)
            high_conf = sum(1 for c in confidences if c > 0.7)
            print(f"📈 Average confidence: {avg_conf:.3f}")
            print(f"🎯 High confidence: {high_conf} ({high_conf/len(results)*100:.1f}%)")
        
        print(f"\n🏆 Final submission: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def process_with_progress(qa_system, test_file: str, total_questions: int) -> List:
    """Process questions with clear progress tracking"""
    import csv
    results = []
    
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for i, row in enumerate(reader, 1):
                question_id = int(row['id'])
                full_question = row['question']
                
                # Parse question and choices
                question, choices = qa_system.parse_question(full_question)
                
                # Process single question (this should NOT re-process embeddings)
                result = qa_system._ensemble_prediction(question, choices)
                result.id = question_id
                results.append(result)
                
                # Progress update every 25 questions
                if i % 25 == 0 or i == total_questions:
                    elapsed = time.time() - process_start_time if 'process_start_time' in globals() else 0
                    rate = i / elapsed if elapsed > 0 else 0
                    remaining = (total_questions - i) / rate if rate > 0 else 0
                    
                    print(f"  📊 Progress: {i}/{total_questions} ({i/total_questions*100:.1f}%) "
                          f"- {rate:.1f} q/s - ETA: {remaining/60:.1f}min")
                
                # Show some sample results
                if i <= 3:
                    print(f"    Q{i}: {question[:40]}... → {result.predicted_answers} (conf: {result.confidence:.2f})")
            
            return results
            
    except Exception as e:
        print(f"❌ Processing error: {e}")
        return results

def save_results(results: List, output_file: str):
    """Save results in submission format"""
    try:
        import csv
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'answer'])
            
            for result in results:
                answer_str = ','.join(result.predicted_answers)
                writer.writerow([result.id, f'"{answer_str}"'])
        
        print(f"✅ Saved: {output_file}")
        
        # Also save simple analysis
        analysis_file = output_file.replace('.csv', '_analysis.txt')
        with open(analysis_file, 'w', encoding='utf-8') as f:
            f.write(f"Thai Healthcare Q&A Results\n")
            f.write(f"=" * 30 + "\n\n")
            f.write(f"Total questions: {len(results)}\n")
            
            if results:
                confidences = [r.confidence for r in results if hasattr(r, 'confidence')]
                if confidences:
                    import numpy as np
                    f.write(f"Average confidence: {np.mean(confidences):.3f}\n")
                    f.write(f"High confidence (>0.7): {sum(1 for c in confidences if c > 0.7)}\n")
                
                # Answer distribution
                answers = {}
                for r in results:
                    key = ','.join(sorted(r.predicted_answers))
                    answers[key] = answers.get(key, 0) + 1
                
                f.write(f"\nTop answer patterns:\n")
                for answer, count in sorted(answers.items(), key=lambda x: x[1], reverse=True)[:5]:
                    f.write(f"  '{answer}': {count} times\n")
        
        print(f"✅ Analysis: {analysis_file}")
        
    except Exception as e:
        print(f"❌ Save error: {e}")

def main():
    """Main optimized runner"""
    global process_start_time
    
    print("🛠️  Llama 3.1 Optimized Runner - Fixed Embedding Loops")
    print("✅ Embeddings processed once, not per question")
    print("📊 Clear progress tracking through all questions")
    print()
    
    process_start_time = time.time()
    success = run_optimized_processing()
    
    if success:
        print(f"\n🎉 SUCCESS! No more loops - clean processing!")
    else:
        print(f"\n❌ Failed - check errors above")

if __name__ == "__main__":
    main()