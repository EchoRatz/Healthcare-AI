#!/usr/bin/env python3
"""
Debug Single Answer Extraction
===============================
"""

import re

def extract_single_answer(text: str) -> str:
    """Extract single Thai choice answer from text"""
    print(f"    Debugging text: '{text}' (lowercase: '{text.lower()}')")
    
    # Look for various single answer patterns
    patterns = [
        (r'\[([ก-ง])\]', "[ก]"),
        (r'^([ก-ง])', "ก at start"),
        (r'คำตอบ[:\s]*(?:คือ\s*)?([ก-ง])', "คำตอบ: ก or คำตอบคือ ก"),
        (r'ตอบ[:\s]*([ก-ง])', "ตอบ: ก"),
        (r'เลือก\s*([ก-ง])', "เลือก ก"),
        (r'([ก-ง])\s*(?:คือ|เป็น)', "ก คือ/เป็น"),
        (r'(?:คือ|เป็น)\s*([ก-ง])', "คือ/เป็น ก"),
        (r'([ก-ง])\s*เป็นคำตอบ', "ก เป็นคำตอบ"),
    ]
    
    for i, (pattern, desc) in enumerate(patterns):
        match = re.search(pattern, text.lower())
        if match:
            print(f"    ✅ Pattern {i+1} ({desc}) matched: {match.group(1)}")
            return match.group(1)
        else:
            print(f"    ❌ Pattern {i+1} ({desc}) no match")
    
    # Last resort: any Thai choice character
    choice_match = re.search(r'[ก-ง]', text)
    if choice_match:
        print(f"    ✅ Fallback matched: {choice_match.group()}")
        return choice_match.group()
    else:
        print(f"    ❌ No Thai characters found")
    
    return None

# Test the problematic cases
test_cases = [
    "คำตอบคือ ง",
    "เลือก ค", 
    "ง เป็นคำตอบที่ถูก",
    "คำตอบ ข"
]

print("🔍 Debugging Single Answer Extraction")
print("=" * 40)

for text in test_cases:
    print(f"\nTesting: '{text}'")
    result = extract_single_answer(text)
    print(f"Result: {result}")
    print("-" * 30)