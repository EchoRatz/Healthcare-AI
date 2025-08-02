#!/usr/bin/env python3
"""
Simple API Test for Healthcare AI
=================================

Tests the single /eval endpoint that matches the specification exactly.
"""

import requests
import json

# API configuration
BASE_URL = "http://localhost:5000"
ENDPOINT = "/eval"

def test_api():
    """Test the API with the exact format from the specification."""
    
    # Test data matching the specification
    test_data = {
        "question": "ผมปวดท้องมาก อ้วกด้วย ไปแผนกไหนดี?ก.Endocrinology ข.Orthopedics ค.Internal Medicine ง.Psychiatry"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("🚀 Testing Healthcare AI API")
    print("=" * 50)
    print(f"URL: {BASE_URL}{ENDPOINT}")
    print(f"Method: POST")
    print(f"Headers: {headers}")
    print(f"Request Body: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    print()
    
    try:
        # Make the API call
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json=test_data,
            headers=headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Response: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # Validate response format
            if "answer" in result and "reason" in result:
                print("\n✅ Response format is correct!")
                print(f"Answer: {result['answer']}")
                print(f"Reason: {result['reason']}")
            else:
                print("❌ Response format is incorrect!")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("   Make sure to start the server with: python api_server.py")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_multiple_questions():
    """Test multiple healthcare questions."""
    
    questions = [
        "ผมปวดท้องมาก อ้วกด้วย ไปแผนกไหนดี?ก.Endocrinology ข.Orthopedics ค.Internal Medicine ง.Psychiatry",
        "ผู้ป่วยมีสิทธิ์รับบริการอะไรบ้างในระบบหลักประกันสุขภาพแห่งชาติ?ก.ตรวจสุขภาพฟรี ข.ผ่าตัด 1000 บาท ค.ยา 50 บาท/เม็ด ง.ไม่มีสิทธิ์",
        "ค่าใช้จ่ายในการรักษาพยาบาลทั่วไปเท่าไหร่?ก.ฟรี ข.30บาท ค.100บาท ง.500บาท",
        "การรักษาฉุกเฉินครอบคลุมอะไรบ้าง?ก.อุบัติเหตุ ข.หัวใจวาย ค.หมดสติ ง.ทุกข้อ"
    ]
    
    print("\n🏥 Testing Multiple Questions")
    print("=" * 50)
    
    for i, question in enumerate(questions, 1):
        print(f"\nQuestion {i}: {question[:50]}...")
        
        try:
            response = requests.post(
                f"{BASE_URL}{ENDPOINT}",
                json={"question": question},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Answer: {result['answer']}")
                print(f"   Reason: {result['reason'][:100]}...")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    # Test single question
    test_api()
    
    # Test multiple questions
    test_multiple_questions() 