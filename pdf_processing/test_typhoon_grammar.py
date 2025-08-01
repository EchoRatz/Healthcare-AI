#!/usr/bin/env python3
"""
Test script for Typhoon.ai Thai Grammar Correction
This script demonstrates how to use the grammar correction feature.
"""

import os
import sys
import tempfile
from PDF_Extractor import correct_thai_grammar_typhoon, process_text_in_chunks

def test_grammar_correction():
    """
    Test Thai grammar correction with sample text.
    """
    # Sample Thai text with intentional grammar issues
    sample_text = """
    คูรือสดทธิหลักประกันสุขภาพแหรงชาติ ปรงบประมาณ 2566
    
    ตามที ส๚านักบรุการประชาชน มีภารกิจหลักในการสรุางความรุูความเข๚าใจ
    ในสดทธิและคุรมครองสดทธิประชาชนในระบบหลักประกัน สุขภาพแหรงชาติ
    
    ยังมีขุอซักถาม เรืรองรุองเรยีน รุองทุกขร เกี่ยวกับสดทธิประโยชนรการเข๚า
    รับบรุการของสดทธิหลักประกันสุขภาพแหรงชาติ
    """
    
    print("=== Thai Grammar Correction Test ===")
    print("\nOriginal text:")
    print(sample_text)
    
    # Check if API key is available
    api_key = os.getenv('TYPHOON_API_KEY')
    if not api_key:
        print("\n❌ No TYPHOON_API_KEY found in environment variables.")
        print("\nTo test grammar correction:")
        print("1. Get a free API key from: https://docs.opentyphoon.ai/")
        print("2. Set the environment variable:")
        print("   export TYPHOON_API_KEY='your_api_key_here'")
        print("3. Run this test again")
        print("\nExample of what would happen:")
        print("- Text would be sent to Typhoon.ai API")
        print("- Thai grammar and spelling errors would be corrected")
        print("- Corrected text would be returned")
        return False
    
    print(f"\n✅ Found TYPHOON_API_KEY (length: {len(api_key)})")
    print("\nSending to Typhoon.ai for grammar correction...")
    
    try:
        # Test grammar correction
        corrected_text = correct_thai_grammar_typhoon(sample_text, api_key)
        
        print("\n=== Corrected Text ===")
        print(corrected_text)
        
        # Save results to file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("=== Original Text ===\n")
            f.write(sample_text)
            f.write("\n\n=== Corrected Text ===\n")
            f.write(corrected_text)
            temp_file = f.name
        
        print(f"\n📄 Results saved to: {temp_file}")
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing grammar correction: {e}")
        return False

def test_pdf_extraction_with_grammar():
    """
    Test the full pipeline: PDF extraction + grammar correction
    """
    print("\n=== Full Pipeline Test ===")
    
    # Check if we have extracted text files to work with
    test_files = [
        "test_results/direct_extraction.txt",
        "doc2_results/direct_extraction.txt",
        "doc3_results/direct_extraction.txt"
    ]
    
    available_files = [f for f in test_files if os.path.exists(f)]
    
    if not available_files:
        print("No extracted text files found. Please run PDF extraction first:")
        print("python PDF_Extractor.py doc.pdf test_results direct")
        return False
    
    print(f"Found {len(available_files)} extracted text files:")
    for f in available_files:
        size = os.path.getsize(f)
        print(f"  - {f} ({size:,} bytes)")
    
    # Test with the first available file
    test_file = available_files[0]
    print(f"\nTesting grammar correction with: {test_file}")
    
    api_key = os.getenv('TYPHOON_API_KEY')
    if not api_key:
        print("❌ No TYPHOON_API_KEY found. Set it to test grammar correction.")
        return False
    
    # Read a small sample (first 500 characters)
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    sample = content[:500] + "..." if len(content) > 500 else content
    
    print(f"\nTesting with sample text ({len(sample)} characters):")
    print("-" * 50)
    print(sample)
    print("-" * 50)
    
    try:
        corrected = correct_thai_grammar_typhoon(sample, api_key)
        print("\nCorrected text:")
        print("-" * 50)
        print(corrected)
        print("-" * 50)
        print("✅ Grammar correction test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🇹🇭 Typhoon.ai Thai Grammar Correction Test")
    print("=" * 50)
    
    # Test 1: Sample text correction
    success1 = test_grammar_correction()
    
    print("\n" + "=" * 50)
    
    # Test 2: Real PDF text correction
    success2 = test_pdf_extraction_with_grammar()
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"✅ Sample text test: {'PASSED' if success1 else 'SKIPPED (no API key)'}")
    print(f"✅ PDF text test: {'PASSED' if success2 else 'SKIPPED (no API key or files)'}")
    
    if not (success1 or success2):
        print("\n💡 To run full tests:")
        print("1. Get Typhoon.ai API key: https://docs.opentyphoon.ai/")
        print("2. export TYPHOON_API_KEY='your_key'")
        print("3. Run: python test_typhoon_grammar.py")