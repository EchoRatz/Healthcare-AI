#!/usr/bin/env python3
"""
Test Optimized Healthcare Q&A System
====================================

Performance comparison and validation script
"""

import os
import sys
import time
import csv
from optimized_healthcare_qa_system import OptimizedHealthcareQA

def test_single_question():
    """Test single question processing"""
    print("🧪 Testing single question...")
    
    qa_system = OptimizedHealthcareQA()
    
    test_question = {
        'id': '1',
        'question': 'ผมปวดท้องมาก อ้วกด้วย ตอนนี้ตีสองยังมีแผนกไหนเปิดอยู่ไหมครับ?  ก. Endocrinology ข. Orthopedics ค. Emergency ง. Internal Medicine'
    }
    
    # Parse question
    question, choices = qa_system.parse_question_fast(test_question['question'])
    print(f"Question: {question}")
    print(f"Choices: {choices}")
    
    # Analyze question
    analysis = qa_system.analyze_question_fast(question)
    print(f"Analysis: {analysis}")
    
    # Search context
    context = qa_system.search_context_fast(analysis)
    print(f"Context length: {len(context)} chars")
    
    # Query LLM
    if qa_system.check_llama31():
        result = qa_system.query_llama31_optimized(question, choices, context)
        print(f"Answer: {result.answer}")
        print(f"Confidence: {result.confidence}")
        print(f"Reasoning: {result.reasoning}")
    else:
        print("❌ Llama 3.1 not available")

def test_performance():
    """Test performance with small batch"""
    print("\n⚡ Testing performance...")
    
    qa_system = OptimizedHealthcareQA()
    
    # Create small test file
    test_questions = [
        {'id': '1', 'question': 'สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ? ก. การรักษาพยาบาล ข. การผ่าตัด ค. การทำฟัน ง. การตรวจสุขภาพ'},
        {'id': '2', 'question': 'ค่าบริการเคลือบฟลูออไรด์ชนิดเข้มข้นสูงเฉพาะที่มีอัตราเหมาจ่ายเท่าใดต่อครั้ง? ก. 100 บาท ข. 200 บาท ค. 300 บาท ง. 400 บาท'},
        {'id': '3', 'question': 'ข้อใดต่อไปนี้เป็นอาการฉุกเฉินวิกฤตที่เข้าข่ายสิทธิ UCEP? ก. ปวดหัว ข. เป็นไข้ ค. หัวใจหยุดเต้น ง. ปวดท้อง'},
        {'id': '4', 'question': 'การผ่าคลอดสามารถใช้สิทธิหลักประกันสุขภาพแห่งชาติได้ในกรณีใด? ก. ทุกกรณี ข. กรณีฉุกเฉินเท่านั้น ค. กรณีที่แพทย์แนะนำ ง. ไม่สามารถใช้ได้'},
        {'id': '5', 'question': 'ผู้ที่ต้องการใส่ฟันปลอมต้องมีอายุเท่าใดขึ้นไป? ก. 18 ปี ข. 20 ปี ค. 25 ปี ง. 30 ปี'}
    ]
    
    # Save to temporary file
    temp_file = "temp_test.csv"
    with open(temp_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'question'])
        writer.writeheader()
        for q in test_questions:
            writer.writerow(q)
    
    try:
        start_time = time.time()
        results = qa_system.process_questions_optimized(temp_file)
        end_time = time.time()
        
        print(f"⏱️  Processing time: {end_time - start_time:.2f} seconds")
        print(f"📊 Questions per second: {len(results)/(end_time - start_time):.2f}")
        
        for result in results:
            print(f"  Q{result['id']}: {result['answer']} (confidence: {result['confidence']:.2f})")
            
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_single_choice_enforcement():
    """Test that only single choices are returned"""
    print("\n✅ Testing single-choice enforcement...")
    
    qa_system = OptimizedHealthcareQA()
    
    # Test cases that might generate multiple answers
    test_cases = [
        "ข้อใดถูกต้องเกี่ยวกับสิทธิหลักประกันสุขภาพ? ก. ครอบคลุมทุกการรักษา ข. ไม่รวมการทำฟัน ค. รวมการผ่าตัด ง. ไม่รวมยา",
        "แผนกใดเปิดตลอด 24 ชั่วโมง? ก. ฉุกเฉิน ข. ศัลยกรรม ค. อายุรกรรม ง. กุมารเวชศาสตร์",
        "ค่าบริการใดไม่รวมในสิทธิหลักประกัน? ก. การตรวจ ข. การรักษา ค. การผ่าตัด ง. การทำฟัน"
    ]
    
    for i, question_text in enumerate(test_cases, 1):
        question, choices = qa_system.parse_question_fast(question_text)
        analysis = qa_system.analyze_question_fast(question)
        context = qa_system.search_context_fast(analysis)
        
        if qa_system.check_llama31():
            result = qa_system.query_llama31_optimized(question, choices, context)
            print(f"  Q{i}: Answer = '{result.answer}' (length: {len(result.answer)})")
            
            # Verify single choice
            if len(result.answer) == 1 and result.answer in ['ก', 'ข', 'ค', 'ง']:
                print(f"    ✅ Single choice enforced")
            else:
                print(f"    ❌ Multiple choices detected: {result.answer}")

