#!/usr/bin/env python3
"""
Test script for High-Accuracy Healthcare Q&A System
==================================================

This script tests the high-accuracy system with sample questions to validate
its performance and identify areas for improvement.
"""

import asyncio
import csv
from high_accuracy_healthcare_qa_system import HighAccuracyHealthcareQA

async def test_system():
    """Test the high-accuracy system with sample questions"""
    
    print("🧪 TESTING HIGH-ACCURACY HEALTHCARE Q&A SYSTEM")
    print("=" * 50)
    
    # Initialize system
    qa_system = HighAccuracyHealthcareQA()
    
    # Test questions with expected answers
    test_questions = [
        {
            "id": "test_1",
            "question": "ผมปวดท้องมาก อ้วกด้วย ตอนนี้ตีสองยังมีแผนกไหนเปิดอยู่ไหมครับ? ก. Endocrinology ข. Orthopedics ค. Emergency ง. Internal Medicine",
            "expected": "ค",  # Emergency should be open 24/7
            "type": "emergency"
        },
        {
            "id": "test_2", 
            "question": "สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ? ก. สิทธิหลักประกันสุขภาพแห่งชาติ ข. สิทธิบัตรทอง ค. สิทธิ 30 บาทรักษาทุกโรค ง. ไม่มีข้อใดถูกต้อง",
            "expected": "ง",  # All are part of the system
            "type": "exclusion"
        },
        {
            "id": "test_3",
            "question": "การผ่าคลอดสามารถใช้สิทธิหลักประกันสุขภาพแห่งชาติได้ในกรณีใด? ก. เมื่อมารดาขอให้แพทย์ผ่าคลอดเพราะกลัวเจ็บครรภ์ ข. เมื่อแพทย์ประเมินและมีข้อบ่งชี้ที่เหมาะสม ค. เมื่อมารดาต้องการเลือกวันคลอดเอง ง. เมื่อไม่มีข้อบ่งชี้ของแพทย์",
            "expected": "ข",  # Medical indication required
            "type": "procedure"
        },
        {
            "id": "test_4",
            "question": "คนไข้ชายอายุ 50 ปี มีอาการปวดหลัง ชาปลายมือ ปวดลงขา ควรพบหมอแผนกไหน? ก. Neurology ข. Orthopedics ค. Cardiology ง. Nephrology",
            "expected": "ข",  # Orthopedics for back pain
            "type": "department"
        },
        {
            "id": "test_5",
            "question": "การตรวจหาการติดเชื้อเอชไอวีด้วยตนเอง (HIVSST) สามารถทำได้ไม่เกินกี่ครั้งต่อวัน? ก. 1 ครั้ง ข. 2 ครั้ง ค. 3 ครั้ง ง. ไม่จำกัด",
            "expected": "ก",  # Usually limited to 1 per day
            "type": "factual"
        }
    ]
    
    print(f"📝 Testing {len(test_questions)} sample questions...")
    
    # Load knowledge base
    qa_system.load_knowledge_base()
    
    results = []
    correct = 0
    
    for test_q in test_questions:
        print(f"\n🔍 Testing Question {test_q['id']}: {test_q['type']}")
        print(f"Question: {test_q['question'][:100]}...")
        
        # Parse question
        question, choices = qa_system.parse_question_enhanced(test_q['question'])
        
        # Analyze question
        question_analysis = qa_system.analyze_question_advanced(question)
        print(f"  Analysis: {question_analysis.primary_type} (confidence: {question_analysis.confidence:.2f})")
        
        # Search context
        context_matches = qa_system.search_context_semantic(question_analysis)
        print(f"  Context matches: {len(context_matches)} (best score: {max([m.relevance_score for m in context_matches]) if context_matches else 0:.2f})")
        
        # Query LLM (if available)
        if qa_system.check_llama31():
            answers, confidence = qa_system.query_llama31_optimized(question, choices, context_matches, question_analysis)
            print(f"  LLM Answer: {answers} (confidence: {confidence:.2f})")
        else:
            print("  ⚠️  LLM not available - skipping LLM query")
            answers, confidence = [], 0.0
        
        # Validate answer
        answer_analysis = qa_system.validate_answer_advanced(question, choices, answers, question_analysis)
        print(f"  Validation: {answer_analysis.reasoning}")
        
        # Check correctness
        final_answer = ",".join(answer_analysis.selected_answers) if answer_analysis.selected_answers else "ง"
        is_correct = final_answer == test_q['expected']
        if is_correct:
            correct += 1
        
        print(f"  Final Answer: {final_answer} | Expected: {test_q['expected']} | {'✅' if is_correct else '❌'}")
        
        results.append({
            'id': test_q['id'],
            'type': test_q['type'],
            'expected': test_q['expected'],
            'actual': final_answer,
            'correct': is_correct,
            'confidence': confidence,
            'validation_passed': answer_analysis.policy_validation,
            'context_relevance': max([m.relevance_score for m in context_matches]) if context_matches else 0.0
        })
    
    # Print summary
    accuracy = correct / len(test_questions) * 100
    print(f"\n📊 TEST RESULTS SUMMARY:")
    print(f"  Total questions: {len(test_questions)}")
    print(f"  Correct answers: {correct}")
    print(f"  Accuracy: {accuracy:.1f}%")
    
    # Breakdown by question type
    type_results = {}
    for result in results:
        qtype = result['type']
        if qtype not in type_results:
            type_results[qtype] = {'total': 0, 'correct': 0}
        type_results[qtype]['total'] += 1
        if result['correct']:
            type_results[qtype]['correct'] += 1
    
    print(f"\n📋 Results by Question Type:")
    for qtype, stats in type_results.items():
        type_accuracy = stats['correct'] / stats['total'] * 100
        print(f"  {qtype}: {stats['correct']}/{stats['total']} ({type_accuracy:.1f}%)")
    
    # Average confidence and context relevance
    avg_confidence = sum(r['confidence'] for r in results) / len(results)
    avg_context_relevance = sum(r['context_relevance'] for r in results) / len(results)
    validation_rate = sum(1 for r in results if r['validation_passed']) / len(results) * 100
    
    print(f"\n📈 Performance Metrics:")
    print(f"  Average confidence: {avg_confidence:.3f}")
    print(f"  Average context relevance: {avg_context_relevance:.3f}")
    print(f"  Validation pass rate: {validation_rate:.1f}%")
    
    return results, accuracy

async def main():
    """Main test function"""
    try:
        results, accuracy = await test_system()
        
        if accuracy >= 75:
            print(f"\n🎉 SUCCESS! System achieved {accuracy:.1f}% accuracy (target: 75%)")
        else:
            print(f"\n⚠️  System achieved {accuracy:.1f}% accuracy (target: 75%) - needs improvement")
        
        # Save test results
        with open('test_results.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'type', 'expected', 'actual', 'correct', 'confidence', 'validation_passed', 'context_relevance'])
            writer.writeheader()
            for result in results:
                writer.writerow(result)
        
        print(f"💾 Test results saved to: test_results.csv")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 