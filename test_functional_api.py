#!/usr/bin/env python3
"""
Test Functional Healthcare AI API
=================================

Tests the fully functional API that connects to LLM.
"""

import requests
import json
import time

# API configuration
BASE_URL = "http://localhost:5000"
ENDPOINT = "/eval"

def test_health_check():
    """Test the health check endpoint."""
    print("🏥 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Status: {data['status']}")
            print(f"   System Ready: {data['system_ready']}")
            print(f"   LLM Available: {data['llm_available']}")
            print(f"   Knowledge Base Loaded: {data['knowledge_base_loaded']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_api_evaluation(question):
    """Test the API evaluation endpoint."""
    print(f"\n🔍 Testing API with question: {question[:100]}...")
    
    test_data = {
        "question": question
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}{ENDPOINT}", 
                               json=test_data, 
                               headers=headers)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response received in {end_time - start_time:.2f}s")
            print(f"   Answer: {data['answer']}")
            print(f"   Reason: {data['reason']}")
            print(f"   Confidence: {data.get('confidence', 'N/A')}")
            print(f"   LLM Available: {data['llm_available']}")
            return True
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API call error: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Testing Functional Healthcare AI API")
    print("=" * 50)
    
    # Test health check
    if not test_health_check():
        print("❌ Health check failed - API may not be running")
        return
    
    # Test questions
    test_questions = [
        "ผู้ป่วยมีสิทธิ์รับบริการอะไรบ้างในระบบหลักประกันสุขภาพแห่งชาติ?ก.ตรวจสุขภาพฟรี ข.ผ่าตัด 1000 บาท ค.ยา 50 บาท/เม็ด ง.ไม่มีสิทธิ์",
        "ผมปวดท้องมาก อ้วกด้วย ไปแผนกไหนดี?ก.Endocrinology ข.Orthopedics ค.Internal Medicine ง.Psychiatry",
        "ค่าใช้จ่ายในการรักษาพยาบาลทั่วไปเท่าไหร่?ก.ฟรี ข.30บาท ค.100บาท ง.500บาท"
    ]
    
    success_count = 0
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}/{len(test_questions)}")
        if test_api_evaluation(question):
            success_count += 1
        time.sleep(1)  # Small delay between requests
    
    print(f"\n🎉 Test Results: {success_count}/{len(test_questions)} successful")
    
    if success_count == len(test_questions):
        print("✅ All tests passed! API is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the API server.")

if __name__ == "__main__":
    main() 