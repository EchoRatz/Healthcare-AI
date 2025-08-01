#!/usr/bin/env python3
"""
Quick Demo of Thai Healthcare Q&A System
Demonstrates the system with sample questions
"""

import os
import sys

def check_demo_requirements():
    """Check if demo can run"""
    required_files = [
        'Healthcare-AI-Refactored/src/infrastructure/results_doc/direct_extraction_corrected.txt',
        'Healthcare-AI-Refactored/src/infrastructure/results_doc2/direct_extraction_corrected.txt', 
        'Healthcare-AI-Refactored/src/infrastructure/results_doc3/direct_extraction_corrected.txt'
    ]
    
    missing = [f for f in required_files if not os.path.exists(f)]
    if missing:
        print(f"❌ Missing demo files: {missing}")
        return False
    return True

def demo_thai_qa():
    """Demonstrate Thai Healthcare Q&A with sample questions"""
    print("🏥 Thai Healthcare Q&A System - Demo")
    print("=" * 50)
    
    try:
        from thai_healthcare_qa_system import ThaiHealthcareQASystem
        
        # Initialize system
        print("🔧 Initializing system...")
        knowledge_files = [
            'Healthcare-AI-Refactored/src/infrastructure/results_doc/direct_extraction_corrected.txt',
            'Healthcare-AI-Refactored/src/infrastructure/results_doc2/direct_extraction_corrected.txt',
            'Healthcare-AI-Refactored/src/infrastructure/results_doc3/direct_extraction_corrected.txt'
        ]
        
        qa_system = ThaiHealthcareQASystem(knowledge_files, memory_file="demo_memory.json")
        print("✅ System initialized!")
        
        # Demo questions (from the test file)
        demo_questions = [
            {
                'id': 1,
                'question': 'ผมปวดท้องมาก อ้วกด้วย ตอนนี้ตีสองยังมีแผนกไหนเปิดอยู่ไหมครับ?  ก. Endocrinology ข. Orthopedics ค. Emergency ง. Internal Medicine'
            },
            {
                'id': 2, 
                'question': 'ยา Clopidogrel mg tablet ในปี 2567 จ่ายในอัตราเท่าใดต่อเม็ดในกรณีผู้ป่วยนอก (OP)?  ก. 2 บาท/เม็ด ข. 3 บาท/เม็ด ค. 4 บาท/เม็ด ง. 5 บาท/เม็ด'
            },
            {
                'id': 3,
                'question': 'ข้อใดต่อไปนี้เป็นอาการฉุกเฉินวิกฤตที่เข้าข่ายสิทธิ UCEP?  ก. เจ็บหน้าอกเฉียบพลันรุนแรง ข. ปวดหัวอย่างรุนแรง ค. มีไข้สูง ง. ปวดท้องเรื้อรัง'
            }
        ]
        
        print(f"\n🧠 Processing {len(demo_questions)} demo questions:")
        print("-" * 50)
        
        results = []
        for demo_q in demo_questions:
            question, choices = qa_system.parse_question(demo_q['question'])
            
            print(f"\n🔍 Question {demo_q['id']}:")
            print(f"❓ {question}")
            print("📋 Choices:")
            for choice_label, choice_text in choices.items():
                print(f"   {choice_label}. {choice_text}")
            
            # Get prediction
            result = qa_system._chain_of_thought_reasoning(question, choices)
            result.id = demo_q['id']
            results.append(result)
            
            # Show result
            print(f"🎯 Prediction: {', '.join(result.predicted_answers)}")
            print(f"📊 Confidence: {result.confidence:.3f}")
            
            if result.evidence:
                print(f"🔍 Evidence: {result.evidence[0][:100]}...")
            
            print(f"🧠 Reasoning: {result.reasoning_chain[-1]}")
        
        # Show submission format
        print(f"\n📄 Submission Format:")
        print("id,answer")
        for result in results:
            answer_str = ','.join(result.predicted_answers)
            print(f'{result.id},"{answer_str}"')
        
        print(f"\n✅ Demo completed successfully!")
        print("Ready to run full processing with: python run_thai_qa.py")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install required packages: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run the demo"""
    if not check_demo_requirements():
        print("Please ensure all healthcare document files are available.")
        sys.exit(1)
    
    print("🚀 Starting Thai Healthcare Q&A Demo...")
    demo_thai_qa()

if __name__ == "__main__":
    main()