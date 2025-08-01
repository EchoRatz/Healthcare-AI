#!/usr/bin/env python3
"""
Test script to verify the API fix works correctly
"""

import requests
import json

def test_api_endpoint():
    """Test the API endpoint with a sample question"""
    
    # Test question in Thai format with multiple choice
    test_question = {
        "question": "อาการหลักของโรคเบาหวานคืออะไร? ก. ปัสสาวะบ่อย ข. ปวดหัว ค. อ่อนเพลีย ง. ทุกข้อ"
    }
    
    # Test local server (if running)
    try:
        print("Testing local server on port 5001...")
        response = requests.post(
            "http://localhost:5001/eval",
            json=test_question,
            timeout=30
        )
        print(f"Local server response: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("Local server not running on port 5001")
    except Exception as e:
        print(f"Local server error: {e}")
    
    # Test remote server
    try:
        print("\nTesting remote server on 172.16.30.130:5000...")
        response = requests.post(
            "http://172.16.30.130:5000/eval",
            json=test_question,
            timeout=30
        )
        print(f"Remote server response: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Remote server error: {e}")

if __name__ == "__main__":
    test_api_endpoint() 