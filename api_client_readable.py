#!/usr/bin/env python3
"""
Healthcare AI API Client - Readable Output
==========================================

This script makes API responses more readable by:
1. Converting Unicode to readable Thai text
2. Formatting the output nicely
3. Providing clear translations
"""

import requests
import json
import sys

def make_readable(response_json):
    """Convert API response to readable format"""
    
    # Decode Unicode characters
    answer = response_json.get("answer", "")
    reason = response_json.get("reason", "")
    
    # Create readable output
    print("🏥 Healthcare AI Response")
    print("=" * 50)
    
    # Map Thai letters to English
    thai_to_english = {
        "ก": "A",
        "ข": "B", 
        "ค": "C",
        "ง": "D"
    }
    
    english_answer = thai_to_english.get(answer, answer)
    
    print(f"📋 Question: {response_json.get('question', 'N/A')}")
    print(f"✅ Answer: {answer} ({english_answer})")
    print(f"💡 Reasoning: {reason}")
    
    # Show choices if available
    if "choices" in response_json:
        print("\n📝 Available Choices:")
        for letter, text in response_json["choices"].items():
            english_letter = thai_to_english.get(letter, letter)
            print(f"   {letter} ({english_letter}): {text}")
    
    # Show confidence if available
    if "confidence" in response_json:
        confidence = response_json["confidence"]
        print(f"\n🎯 Confidence: {confidence:.2%}")
    
    print("=" * 50)

def test_api():
    """Test the API with sample questions"""
    
    # Sample questions
    questions = [
        "ผมปวดท้องมาก อ้วกด้วย ไปแผนกไหนดี? ก. Endocrinology ข. Orthopedics ค. Emergency ง. Internal Medicine",
        "โรคเบาหวานรักษาได้ที่ไหน? ก. โรงพยาบาล ข. คลินิก ค. ร้านยา ง. ทุกข้อ",
        "อาการของโรคหัวใจคืออะไร? ก. ปวดหัว ข. ปวดท้อง ค. เจ็บหน้าอก ง. ปวดหลัง"
    ]
    
    api_url = "http://172.16.30.130:5000/eval"
    
    for i, question in enumerate(questions, 1):
        print(f"\n🔍 Test {i}:")
        print(f"Question: {question}")
        
        try:
            response = requests.post(
                api_url,
                json={"question": question},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                result["question"] = question  # Add question to response for display
                make_readable(result)
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Connection Error: {e}")
        
        print("\n" + "-" * 50)

def interactive_mode():
    """Interactive mode for asking questions"""
    
    api_url = "http://172.16.30.130:5000/eval"
    
    print("🏥 Healthcare AI - Interactive Mode")
    print("=" * 50)
    print("Enter your healthcare question with choices (ก. ข. ค. ง.)")
    print("Type 'quit' to exit")
    print("=" * 50)
    
    while True:
        try:
            question = input("\n🤔 Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not question:
                continue
            
            print("🔄 Processing...")
            
            response = requests.post(
                api_url,
                json={"question": question},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                result["question"] = question
                make_readable(result)
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_api()
        else:
            print("Usage: python api_client_readable.py [test]")
            print("  test: Run predefined tests")
            print("  (no args): Interactive mode")
    else:
        interactive_mode() 