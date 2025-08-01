#!/usr/bin/env python3
"""
Demo script showing the enhanced batch processor features
"""

import os
import csv
from batch_test_processor import validate_csv_format, preview_csv, show_help


def demo_features():
    """Demonstrate the enhanced batch processor features"""
    
    print("🎯 Enhanced Batch Processor Demo")
    print("=" * 60)
    
    # Feature 1: Auto-detect test.csv
    print("🔍 Feature 1: Auto-detect test.csv location")
    print("-" * 40)
    
    possible_paths = ["test.csv", "../test.csv", "AI/test.csv"]
    found_file = None
    
    for path in possible_paths:
        if os.path.exists(path):
            found_file = path
            print(f"   ✅ Found: {path}")
            break
        else:
            print(f"   🔍 Checking: {path}")
    
    if not found_file:
        print("   ❌ test.csv not found in standard locations")
        return
    
    print(f"\n📁 Using file: {found_file}")
    
    # Feature 2: CSV validation
    print("\n🔍 Feature 2: CSV Format Validation")
    print("-" * 40)
    
    is_valid, message = validate_csv_format(found_file)
    print(f"   Status: {'✅' if is_valid else '❌'} {message}")
    
    if not is_valid:
        return
    
    # Feature 3: Preview CSV content
    print("\n📋 Feature 3: CSV Content Preview")
    print("-" * 40)
    
    preview_csv(found_file, num_rows=5)
    
    # Feature 4: Count questions
    print("\n📊 Feature 4: Question Statistics")
    print("-" * 40)
    
    try:
        with open(found_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            questions = list(reader)
            
        total_questions = len(questions)
        print(f"   📝 Total questions: {total_questions}")
        
        # Sample question analysis
        if questions:
            sample_q = questions[0]['question']
            choices = ['ก.', 'ข.', 'ค.', 'ง.']
            choice_count = sum(1 for choice in choices if choice in sample_q)
            print(f"   🎯 Choices per question: ~{choice_count}")
            
            # Check question types
            has_thai = any(ord(c) >= 0x0E00 and ord(c) <= 0x0E7F for c in sample_q)
            print(f"   🇹🇭 Thai language content: {'✅' if has_thai else '❌'}")
            
    except Exception as e:
        print(f"   ❌ Error analyzing questions: {e}")
    
    # Feature 5: Show usage examples
    print("\n💡 Feature 5: Usage Examples")
    print("-" * 40)
    
    print("   Basic usage:")
    print("     python batch_test_processor.py")
    print()
    print("   With custom settings:")
    print("     python batch_test_processor.py test.csv results.csv 10")
    print()
    print("   Auto mode (no confirmation):")
    print("     python batch_test_processor.py test.csv results.csv 10 --auto")
    print()
    print("   Help:")
    print("     python batch_test_processor.py --help")
    
    # Feature 6: Expected output format
    print("\n📤 Feature 6: Expected Output Format")
    print("-" * 40)
    
    print("   Input CSV format:")
    print("     id,question,answer")
    print("     1,คำถาม? ก. A ข. B ค. C ง. D,")
    print()
    print("   Output CSV format:")
    print("     id,question,answer")
    print("     1,คำถาม? ก. A ข. B ค. C ง. D,ค")
    print()
    print("   Answer format: Only choice letters (ก, ข, ค, ง)")
    
    print("\n" + "=" * 60)
    print("🎉 Enhanced batch processor is ready!")
    print("   ✅ Auto-detects test.csv location")
    print("   ✅ Validates CSV format before processing")
    print("   ✅ Shows preview of questions")
    print("   ✅ Counts total questions")
    print("   ✅ Interactive confirmation (or --auto mode)")
    print("   ✅ Detailed progress tracking")
    print("   ✅ Results preview after completion")
    print("   ✅ Comprehensive error handling")


if __name__ == "__main__":
    demo_features()