#!/usr/bin/env python3
"""
Healthcare AI API Test Examples
===============================

This script provides examples of how to use the Healthcare AI API endpoints.
Run this after starting the API server with: python api_server.py
"""

import requests
import json
import time
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint."""
    print("🏥 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Status: {data['status']}")
            print(f"   Model Available: {data['model_available']}")
            print(f"   Knowledge Base Loaded: {data['knowledge_base_loaded']}")
            print(f"   Vector Store Ready: {data['vector_store_ready']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_system_status():
    """Test the system status endpoint."""
    print("\n📊 Testing System Status...")
    try:
        response = requests.get(f"{BASE_URL}/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ LLM Status: {data['llm_status']}")
            print(f"   Vector Store Status: {data['vector_store_status']}")
            print(f"   Knowledge Base Status: {data['knowledge_base_status']}")
            print(f"   Model Name: {data['model_name']}")
            print(f"   Documents Loaded: {data['documents_loaded']}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False

def test_single_question():
    """Test processing a single question."""
    print("\n❓ Testing Single Question...")
    
    question_data = {
        "question": "ผู้ป่วยมีสิทธิ์รับบริการอะไรบ้างในระบบหลักประกันสุขภาพแห่งชาติ?",
        "context_size": 3
    }
    
    try:
        response = requests.post(f"{BASE_URL}/question", json=question_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Question: {data['question']}")
            print(f"   Answer: {data['answer']}")
            print(f"   Confidence: {data['confidence']:.3f}")
            print(f"   Processing Time: {data['processing_time']:.3f}s")
            print(f"   Model Used: {data['model_used']}")
            print(f"   Sources: {len(data['sources'])} documents")
            return True
        else:
            print(f"❌ Question processing failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Question processing error: {e}")
        return False

def test_batch_questions():
    """Test processing multiple questions in batch."""
    print("\n📝 Testing Batch Questions...")
    
    questions_data = {
        "questions": [
            "ผู้ป่วยมีสิทธิ์รับบริการอะไรบ้างในระบบหลักประกันสุขภาพแห่งชาติ?",
            "ค่าใช้จ่ายในการรักษาพยาบาลเท่าไหร่?",
            "การรักษาฉุกเฉินครอบคลุมอะไรบ้าง?",
            "สิทธิ์บัตรทองสำหรับผู้สูงอายุมีอะไรบ้าง?"
        ],
        "context_size": 2
    }
    
    try:
        response = requests.post(f"{BASE_URL}/batch", json=questions_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Total Questions: {data['total_questions']}")
            print(f"   Successful: {data['successful_questions']}")
            print(f"   Failed: {data['failed_questions']}")
            print(f"   Total Time: {data['total_processing_time']:.3f}s")
            print(f"   Average Confidence: {data['average_confidence']:.3f}")
            
            print("\n   Results:")
            for i, result in enumerate(data['results'], 1):
                print(f"   {i}. {result['question'][:50]}...")
                print(f"      Answer: {result['answer']}")
                print(f"      Confidence: {result['confidence']:.3f}")
            return True
        else:
            print(f"❌ Batch processing failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Batch processing error: {e}")
        return False

def test_available_models():
    """Test listing available models."""
    print("\n🤖 Testing Available Models...")
    try:
        response = requests.get(f"{BASE_URL}/models")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Available Models: {data['models']}")
            return True
        else:
            print(f"❌ Model listing failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Model listing error: {e}")
        return False

def test_reload_system():
    """Test reloading the system."""
    print("\n🔄 Testing System Reload...")
    try:
        response = requests.post(f"{BASE_URL}/reload")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
            return True
        else:
            print(f"❌ System reload failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ System reload error: {e}")
        return False

def test_specific_healthcare_questions():
    """Test specific healthcare-related questions."""
    print("\n🏥 Testing Healthcare-Specific Questions...")
    
    healthcare_questions = [
        {
            "question": "ผู้ป่วยอายุ 60 ปี มีสิทธิ์รับบริการอะไรบ้าง?",
            "expected_keywords": ["ผู้สูงอายุ", "บัตรทอง", "60ปี"]
        },
        {
            "question": "ค่าใช้จ่ายในการรักษาพยาบาลทั่วไปเท่าไหร่?",
            "expected_keywords": ["ค่าใช้จ่าย", "30บาท", "รักษา"]
        },
        {
            "question": "การรักษาฉุกเฉินครอบคลุมอะไรบ้าง?",
            "expected_keywords": ["ฉุกเฉิน", "UCEP", "วิกฤต"]
        },
        {
            "question": "สิทธิ์ประกันสังคมสำหรับการรักษาพยาบาลมีอะไรบ้าง?",
            "expected_keywords": ["ประกันสังคม", "ขสมก", "สวัสดิการ"]
        }
    ]
    
    for i, q_data in enumerate(healthcare_questions, 1):
        print(f"\n   Question {i}: {q_data['question']}")
        try:
            response = requests.post(f"{BASE_URL}/question", json={
                "question": q_data['question'],
                "context_size": 3
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Answer: {data['answer']}")
                print(f"      Confidence: {data['confidence']:.3f}")
                print(f"      Sources: {len(data['sources'])} documents")
            else:
                print(f"      ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")

def test_error_handling():
    """Test error handling with invalid requests."""
    print("\n⚠️ Testing Error Handling...")
    
    # Test with empty question
    try:
        response = requests.post(f"{BASE_URL}/question", json={"question": ""})
        print(f"   Empty question: {response.status_code}")
    except Exception as e:
        print(f"   Empty question error: {e}")
    
    # Test with invalid endpoint
    try:
        response = requests.get(f"{BASE_URL}/invalid_endpoint")
        print(f"   Invalid endpoint: {response.status_code}")
    except Exception as e:
        print(f"   Invalid endpoint error: {e}")

def main():
    """Run all API tests."""
    print("🚀 Healthcare AI API Test Suite")
    print("=" * 50)
    
    # Check if server is running
    print("🔍 Checking if API server is running...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running!")
        else:
            print("❌ API server is not responding correctly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API server: {e}")
        print("   Make sure to start the server with: python api_server.py")
        return
    
    # Run tests
    tests = [
        test_health_check,
        test_system_status,
        test_single_question,
        test_batch_questions,
        test_available_models,
        test_specific_healthcare_questions,
        test_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the API server configuration.")

if __name__ == "__main__":
    main() 