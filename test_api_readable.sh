#!/bin/bash

# Healthcare AI API Test Script - Readable Output
# ==============================================

API_URL="http://172.16.30.130:5000/eval"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏥 Healthcare AI API Test${NC}"
echo "=================================="

# Function to make response readable
make_readable() {
    local response="$1"
    local question="$2"
    
    echo -e "\n${GREEN}📋 Question:${NC} $question"
    echo -e "${GREEN}📄 Raw Response:${NC} $response"
    
    # Extract answer and reason using jq if available, otherwise use grep
    if command -v jq &> /dev/null; then
        answer=$(echo "$response" | jq -r '.answer // "N/A"')
        reason=$(echo "$response" | jq -r '.reason // "N/A"')
    else
        # Fallback to grep/sed
        answer=$(echo "$response" | grep -o '"answer":"[^"]*"' | sed 's/"answer":"//;s/"//')
        reason=$(echo "$response" | grep -o '"reason":"[^"]*"' | sed 's/"reason":"//;s/"//')
    fi
    
    # Map Thai letters to English
    case $answer in
        "ก") english_answer="A" ;;
        "ข") english_answer="B" ;;
        "ค") english_answer="C" ;;
        "ง") english_answer="D" ;;
        *) english_answer="$answer" ;;
    esac
    
    echo -e "${YELLOW}✅ Answer:${NC} $answer ($english_answer)"
    echo -e "${YELLOW}💡 Reasoning:${NC} $reason"
    echo "----------------------------------"
}

# Test 1: Stomach pain question
echo -e "\n${BLUE}🔍 Test 1: Stomach Pain${NC}"
question1='{"question": "ผมปวดท้องมาก อ้วกด้วย ไปแผนกไหนดี? ก. Endocrinology ข. Orthopedics ค. Emergency ง. Internal Medicine"}'
response1=$(curl -s -X POST "$API_URL" -H "Content-Type: application/json" -d "$question1")
make_readable "$response1" "ผมปวดท้องมาก อ้วกด้วย ไปแผนกไหนดี?"

# Test 2: Diabetes question
echo -e "\n${BLUE}🔍 Test 2: Diabetes Treatment${NC}"
question2='{"question": "โรคเบาหวานรักษาได้ที่ไหน? ก. โรงพยาบาล ข. คลินิก ค. ร้านยา ง. ทุกข้อ"}'
response2=$(curl -s -X POST "$API_URL" -H "Content-Type: application/json" -d "$question2")
make_readable "$response2" "โรคเบาหวานรักษาได้ที่ไหน?"

# Test 3: Heart disease symptoms
echo -e "\n${BLUE}🔍 Test 3: Heart Disease Symptoms${NC}"
question3='{"question": "อาการของโรคหัวใจคืออะไร? ก. ปวดหัว ข. ปวดท้อง ค. เจ็บหน้าอก ง. ปวดหลัง"}'
response3=$(curl -s -X POST "$API_URL" -H "Content-Type: application/json" -d "$question3")
make_readable "$response3" "อาการของโรคหัวใจคืออะไร?"

echo -e "\n${GREEN}✅ All tests completed!${NC}" 