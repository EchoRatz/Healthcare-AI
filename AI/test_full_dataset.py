#!/usr/bin/env python3
"""
Test the intelligent knowledge caching system with the full test.csv dataset
Modified to output clean CSV format (id,answer only) with 120 threads
"""

from thai_qa_processor import ThaiHealthcareQA
import time
import csv

def test_full_dataset():
    """Test with the complete test.csv dataset and output clean CSV"""
    print("=" * 60)
    print("Testing Intelligent Knowledge Caching with Full Dataset")
    print("Output: Clean CSV format (id,answer only)")
    print("🚀 Using 120 Threads for Ultra-Fast Processing!")
    print("=" * 60)
    print("Processing 500 questions from test.csv...")
    print("This will show how the AI learns from real healthcare data!")
    
    # Initialize the system
    print("\nInitializing Thai Healthcare Q&A System...")
    qa_system = ThaiHealthcareQA()
    
    # Show initial cache stats
    print("\nCurrent cache before processing test.csv:")
    qa_system.show_cache_stats()
    
    # Process the full dataset with CLEAN FORMAT + 120 THREADS
    print("\nStarting batch processing of test.csv...")
    print("🔥 Using 120 threads - This should be MUCH faster!")
    
    start_time = time.time()
    
    try:
        # 🎯 แทนที่ process_csv_questions ด้วย process_csv_multithreaded
        qa_system.process_csv_multithreaded(
            'test.csv', 
            'test_answers_clean_output.csv',  # หรือจะใช้ 'output_120_threads.csv'
            max_threads=120,
            clean_format=True
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"\n🎉 Processing completed in {processing_time:.1f} seconds")
        print(f"⚡ That's {500/processing_time:.1f} questions per second!")
        
        # Show final cache stats
        print("\nFinal cache after processing test.csv:")
        qa_system.show_cache_stats()
        
        # Export the knowledge gained
        print("\nExporting learned knowledge...")
        qa_system.export_cache_to_text("full_dataset_learned_knowledge.txt")
        
        print("\n" + "=" * 60)
        print("SUCCESS! Clean CSV output generated with 120 threads!")
        print("📄 Output file: test_answers_clean_output.csv")
        print("📋 Format: id,answer (exactly like your submission.csv)")
        print("🚀 Processing speed: ULTRA FAST with multithreading!")
        print("=" * 60)
        
        # Show sample of clean output
        print("\nSample of clean CSV output:")
        try:
            with open('test_answers_clean_output.csv', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print("id,answer")  # Header
                for i in range(min(5, len(lines)-1)):  # Show first 5 answers
                    print(lines[i+1].strip())  # Skip header line
        except Exception as e:
            print(f"Could not display sample: {e}")
        
    except Exception as e:
        print(f"Error during processing: {e}")
        print("Make sure Ollama is running and models are available")
        print("Also check if your system can handle 120 concurrent connections")

def test_adaptive_threading():
    """Alternative: Use adaptive threading (recommended)"""
    print("🤖 Testing with Adaptive Threading (Recommended)")
    qa_system = ThaiHealthcareQA()
    
    qa_system.process_csv_adaptive_threads(
        'test.csv',
        'test_answers_adaptive.csv',
        clean_format=True
    )

if __name__ == "__main__":
    # เลือกวิธีใดวิธีหนึ่ง:
    
    # วิธีที่ 1: ใช้ 120 threads เต็ม
    test_full_dataset()
    
    # วิธีที่ 2: ใช้ adaptive threading (แนะนำ)
    # test_adaptive_threading()