#!/usr/bin/env python3
"""
Test Enhanced Thai Healthcare Q&A System
Compare different AI approaches and validate improvements
"""

import os
import sys
import time
import json
import numpy as np
from typing import Dict, List

def test_parsing():
    """Test question parsing capability"""
    print("🧪 Testing Question Parsing")
    print("-" * 40)
    
    try:
        from enhanced_thai_qa_system import EnhancedThaiHealthcareQA
        
        # Initialize with minimal setup
        knowledge_files = [
            'Healthcare-AI-Refactored/src/infrastructure/results_doc/direct_extraction_corrected.txt'
        ]
        
        if not os.path.exists(knowledge_files[0]):
            print("❌ Knowledge file not found for testing")
            return False
        
        qa_system = EnhancedThaiHealthcareQA(knowledge_files)
        
        # Test questions
        test_questions = [
            "ผมปวดท้องมาก อ้วกด้วย ตอนนี้ตีสองยังมีแผนกไหนเปิดอยู่ไหมครับ?  ก. Endocrinology ข. Orthopedics ค. Emergency ง. Internal Medicine",
            "ยา Clopidogrel mg tablet ในปี 2567 จ่ายในอัตราเท่าใดต่อเม็ดในกรณีผู้ป่วยนอก (OP)?  ก. 2 บาท/เม็ด ข. 3 บาท/เม็ด ค. 4 บาท/เม็ด ง. 5 บาท/เม็ด"
        ]
        
        for i, test_q in enumerate(test_questions, 1):
            print(f"\n📝 Test {i}:")
            question, choices = qa_system.parse_question(test_q)
            print(f"Question: {question[:50]}...")
            print(f"Choices extracted: {len(choices)}")
            for label, text in choices.items():
                print(f"  {label}. {text[:30]}...")
        
        print("\n✅ Question parsing test passed")
        return True
        
    except Exception as e:
        print(f"❌ Question parsing test failed: {e}")
        return False

def test_ai_capabilities():
    """Test different AI model capabilities"""
    print("\n🧠 Testing AI Model Capabilities")
    print("-" * 40)
    
    capabilities = {}
    
    # Test Sentence Transformers
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('intfloat/multilingual-e5-large')
        test_texts = ["ทดสอบระบบ", "test system"]
        embeddings = model.encode(test_texts)
        capabilities["Sentence Transformers"] = True
        print("✅ Sentence Transformers: Available")
        print(f"   Model: multilingual-e5-large")
        print(f"   Embedding dimension: {embeddings.shape[1]}")
    except Exception as e:
        capabilities["Sentence Transformers"] = False
        print(f"❌ Sentence Transformers: Not available ({str(e)[:50]}...)")
    
    # Test FAISS
    try:
        import faiss
        # Test with small index
        dimension = 512
        index = faiss.IndexFlatIP(dimension)
        test_vectors = [[0.1] * dimension, [0.2] * dimension]
        index.add(np.array(test_vectors, dtype='float32'))
        capabilities["FAISS"] = True
        print("✅ FAISS: Available")
    except Exception as e:
        capabilities["FAISS"] = False
        print(f"❌ FAISS: Not available ({str(e)[:50]}...)")
    
    # Test OpenAI
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            capabilities["OpenAI"] = True
            print("✅ OpenAI: API key configured")
        except Exception as e:
            capabilities["OpenAI"] = False
            print(f"❌ OpenAI: Error ({str(e)[:50]}...)")
    else:
        capabilities["OpenAI"] = False
        print("❌ OpenAI: No API key (set OPENAI_API_KEY)")
    
    return capabilities

