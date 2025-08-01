#!/bin/bash

# Simple curl command that makes API responses readable
API_URL="http://172.16.30.130:5000/eval"

echo "🏥 Healthcare AI API - Readable Response"
echo "======================================"

# Make the API call and convert Unicode to readable text
response=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"question": "ผมปวดท้องมาก อ้วกด้วย ไปแผนกไหนดี? ก. Endocrinology ข. Orthopedics ค. Emergency ง. Internal Medicine"}')

echo "Raw response: $response"
echo ""

# Convert to readable format using Python
echo "$response" | python3 -c "
import json
import sys

try:
    data = json.load(sys.stdin)
    
    # Convert Unicode to readable Thai
    answer = data.get('answer', '')
    reason = data.get('reason', '')
    
    # Map Thai letters to English
    thai_map = {'ก': 'A', 'ข': 'B', 'ค': 'C', 'ง': 'D'}
    english_answer = thai_map.get(answer, answer)
    
    print('📋 Question: ผมปวดท้องมาก อ้วกด้วย ไปแผนกไหนดี?')
    print('✅ Answer:', answer, f'({english_answer})')
    print('💡 Reasoning:', reason)
    
except Exception as e:
    print('Error parsing response:', e)
    print('Raw response:', sys.stdin.read())
" 