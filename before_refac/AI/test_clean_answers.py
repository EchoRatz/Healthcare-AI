#!/usr/bin/env python3
"""
Test the clean answer extraction - should return only choice letters
"""

from thai_qa_processor import ThaiHealthcareQA

def test_answer_extraction():
    """Test that answers are extracted as clean choice letters only"""
    print("🧪 Testing Clean Answer Extraction")
    print("=" * 50)
    print("Expected: Only choice letters like ก, ข, ค, ง")
    print("=" * 50)
    
    # Initialize the system
    qa_system = ThaiHealthcareQA()
    
    # Test questions
    test_questions = [
        "ผมปวดท้องมาก อ้วกด้วย ตอนนี้ตีสองยังมีแผนกไหนเปิดอयู่ไหมครับ? ก. Endocrinology ข. Orthopedics ค. Emergency ง. Internal Medicine",
        "ยา Clopidogrel mg tablet ในปี 2567 จ่ายในอัตราเท่าใดต่อเม็ดในกรณีผู้ป่วยนอก (OP)? ก. 2 บาท/เม็ด ข. 3 บาท/เม็ด ค. 4 บาท/เม็ด ง. 5 บาท/เม็ด",
        "ข้อใดต่อไปนี้เป็นอาการฉุกเฉินวิกฤตที่เข้าข่ายสิทธิ UCEP? ก. เจ็บหน้าอกเฉียบพลันรุนแรง ข. ปวดหัวอย่างรุนแรง ค. มีไข้สูง ง. ปวดท้องเรื้อรัง"
    ]
    
    print("\n🔍 Testing Answer Extraction:")
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Question {i}:")
        print(f"Q: {question[:80]}...")
        
        try:
            # Get answer
            answer = qa_system.answer_question(question, enable_caching=False)
            print(f"✅ Clean Answer: '{answer}'")
            
            # Verify it's clean (should be short and contain only Thai letters or standard phrases)
            if len(answer) <= 20 and any(c in answer for c in 'กขคง'):
                print("✅ Format: GOOD - Clean choice letters")
            elif "ไม่มีคำตอบที่ถูกต้อง" in answer:
                print("✅ Format: GOOD - Standard no-answer response")
            else:
                print("⚠️  Format: May need improvement")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)
    
    # Test the extraction function directly
    print("\n🔧 Testing Direct Answer Extraction:")
    test_responses = [
        'วิเคราะห์คำถาม... คำตอบ: ก, ข',
        'ตอบ: ค',
        '"ง"',
        'ไม่มีคำตอบที่ถูกต้องตามข้อมูล',
        'คำถามยากมาก ตอบ ก',
        'ข้อมูลไม่เพียงพอ'
    ]
    
    for i, response in enumerate(test_responses, 1):
        extracted = qa_system.extract_choice_only(response)
        print(f"Test {i}:")
        print(f"  Input: {response}")
        print(f"  Output: '{extracted}'")
        print()

if __name__ == "__main__":
    test_answer_extraction()