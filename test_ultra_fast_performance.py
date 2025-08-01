#!/usr/bin/env python3
"""
Test Ultra-Fast Performance
==========================

This script tests the performance improvements of the ultra-fast system.
"""

import asyncio
import time
import os
from ultra_fast_healthcare_qa import UltraFastHealthcareQA

async def test_performance():
    """Test the performance of the ultra-fast system"""
    
    # Check if we have a test file
    test_files = [
        "test.csv",
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
    
    print(f"🧪 Testing ultra-fast system with {test_file}")
    
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
        qa_system = UltraFastHealthcareQA(
            max_workers=config['max_workers'],
            batch_size=config['batch_size']
        )
        
        # Test performance
        start_time = time.time()
        
        try:
            results = await qa_system.process_questions_ultra_fast(test_file)
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"   ✅ Completed in {duration:.1f} seconds")
            print(f"   📊 Processed {len(results)} questions")
            print(f"   🚀 Rate: {len(results)/duration:.1f} questions/second")
            
            # Save results
            output_file = f"ultra_fast_{config['name'].lower()}_submission.csv"
            qa_system.save_results(results, output_file)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Cleanup
        await qa_system.cleanup()

def compare_with_original():
    """Compare with original system timing"""
    print("\n📊 Performance Comparison:")
    print("Original system: ~30 minutes for full dataset")
    print("Ultra-fast system targets: 2-5 minutes for full dataset")
    print("Expected improvement: 6-15x faster")

if __name__ == "__main__":
    print("🚀 Ultra-Fast Healthcare QA Performance Test")
    print("=" * 50)
    
    # Run performance test
    asyncio.run(test_performance())
    
    # Show comparison
    compare_with_original()
    
    print("\n✅ Performance test complete!") 