def test_processing_speed():
    """Test processing speed with different methods"""
    print("\n⚡ Testing Processing Speed")
    print("-" * 40)
    
    try:
        # Test with original system
        print("Testing original system...")
        from thai_healthcare_qa_system import ThaiHealthcareQASystem
        
        knowledge_files = [
            'Healthcare-AI-Refactored/src/infrastructure/results_doc/direct_extraction_corrected.txt',
            'Healthcare-AI-Refactored/src/infrastructure/results_doc2/direct_extraction_corrected.txt',
            'Healthcare-AI-Refactored/src/infrastructure/results_doc3/direct_extraction_corrected.txt'
        ]
        
        # Check if files exist
        if not all(os.path.exists(f) for f in knowledge_files):
            print("❌ Knowledge files not found for speed test")
            return
        
        start_time = time.time()
        original_system = ThaiHealthcareQASystem(knowledge_files, memory_file="speed_test_memory.json")
        original_init_time = time.time() - start_time
        
        # Test enhanced system
        print("Testing enhanced system...")
        from enhanced_thai_qa_system import EnhancedThaiHealthcareQA
        
        start_time = time.time()
        enhanced_system = EnhancedThaiHealthcareQA(knowledge_files)
        enhanced_init_time = time.time() - start_time
        
        print(f"\n📊 Initialization Times:")
        print(f"  Original system: {original_init_time:.2f} seconds")
        print(f"  Enhanced system: {enhanced_init_time:.2f} seconds")
        
        # Test single question processing
        test_question = "ผมปวดท้องมาก อ้วกด้วย ตอนนี้ตีสองยังมีแผนกไหนเปิดอยู่ไหมครับ?  ก. Endocrinology ข. Orthopedics ค. Emergency ง. Internal Medicine"
        
        # Original system
        question, choices = original_system.parse_question(test_question)
        start_time = time.time()
        original_result = original_system._chain_of_thought_reasoning(question, choices)
        original_question_time = time.time() - start_time
        
        # Enhanced system  
        question, choices = enhanced_system.parse_question(test_question)
        start_time = time.time()
        enhanced_result = enhanced_system._ensemble_prediction(question, choices)
        enhanced_question_time = time.time() - start_time
        
        print(f"\n📊 Single Question Processing:")
        print(f"  Original: {original_question_time:.3f} seconds")
        print(f"  Enhanced: {enhanced_question_time:.3f} seconds")
        
        print(f"\n🎯 Prediction Comparison:")
        print(f"  Original: {original_result.predicted_answers} (conf: {original_result.confidence:.3f})")
        print(f"  Enhanced: {enhanced_result.predicted_answers} (conf: {enhanced_result.confidence:.3f})")
        
        # Clean up test files
        if os.path.exists("speed_test_memory.json"):
            os.remove("speed_test_memory.json")
        
    except Exception as e:
        print(f"❌ Speed test failed: {e}")

