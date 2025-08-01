#!/usr/bin/env python3
"""
Test Improved Performance
========================

This script tests the performance improvements in the improved_healthcare_qa_system.py
"""

import asyncio
import time
import os
from improved_healthcare_qa_system import ImprovedHealthcareQA

async def test_improved_performance():
    """Test the performance of the improved system"""
    
    # Check if we have a test file
    test_files = [
        "test.csv",
        "Healthcare-AI-Refactored/src/infrastructure/test.csv",
        "Hackathon Test - Sheet1 (3).csv", 
        "Hackathon Test - Sheet2.csv"
    ]
    
    test_file = None
    for file in test_files:
        if os.path.exists(file):
            test_file = file
            break
    
    if not test_file:
        print("❌ No test file found. Please provide a CSV file with questions.")
        return
    
    print(f"🧪 Testing improved system with {test_file}")
    
    # Create system with different configurations
    configs = [
        {"max_workers": 3, "batch_size": 5, "name": "Conservative"},
        {"max_workers": 5, "batch_size": 10, "name": "Balanced"},
        {"max_workers": 8, "batch_size": 15, "name": "Aggressive"}
    ]
    
    for config in configs:
        print(f"\n🔧 Testing {config['name']} configuration:")
        print(f"   Max workers: {config['max_workers']}")
        print(f"   Batch size: {config['batch_size']}")
        
        # Create system
        qa_system = ImprovedHealthcareQA(
            max_workers=config['max_workers'],
            batch_size=config['batch_size']
        )
        
        # Test performance
        start_time = time.time()
        
        try:
            results = await qa_system.process_questions_enhanced(test_file)
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"   ✅ Completed in {duration:.1f} seconds")
            print(f"   📊 Processed {len(results)} questions")
            print(f"   🚀 Rate: {len(results)/duration:.1f} questions/second")
            
            # Save results
            output_file = f"improved_{config['name'].lower()}_submission.csv"
            qa_system.save_results(results, output_file)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Cleanup
        await qa_system.cleanup()

def compare_with_original():
    """Compare with original system timing"""
    print("\n📊 Performance Comparison:")
    print("Original system: ~30 minutes for full dataset")
    print("Improved system targets: 5-15 minutes for full dataset")
    print("Expected improvement: 2-6x faster")

if __name__ == "__main__":
    print("🚀 Improved Healthcare QA Performance Test")
    print("=" * 50)
    
    # Run performance test
    asyncio.run(test_improved_performance())
    
    # Show comparison
    compare_with_original()
    
    print("\n✅ Performance test complete!") 