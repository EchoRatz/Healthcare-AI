#!/bin/bash

# Healthcare AI API Test with curl
# ================================

echo "🚀 Testing Healthcare AI API with curl"
echo "======================================"

# API endpoint
URL="http://localhost:5000/eval"

# Test question (matching the specification)
QUESTION='{
  "question": "ผมปวดท้องมาก อ้วกด้วย ไปแผนกไหนดี?ก.Endocrinology ข.Orthopedics ค.Internal Medicine ง.Psychiatry"
}'

echo "URL: $URL"
echo "Method: POST"
echo "Headers: Content-Type: application/json"
echo "Request Body: $QUESTION"
echo ""

# Make the API call
curl -X POST "$URL" \
  -H "Content-Type: application/json" \
  -d "$QUESTION" \
  -w "\n\nStatus Code: %{http_code}\nResponse Time: %{time_total}s\n"

echo ""
echo "✅ Test completed!" 