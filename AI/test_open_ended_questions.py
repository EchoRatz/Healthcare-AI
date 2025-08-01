#!/usr/bin/env python3
"""
Test script to demonstrate open-ended question answering with cached knowledge
"""

from thai_qa_processor import ThaiHealthcareQA

def test_open_ended_questions():
    """Test the system's ability to answer open-ended questions using cached knowledge"""
    print("🧪 Testing Open-Ended Questions with Cached Knowledge")
    print("=" * 60)
    
    # Initialize the system
    qa_system = ThaiHealthcareQA()
    
    # Show current cache
    print("📊 Current Knowledge Cache:")
    qa_system.show_cache_stats()
    
    print("\n🎯 Testing Open-Ended Questions:")
    print("-" * 40)
    
    # Test questions that should use cached knowledge
    test_questions = [
        "เคลือบฟลูออไรด์ราคาเท่าไร?",
        "UCEP ครอบคลุมอาการไหนบ้าง?",
        "แผนกฉุกเฉินเปิดตลอดเวลาไหม?",
        "ค่าบริการทันตกรรมเท่าไหร่?",
        "สิทธิ 30 บาทได้อะไรบ้าง?",
        "โรงพยาบาลมีแผนกไหนเปิด 24 ชั่วโมง?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Question {i}:")
        print(f"Q: {question}")
        
        try:
            # Answer the question
            answer = qa_system.answer_question(question, enable_caching=False)
            
            # Show answer
            print(f"A: {answer}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)
    
    print("\n✅ Open-ended question testing complete!")

if __name__ == "__main__":
    test_open_ended_questions()