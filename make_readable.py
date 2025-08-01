#!/usr/bin/env python3
"""
Simple script to make JSON responses readable
Usage: python make_readable.py '{"answer":"\\u0e07","reason":"\\u0e44\\u0e21\\u0e48..."}'
"""

import json
import sys

def make_readable(json_string):
    """Convert JSON string to readable format"""
    try:
        # Parse the JSON
        data = json.loads(json_string)
        
        # Extract fields
        answer = data.get('answer', '')
        reason = data.get('reason', '')
        question = data.get('question', 'N/A')
        
        # Map Thai letters to English
        thai_map = {'ก': 'A', 'ข': 'B', 'ค': 'C', 'ง': 'D'}
        english_answer = thai_map.get(answer, answer)
        
        # Print readable format
        print("🏥 Healthcare AI Response")
        print("=" * 50)
        print(f"📋 Question: {question}")
        print(f"✅ Answer: {answer} ({english_answer})")
        print(f"💡 Reasoning: {reason}")
        print("=" * 50)
        
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        print(f"Raw input: {json_string}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Get JSON from command line argument
        json_string = sys.argv[1]
        make_readable(json_string)
    else:
        # Get JSON from stdin
        json_string = sys.stdin.read().strip()
        if json_string:
            make_readable(json_string)
        else:
            print("Usage: python make_readable.py 'JSON_STRING'")
            print("   or: echo 'JSON_STRING' | python make_readable.py") 