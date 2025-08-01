#!/usr/bin/env python3
"""
Test Multiple Answer Extraction
===============================

Test the multiple answer detection functionality
"""

import re
from typing import List

def extract_multiple_answers(text: str) -> List[str]:
    """Extract multiple Thai choice answers from text"""
    # Clean the text
    text = text.strip().lower()
    
    # Pattern 1: "ข,ง" or "ก,ค,ง" 
    comma_pattern = re.search(r'([ก-ง](?:,\s*[ก-ง])+)', text)
    if comma_pattern:
        answers_str = comma_pattern.group(1)
        answers = [a.strip() for a in answers_str.split(',')]
        return [a for a in answers if a in ['ก', 'ข', 'ค', 'ง']]
    
    # Pattern 2: "ข และ ง" or "ก และ ค และ ง"
    and_pattern = re.search(r'([ก-ง](?:\s*และ\s*[ก-ง])+)', text)
    if and_pattern:
        answers_str = and_pattern.group(1)
        answers = re.findall(r'[ก-ง]', answers_str)
        return list(set(answers))  # Remove duplicates
    
    # Pattern 3: Multiple separate mentions like "ก ข ง" (but not in question text)
    # Look for multiple choice characters that appear after common answer keywords
    answer_section_patterns = [
        r'(?:คำตอบ|ตอบ|เลือก|ข้อ)[:\s]*(.+)',  # After answer keywords
        r'(.{0,50})$',  # Last 50 characters (likely the answer)
    ]
    
    for section_pattern in answer_section_patterns:
        section_match = re.search(section_pattern, text, re.IGNORECASE)
        if section_match:
            answer_section = section_match.group(1)
            # Only look for multiple chars in the answer section
            section_chars = re.findall(r'[ก-ง]', answer_section)
            if len(section_chars) > 1:
                unique_answers = list(dict.fromkeys(section_chars))
                # Only return if reasonable number and no common Thai words
                if 2 <= len(unique_answers) <= 4:
                    # Avoid cases where chars are part of Thai words
                    if not any(word in answer_section for word in ['คือ', 'เป็น', 'คำตอบ', 'ข้อ']):
                        return unique_answers
    
    return []

def extract_single_answer(text: str) -> str:
    """Extract single Thai choice answer from text"""
    # Look for various single answer patterns
    patterns = [
        r'\[([ก-ง])\]',                    # [ก]
        r'^([ก-ง])',                       # ก at start of line
        r'คำตอบ[:\s]*(?:คือ\s*)?([ก-ง])',  # คำตอบ: ก or คำตอบคือ ก
        r'ตอบ[:\s]*([ก-ง])',               # ตอบ: ก
        r'เลือก\s*([ก-ง])',                # เลือก ก
        r'([ก-ง])\s*(?:คือ|เป็น)',        # ก คือ
        r'(?:คือ|เป็น)\s*([ก-ง])',         # คือ ก
        r'([ก-ง])\s*เป็นคำตอบ',            # ก เป็นคำตอบ
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return match.group(1)
    
    # Last resort: any Thai choice character
    choice_match = re.search(r'[ก-ง]', text)
    if choice_match:
        return choice_match.group()
    
    return None

def test_extraction():
    """Test the extraction functions"""
    print("🧪 Testing Multiple Answer Extraction")
    print("=" * 40)
    
    # Test cases for multiple answers
    multiple_test_cases = [
        ("คำตอบคือ ข,ง", ["ข", "ง"]),
        ("ก,ค,ง เป็นคำตอบที่ถูกต้อง", ["ก", "ค", "ง"]),
        ("ตอบ: ข และ ง", ["ข", "ง"]),
        ("เลือก ก และ ค และ ง", ["ก", "ค", "ง"]),
        ("คำตอบ ก ข ค", ["ก", "ข", "ค"]),
        ("ข, ง", ["ข", "ง"]),
        ("[ก,ง]", ["ก", "ง"]),
    ]
    
    # Test cases for single answers
    single_test_cases = [
        ("คำตอบคือ ง", "ง"),
        ("[ข]", "ข"),
        ("ตอบ: ก", "ก"),
        ("เลือก ค", "ค"),
        ("ง เป็นคำตอบที่ถูก", "ง"),
        ("คำตอบ ข", "ข"),
    ]
    
    print("📊 Testing Multiple Answers:")
    passed_multiple = 0
    for i, (text, expected) in enumerate(multiple_test_cases, 1):
        result = extract_multiple_answers(text)
        if result == expected or set(result) == set(expected):
            print(f"  ✅ Test {i}: '{text}' → {result}")
            passed_multiple += 1
        else:
            print(f"  ❌ Test {i}: '{text}' → {result} (expected: {expected})")
    
    print(f"\n📊 Testing Single Answers:")
    passed_single = 0
    for i, (text, expected) in enumerate(single_test_cases, 1):
        # For single answers, we use multiple first, then fallback to single
        result_multiple = extract_multiple_answers(text)
        if result_multiple:
            result = result_multiple[0] if len(result_multiple) == 1 else None
        else:
            result = extract_single_answer(text)
        
        if result == expected:
            print(f"  ✅ Test {i}: '{text}' → '{result}'")
            passed_single += 1
        else:
            print(f"  ❌ Test {i}: '{text}' → '{result}' (expected: '{expected}')")
    
    # Summary
    total_tests = len(multiple_test_cases) + len(single_test_cases)
    total_passed = passed_multiple + passed_single
    
    print(f"\n🎯 Test Results:")
    print(f"  Multiple answers: {passed_multiple}/{len(multiple_test_cases)} passed")
    print(f"  Single answers: {passed_single}/{len(single_test_cases)} passed")
    print(f"  Overall: {total_passed}/{total_tests} passed ({total_passed/total_tests*100:.1f}%)")
    
    if total_passed == total_tests:
        print(f"\n🎉 All tests passed! Multiple answer detection is working correctly.")
    else:
        print(f"\n⚠️  Some tests failed. Review the extraction logic.")
    
    return total_passed == total_tests

def main():
    """Main test function"""
    success = test_extraction()
    
    if success:
        print(f"\n✅ Ready for multiple answer processing!")
        print(f"🚀 The system can now handle:")
        print(f"   • Single answers: '1,\"ง\"'")
        print(f"   • Multiple answers: '5,\"ข,ง\"'")
        print(f"   • Complex answers: '10,\"ก,ค,ง\"'")
    else:
        print(f"\n🔧 Fix extraction logic before proceeding")

if __name__ == "__main__":
    main()