def test_accuracy_comparison():
    """Compare accuracy between systems on sample questions"""
    print("\n🎯 Testing Accuracy Comparison")
    print("-" * 40)
    
    # Sample questions with expected answers (if known)
    test_cases = [
        {
            "question": "ผมปวดท้องมาก อ้วกด้วย ตอนนี้ตีสองยังมีแผนกไหนเปิดอยู่ไหมครับ?  ก. Endocrinology ข. Orthopedics ค. Emergency ง. Internal Medicine",
            "expected": ["ค"],  # Emergency seems most appropriate
            "reasoning": "Emergency department for acute symptoms"
        },
        {
            "question": "ข้อใดต่อไปนี้เป็นอาการฉุกเฉินวิกฤตที่เข้าข่ายสิทธิ UCEP?  ก. เจ็บหน้าอกเฉียบพลันรุนแรง ข. ปวดหัวอย่างรุนแรง ค. มีไข้สูง ง. ปวดท้องเรื้อรัง",
            "expected": ["ก"],  # Acute severe chest pain is emergency
            "reasoning": "Acute severe chest pain is critical emergency"
        }
    ]
    
    try:
        knowledge_files = [
            'Healthcare-AI-Refactored/src/infrastructure/results_doc/direct_extraction_corrected.txt',
            'Healthcare-AI-Refactored/src/infrastructure/results_doc2/direct_extraction_corrected.txt',
            'Healthcare-AI-Refactored/src/infrastructure/results_doc3/direct_extraction_corrected.txt'
        ]
        
        if not all(os.path.exists(f) for f in knowledge_files):
            print("❌ Knowledge files not found for accuracy test")
            return
        
        # Initialize systems
        from thai_healthcare_qa_system import ThaiHealthcareQASystem
        from enhanced_thai_qa_system import EnhancedThaiHealthcareQA
        
        original_system = ThaiHealthcareQASystem(knowledge_files, memory_file="accuracy_test_memory.json")
        enhanced_system = EnhancedThaiHealthcareQA(knowledge_files)
        
        print(f"Testing {len(test_cases)} sample questions...")
        
        original_correct = 0
        enhanced_correct = 0
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test Case {i}:")
            print(f"Question: {test_case['question'][:60]}...")
            print(f"Expected: {test_case['expected']} ({test_case['reasoning']})")
            
            question, choices = original_system.parse_question(test_case['question'])
            
            # Original system
            original_result = original_system._chain_of_thought_reasoning(question, choices)
            original_match = any(ans in test_case['expected'] for ans in original_result.predicted_answers)
            if original_match:
                original_correct += 1
            
            # Enhanced system
            enhanced_result = enhanced_system._ensemble_prediction(question, choices)
            enhanced_match = any(ans in test_case['expected'] for ans in enhanced_result.predicted_answers)
            if enhanced_match:
                enhanced_correct += 1
            
            print(f"Original: {original_result.predicted_answers} {'✅' if original_match else '❌'} (conf: {original_result.confidence:.3f})")
            print(f"Enhanced: {enhanced_result.predicted_answers} {'✅' if enhanced_match else '❌'} (conf: {enhanced_result.confidence:.3f})")
        
        print(f"\n📊 Accuracy Results:")
        print(f"  Original system: {original_correct}/{len(test_cases)} ({original_correct/len(test_cases)*100:.1f}%)")
        print(f"  Enhanced system: {enhanced_correct}/{len(test_cases)} ({enhanced_correct/len(test_cases)*100:.1f}%)")
        
        if enhanced_correct > original_correct:
            print("🎉 Enhanced system shows improvement!")
        elif enhanced_correct == original_correct:
            print("📊 Systems perform similarly on this sample")
        else:
            print("⚠️  Enhanced system needs tuning")
        
        # Clean up
        if os.path.exists("accuracy_test_memory.json"):
            os.remove("accuracy_test_memory.json")
            
    except Exception as e:
        print(f"❌ Accuracy test failed: {e}")

def main():
    """Run all enhanced system tests"""
    print("🚀 Enhanced Thai Healthcare Q&A System - Testing Suite")
    print("=" * 60)
    
    try:
        # Test 1: Basic parsing
        parsing_success = test_parsing()
        
        # Test 2: AI capabilities
        capabilities = test_ai_capabilities()
        
        # Test 3: Processing speed (if parsing works)
        if parsing_success:
            test_processing_speed()
        
        # Test 4: Accuracy comparison (if parsing works)
        if parsing_success:
            test_accuracy_comparison()
        
        # Summary
        print(f"\n📋 Test Summary:")
        print(f"=" * 40)
        print(f"✅ Question parsing: {'✅' if parsing_success else '❌'}")
        print(f"🧠 AI Capabilities:")
        for capability, available in capabilities.items():
            print(f"   {capability}: {'✅' if available else '❌'}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if not capabilities.get("Sentence Transformers", False):
            print("  📦 Install sentence-transformers for better embeddings")
        if not capabilities.get("FAISS", False):
            print("  📦 Install faiss-cpu for faster vector search")
        if not capabilities.get("OpenAI", False):
            print("  🔑 Set OPENAI_API_KEY for highest accuracy")
        
        print(f"\n🎯 Ready to run enhanced system:")
        print(f"   python enhanced_thai_qa_system.py")
        
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()