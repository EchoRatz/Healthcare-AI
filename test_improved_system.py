#!/usr/bin/env python3
"""
Test Improved Healthcare Q&A System
===================================

Test script to validate the improved system and compare with original implementation
"""

import os
import sys
import csv
import time
from improved_healthcare_qa_system import ImprovedHealthcareQA

def test_single_question():
    """Test the system with a single question"""
    print("🧪 Testing single question...")
    
    qa_system = ImprovedHealthcareQA()
    
    # Test question (from the dataset)
    test_question = {
        'id': '1',
        'question': 'ผมปวดท้องมาก อ้วกด้วย ตอนนี้ตีสองยังมีแผนกไหนเปิดอยู่ไหมครับ?  ก. Endocrinology ข. Orthopedics ค. Emergency ง. Internal Medicine'
    }
    
    # Parse question
    question, choices = qa_system.parse_question(test_question['question'])
    print(f"Question: {question}")
    print(f"Choices: {choices}")
    
    # Analyze question
    analysis = qa_system.analyze_question(question)
    print(f"Analysis: {analysis}")
    
    # Load knowledge base
    qa_system.load_knowledge_base()
    
    # Search context
    context = qa_system.search_context(analysis)
    print(f"Context length: {len(context)} chars")
    
    # Query LLM (if available)
    if qa_system.check_llama31():
        answers, confidence = qa_system.query_llama31_enhanced(question, choices, context)
        print(f"Answers: {answers}")
        print(f"Confidence: {confidence}")
        
        # Validate
        validation = qa_system.validate_answer_enhanced(question, choices, answers, context)
        print(f"Validation: {validation}")
    else:
        print("❌ Llama 3.1 not available for testing")

