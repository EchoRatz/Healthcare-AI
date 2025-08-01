"""
Test script for the Thai Healthcare Q&A System
"""

from thai_qa_processor import ThaiHealthcareQA


def test_example_question():
    """Test with the example question provided"""
    
    example_question = """ผมปวดท้องมาก อ้วกด้วย ตอนนี้ตีสองยังมีแผนกไหนเปิดอยู่ไหมครับ?
ก. Endocrinology
ข. Orthopedics
ค. Emergency
ง. Internal Medicine"""

    print("=== ทดสอบระบบ Thai Healthcare Q&A ===\n")
    
    try:
        # Initialize the Q&A system
        print("กำลังเริ่มต้นระบบ...")
        qa_system = ThaiHealthcareQA()
        
        print("ระบบพร้อมแล้ว!\n")
        
        # Test the example question
        print("คำถามทดสอบ:")
        print(example_question)
        print("\n" + "="*60)
        print("กำลังประมวลผล...\n")
        
        answer = qa_system.answer_question(example_question)
        
        print("คำตอบ:")
        print(answer)
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        print("\nโปรดตรวจสอบ:")
        print("1. Ollama กำลังทำงานอยู่")
        print("2. โมเดล llama3.2 และ mxbai-embed-large ถูกติดตั้งแล้ว")
        print("3. ไฟล์ direct_extraction_corrected.txt มีอยู่ในโฟลเดอร์ results_doc/")


def test_multiple_questions():
    """Test with multiple healthcare questions"""
    
    questions = [
        """นโยบายปฐมภูมิไปที่ไหนก็ได้ ใช้ได้อย่างไร?
ก. ต้องเข้ารับการรักษากรณีผู้ป่วยนอก (OPD)
ข. ต้องไม่ใช้กรณีรักษาต่อเนื่อง (นัดติดตามอาการ)
ค. ใช้ได้ทั้งสองข้อ
ง. ไม่มีเงื่อนไขใดๆ""",

        """สิทธิหลักประกันสุขภาพแห่งชาติคุ้มครองการใส่ฟันเทียมแบบไหน?
ก. แบบซี่เท่านั้น
ข. แบบทั้งปากเท่านั้น
ค. ทั้งแบบซี่และแบบทั้งปาก
ง. ไม่คุ้มครองการใส่ฟันเทียม""",

        """ผู้ป่วยมีสิทธิเปลี่ยนหน่วยบริการประจำได้กี่ครั้งต่อปี?
ก. 2 ครั้ง
ข. 3 ครั้ง  
ค. 4 ครั้ง
ง. ไม่จำกัด"""
    ]
    
    print("\n=== ทดสอบคำถามหลายข้อ ===\n")
    
    try:
        qa_system = ThaiHealthcareQA()
        
        for i, question in enumerate(questions, 1):
            print(f"คำถามที่ {i}:")
            print(question)
            print("\n" + "-"*50)
            
            answer = qa_system.answer_question(question)
            print("คำตอบ:")
            print(answer)
            print("\n" + "="*60 + "\n")
            
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")


if __name__ == "__main__":
    # Run the basic test first
    test_example_question()
    
    # Ask if user wants to run more tests
    print("\nต้องการทดสอบคำถามเพิ่มเติมหรือไม่? (y/n)")
    response = input().strip().lower()
    
    if response in ['y', 'yes', 'ใช่']:
        test_multiple_questions()
    
    print("\nการทดสอบเสร็จสิ้น!")