#!/usr/bin/env python3
"""
Production runner for Thai Healthcare Q&A System
Run this to generate the final submission file
"""

import os
import sys
import time
from datetime import datetime
from thai_healthcare_qa_system import ThaiHealthcareQASystem

def check_requirements():
    """Check if all required files exist"""
    required_files = [
        'Healthcare-AI-Refactored/src/infrastructure/test.csv',
        'Healthcare-AI-Refactored/src/infrastructure/results_doc/direct_extraction_corrected.txt',
        'Healthcare-AI-Refactored/src/infrastructure/results_doc2/direct_extraction_corrected.txt',
        'Healthcare-AI-Refactored/src/infrastructure/results_doc3/direct_extraction_corrected.txt'
    ]
    
    missing = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing.append(file_path)
    
    if missing:
        print(f"❌ Missing required files:")
        for file_path in missing:
            print(f"   - {file_path}")
        return False
    
    # Show file sizes
    print(f"📁 Input Files:")
    for file_path in required_files:
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        print(f"   ✅ {os.path.basename(file_path)}: {size_mb:.2f} MB")
    
    return True

def run_full_processing():
    """Run the complete Thai healthcare Q&A processing"""
    print("🏥 Thai Healthcare Q&A System - Production Run")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    try:
        # Configuration
        knowledge_files = [
            'Healthcare-AI-Refactored/src/infrastructure/results_doc/direct_extraction_corrected.txt',
            'Healthcare-AI-Refactored/src/infrastructure/results_doc2/direct_extraction_corrected.txt',
            'Healthcare-AI-Refactored/src/infrastructure/results_doc3/direct_extraction_corrected.txt'
        ]
        test_file = 'Healthcare-AI-Refactored/src/infrastructure/test.csv'
        output_file = 'submission.csv'
        
        # Count total questions
        with open(test_file, 'r', encoding='utf-8') as f:
            total_questions = sum(1 for line in f) - 1  # Subtract header
        
        print(f"📊 Processing {total_questions} Thai healthcare questions")
        print(f"📚 Using {len(knowledge_files)} knowledge base documents")
        print("-" * 60)
        
        # Initialize system
        print("🔧 Initializing Thai Healthcare Q&A System...")
        qa_system = ThaiHealthcareQASystem(
            knowledge_files, 
            memory_file="thai_healthcare_memory.json"
        )
        print("✅ System initialized successfully")
        
        # Process all questions
        print(f"\n🚀 Starting processing...")
        results = qa_system.process_test_file(test_file, output_file)
        
        # Calculate processing time
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Summary
        print(f"\n🎉 Processing Complete!")
        print("=" * 60)
        print(f"⏱️  Total time: {processing_time:.1f} seconds")
        print(f"📊 Questions processed: {len(results)}")
        print(f"⚡ Average time per question: {processing_time/len(results):.2f} seconds")
        
        # Confidence analysis
        high_conf = sum(1 for r in results if r.confidence > 0.5)
        medium_conf = sum(1 for r in results if 0.2 <= r.confidence <= 0.5)
        low_conf = sum(1 for r in results if r.confidence < 0.2)
        
        print(f"\n📈 Confidence Distribution:")
        print(f"   🟢 High confidence (>0.5): {high_conf} ({high_conf/len(results)*100:.1f}%)")
        print(f"   🟡 Medium confidence (0.2-0.5): {medium_conf} ({medium_conf/len(results)*100:.1f}%)")
        print(f"   🔴 Low confidence (<0.2): {low_conf} ({low_conf/len(results)*100:.1f}%)")
        
        # Answer distribution
        answer_counts = {}
        multiple_answers = 0
        
        for result in results:
            answer_key = ','.join(sorted(result.predicted_answers))
            answer_counts[answer_key] = answer_counts.get(answer_key, 0) + 1
            if len(result.predicted_answers) > 1:
                multiple_answers += 1
        
        print(f"\n📋 Answer Distribution:")
        print(f"   🔢 Multiple choice answers: {multiple_answers} ({multiple_answers/len(results)*100:.1f}%)")
        print(f"   📝 Most common answers:")
        for answer, count in sorted(answer_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"      '{answer}': {count} times ({count/len(results)*100:.1f}%)")
        
        # File outputs
        print(f"\n📄 Generated Files:")
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file) / 1024
            print(f"   📊 {output_file}: {file_size:.1f} KB (MAIN SUBMISSION)")
        
        detailed_file = output_file.replace('.csv', '_detailed.json')
        if os.path.exists(detailed_file):
            file_size = os.path.getsize(detailed_file) / 1024
            print(f"   📋 {detailed_file}: {file_size:.1f} KB (detailed analysis)")
        
        memory_file = "thai_healthcare_memory.json"
        if os.path.exists(memory_file):
            file_size = os.path.getsize(memory_file) / 1024
            print(f"   🧠 {memory_file}: {file_size:.1f} KB (system memory)")
        
        # Validation check
        print(f"\n🔍 Submission Validation:")
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if len(lines) == total_questions + 1:  # +1 for header
                print(f"   ✅ Correct number of predictions: {len(lines)-1}")
            else:
                print(f"   ❌ Incorrect number of predictions: {len(lines)-1} (expected {total_questions})")
        
        print(f"\n🎯 Ready for submission: {output_file}")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n❌ Error during processing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """Main execution function"""
    if not check_requirements():
        print(f"\n❌ Cannot proceed without required files.")
        sys.exit(1)
    
    print(f"\n⚠️  This will process all {500} questions and may take 10-30 minutes.")
    response = input("Continue? (y/N): ").strip().lower()
    
    if response not in ['y', 'yes']:
        print("Processing cancelled.")
        sys.exit(0)
    
    success = run_full_processing()
    
    if success:
        print(f"\n🎉 SUCCESS! Check submission.csv for your final predictions.")
        sys.exit(0)
    else:
        print(f"\n❌ FAILED! Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()