def test_question_analysis():
    """Test question analysis with various question types"""
    print("\n🔍 Testing question analysis...")
    
    qa_system = ImprovedHealthcareQA()
    
    test_questions = [
        "สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ?",
        "ค่าบริการเคลือบฟลูออไรด์ชนิดเข้มข้นสูงเฉพาะที่มีอัตราเหมาจ่ายเท่าใดต่อครั้ง?",
        "ข้อใดต่อไปนี้เป็นอาการฉุกเฉินวิกฤตที่เข้าข่ายสิทธิ UCEP?",
        "การผ่าคลอดสามารถใช้สิทธิหลักประกันสุขภาพแห่งชาติได้ในกรณีใด?",
        "ผู้ที่ต้องการใส่ฟันปลอมต้องมีอายุเท่าใดขึ้นไป?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        analysis = qa_system.analyze_question(question)
        print(f"\nQuestion {i}: {question}")
        print(f"  Type: {analysis.question_type}")
        print(f"  Keywords: {analysis.keywords}")
        print(f"  Entities: {analysis.entities}")
        print(f"  Confidence: {analysis.confidence:.2f}")

def test_knowledge_base_indexing():
    """Test knowledge base indexing"""
    print("\n📚 Testing knowledge base indexing...")
    
    qa_system = ImprovedHealthcareQA()
    qa_system.load_knowledge_base()
    
    print(f"Indexed keywords: {len(qa_system.knowledge_base)}")
    
    # Test search for specific terms
    test_keywords = ["สิทธิ", "หลักประกัน", "สุขภาพ", "การรักษา", "ยา"]
    
    for keyword in test_keywords:
        if keyword in qa_system.knowledge_base:
            sections = qa_system.knowledge_base[keyword]
            print(f"  {keyword}: {len(sections)} sections")
        else:
            print(f"  {keyword}: Not found")

def test_answer_extraction():
    """Test answer extraction patterns"""
    print("\n📝 Testing answer extraction...")
    
    qa_system = ImprovedHealthcareQA()
    
    test_responses = [
        "คำตอบ: ก",
        "ตอบ: ข,ค",
        "ตัวเลือกที่ถูกต้องคือ ง",
        "ก และ ข ถูกต้อง",
        "ไม่มีข้อใดถูกต้อง ง",
        "คำตอบคือ ก,ข,ค",
        "ตอบ ก"
    ]
    
    choices = {'ก': 'Choice A', 'ข': 'Choice B', 'ค': 'Choice C', 'ง': 'Choice D'}
    
    for response in test_responses:
        answers = qa_system._extract_answers_enhanced(response, choices)
        print(f"Response: {response}")
        print(f"  Extracted: {answers}")

def test_validation_logic():
    """Test answer validation logic"""
    print("\n✅ Testing validation logic...")
    
    qa_system = ImprovedHealthcareQA()
    
    test_cases = [
        {
            'question': 'สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ?',
            'choices': {
                'ก': 'สิทธิหลักประกันสุขภาพแห่งชาติ',
                'ข': 'สิทธิบัตรทอง', 
                'ค': 'สิทธิ 30 บาทรักษาทุกโรค',
                'ง': 'ไม่มีข้อใดถูกต้อง'
            },
            'answers': ['ข', 'ง', 'ก'],
            'expected_issue': 'Contradiction with ง'
        },
        {
            'question': 'ค่าบริการเคลือบฟลูออไรด์มีอัตราเท่าใด?',
            'choices': {
                'ก': '50 บาท',
                'ข': '75 บาท',
                'ค': '100 บาท', 
                'ง': '150 บาท'
            },
            'answers': ['ก', 'ข', 'ค', 'ง'],
            'expected_issue': 'All choices selected'
        },
        {
            'question': 'ข้อใดเป็นอาการฉุกเฉิน?',
            'choices': {
                'ก': 'เจ็บหน้าอกเฉียบพลัน',
                'ข': 'ปวดหัว',
                'ค': 'มีไข้',
                'ง': 'ปวดท้องเรื้อรัง'
            },
            'answers': ['ก'],
            'expected_issue': 'Valid answer'
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\nTest case {i}:")
        validation = qa_system.validate_answer_enhanced(
            case['question'], 
            case['choices'], 
            case['answers'], 
            "Test context"
        )
        print(f"  Answers: {case['answers']}")
        print(f"  Valid: {validation.is_valid}")
        print(f"  Reasoning: {validation.reasoning}")
        print(f"  Expected: {case['expected_issue']}")

def compare_with_original():
    """Compare results with original implementation"""
    print("\n📊 Comparing with original implementation...")
    
    # Load original results
    original_file = "ultra_fast_submission.csv"
    improved_file = "improved_healthcare_submission.csv"
    
    if not os.path.exists(original_file):
        print(f"❌ Original file not found: {original_file}")
        return
    
    if not os.path.exists(improved_file):
        print(f"❌ Improved file not found: {improved_file}")
        return
    
    # Load both results
    original_results = {}
    with open(original_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            original_results[row['id']] = row['answer']
    
    improved_results = {}
    with open(improved_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            improved_results[row['id']] = row['answer']
    
    # Compare
    total_questions = len(original_results)
    same_answers = 0
    different_answers = 0
    original_none_count = 0
    improved_none_count = 0
    
    for qid in original_results:
        original_answer = original_results[qid]
        improved_answer = improved_results.get(qid, "ง")
        
        if original_answer == improved_answer:
            same_answers += 1
        else:
            different_answers += 1
        
        if original_answer == "ง":
            original_none_count += 1
        if improved_answer == "ง":
            improved_none_count += 1
    
    print(f"Total questions: {total_questions}")
    print(f"Same answers: {same_answers} ({same_answers/total_questions*100:.1f}%)")
    print(f"Different answers: {different_answers} ({different_answers/total_questions*100:.1f}%)")
    print(f"Original 'ง' answers: {original_none_count} ({original_none_count/total_questions*100:.1f}%)")
    print(f"Improved 'ง' answers: {improved_none_count} ({improved_none_count/total_questions*100:.1f}%)")
    
    # Show some examples of differences
    print(f"\nExamples of different answers:")
    count = 0
    for qid in original_results:
        if count >= 5:  # Show only first 5 differences
            break
        original_answer = original_results[qid]
        improved_answer = improved_results.get(qid, "ง")
        if original_answer != improved_answer:
            print(f"  Q{qid}: {original_answer} → {improved_answer}")
            count += 1

def main():
    """Run all tests"""
    print("🧪 IMPROVED HEALTHCARE Q&A SYSTEM - TESTING")
    print("=" * 60)
    
    # Test individual components
    test_question_analysis()
    test_knowledge_base_indexing()
    test_answer_extraction()
    test_validation_logic()
    
    # Test single question (if LLM available)
    test_single_question()
    
    # Compare with original (if files exist)
    compare_with_original()
    
    print("\n✅ Testing complete!")

if __name__ == "__main__":
    main() 