async def compare_with_original():
    """Compare performance with original system"""
    print("\n📊 Performance comparison...")
    
    # Check if original system exists
    try:
        from improved_healthcare_qa_system import ImprovedHealthcareQA
        original_available = True
    except ImportError:
        original_available = False
        print("⚠️  Original system not available for comparison")
    
    if not original_available:
        return
    
    # Create small test file for comparison
    test_questions = [
        {'id': '1', 'question': 'สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ? ก. การรักษาพยาบาล ข. การผ่าตัด ค. การทำฟัน ง. การตรวจสุขภาพ'},
        {'id': '2', 'question': 'ค่าบริการเคลือบฟลูออไรด์ชนิดเข้มข้นสูงเฉพาะที่มีอัตราเหมาจ่ายเท่าใดต่อครั้ง? ก. 100 บาท ข. 200 บาท ค. 300 บาท ง. 400 บาท'}
    ]
    
    temp_file = "temp_comparison.csv"
    with open(temp_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'question'])
        writer.writeheader()
        for q in test_questions:
            writer.writerow(q)
    
    try:
        # Test optimized system
        print("Testing optimized system...")
        optimized_system = OptimizedHealthcareQA()
        start_time = time.time()
        optimized_results = optimized_system.process_questions_optimized(temp_file)
        optimized_time = time.time() - start_time
        
        # Test original system
        print("Testing original system...")
        original_system = ImprovedHealthcareQA()
        start_time = time.time()
        original_results = await original_system.process_questions_enhanced(temp_file)
        original_time = time.time() - start_time
        
        print(f"\n📈 Performance Comparison:")
        print(f"  Optimized system: {optimized_time:.2f}s ({len(optimized_results)/optimized_time:.2f} q/s)")
        print(f"  Original system: {original_time:.2f}s ({len(original_results)/original_time:.2f} q/s)")
        print(f"  Speed improvement: {original_time/optimized_time:.1f}x faster")
        
        # Check single-choice enforcement
        optimized_single = sum(1 for r in optimized_results if len(r['answer']) == 1)
        original_single = sum(1 for r in original_results if len(r['answer']) == 1)
        
        print(f"\n✅ Single-choice enforcement:")
        print(f"  Optimized: {optimized_single}/{len(optimized_results)} single choices")
        print(f"  Original: {original_single}/{len(original_results)} single choices")
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

async def main():
    """Main test function"""
    print("🏥 Optimized Healthcare Q&A System - Performance Tests")
    print("=" * 60)
    
    # Run tests
    test_single_question()
    test_performance()
    test_single_choice_enforcement()
    
    # Only run comparison if original system is available
    try:
        await compare_with_original()
    except Exception as e:
        print(f"⚠️  Comparison test skipped: {e}")
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 