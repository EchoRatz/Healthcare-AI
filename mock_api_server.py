#!/usr/bin/env python3
"""
Mock Healthcare AI API Server
=============================

Provides intelligent responses based on keyword matching and healthcare knowledge.
No LLM required - works offline with predefined rules.
"""

import re
import json
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Healthcare AI API (Mock)",
    description="Mock API for Thai Healthcare Q&A System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests/responses
class EvaluationRequest(BaseModel):
    question: str = Field(..., description="The question to evaluate")

class EvaluationResponse(BaseModel):
    answer: str = Field(..., description="The answer (e.g., 'ก', 'ข', 'ค', 'ง')")
    reason: str = Field(..., description="The reasoning for the answer")

class HealthcareRuleEngine:
    """Rule-based engine for healthcare questions."""
    
    def __init__(self):
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict[str, Any]:
        """Load healthcare rules and patterns."""
        return {
            "department_selection": {
                "patterns": [
                    (r"ปวดท้อง|อ้วก|คลื่นไส้|ท้องเสีย", "ค", "Internal Medicine"),
                    (r"ปวดหัว|เวียนหัว|มึนงง", "ค", "Internal Medicine"),
                    (r"ปวดหลัง|ปวดข้อ|กระดูก", "ข", "Orthopedics"),
                    (r"หัวใจ|ความดัน|เจ็บหน้าอก", "ค", "Internal Medicine"),
                    (r"เบาหวาน|น้ำตาล|ฮอร์โมน", "ก", "Endocrinology"),
                    (r"จิต|วิตก|กังวล|ซึมเศร้า", "ง", "Psychiatry"),
                    (r"สมอง|ประสาท|ชัก", "ค", "Internal Medicine"),
                    (r"ไต|ปัสสาวะ|ล้างไต", "ค", "Internal Medicine"),
                    (r"ฟัน|ปวดฟัน|ทันต", "ค", "Internal Medicine"),
                    (r"เด็ก|ทารก|กุมาร", "ค", "Internal Medicine")
                ]
            },
            "healthcare_rights": {
                "patterns": [
                    (r"สิทธิ์|หลักประกัน|สุขภาพแห่งชาติ", "ก", "ตรวจสุขภาพฟรี"),
                    (r"30บาท|ค่าบริการ", "ข", "30บาท"),
                    (r"ฟรี|ไม่เสียค่าใช้จ่าย", "ก", "ฟรี"),
                    (r"ไม่มีสิทธิ์|ไม่ครอบคลุม", "ง", "ไม่มีสิทธิ์"),
                    (r"ยา|เม็ด", "ค", "ยา 50 บาท/เม็ด"),
                    (r"ผ่าตัด|ศัลยกรรม", "ข", "ผ่าตัด 1000 บาท")
                ]
            },
            "cost_questions": {
                "patterns": [
                    (r"ค่าใช้จ่าย|ราคา|เท่าไหร่", "ข", "30บาท"),
                    (r"ฟรี|ไม่เสีย", "ก", "ฟรี"),
                    (r"100บาท|500บาท", "ง", "ไม่มีข้อใดถูกต้อง"),
                    (r"30บาท", "ข", "30บาท")
                ]
            },
            "emergency_coverage": {
                "patterns": [
                    (r"ฉุกเฉิน|วิกฤต|UCEP", "ง", "ทุกข้อ"),
                    (r"อุบัติเหตุ", "ก", "อุบัติเหตุ"),
                    (r"หัวใจวาย|หมดสติ", "ข", "หัวใจวาย"),
                    (r"หมดสติ", "ค", "หมดสติ")
                ]
            }
        }
    
    def analyze_question(self, question: str, choices: Dict[str, str]) -> tuple:
        """Analyze question and return answer with reasoning."""
        
        question_lower = question.lower()
        
        # Check department selection
        for pattern, answer, department in self.rules["department_selection"]["patterns"]:
            if re.search(pattern, question_lower):
                reason = f"หากมีอาการ{pattern} ควรไปพบแพทย์ที่แผนก {department} ดังนั้นจึงตอบข้อ {answer}"
                return answer, reason
        
        # Check healthcare rights
        for pattern, answer, service in self.rules["healthcare_rights"]["patterns"]:
            if re.search(pattern, question_lower):
                reason = f"ในระบบหลักประกันสุขภาพแห่งชาติ {service} จึงตอบข้อ {answer}"
                return answer, reason
        
        # Check cost questions
        for pattern, answer, cost in self.rules["cost_questions"]["patterns"]:
            if re.search(pattern, question_lower):
                reason = f"ค่าใช้จ่ายในการรักษาพยาบาลทั่วไปคือ {cost} จึงตอบข้อ {answer}"
                return answer, reason
        
        # Check emergency coverage
        for pattern, answer, coverage in self.rules["emergency_coverage"]["patterns"]:
            if re.search(pattern, question_lower):
                reason = f"การรักษาฉุกเฉินครอบคลุม {coverage} จึงตอบข้อ {answer}"
                return answer, reason
        
        # Default response based on question type
        if "แผนก" in question or "department" in question_lower:
            return "ค", "โดยทั่วไปควรไปแผนกอายุรกรรม (Internal Medicine) ก่อน"
        elif "สิทธิ์" in question or "หลักประกัน" in question:
            return "ก", "ระบบหลักประกันสุขภาพแห่งชาติให้สิทธิ์ตรวจสุขภาพฟรี"
        elif "ค่าใช้จ่าย" in question or "ราคา" in question:
            return "ข", "ค่าใช้จ่ายในการรักษาพยาบาลทั่วไปคือ 30 บาท"
        elif "ฉุกเฉิน" in question:
            return "ง", "การรักษาฉุกเฉินครอบคลุมทุกกรณี"
        else:
            return "ง", "ไม่สามารถหาข้อมูลที่เหมาะสมได้"

# Initialize rule engine
rule_engine = HealthcareRuleEngine()

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Healthcare AI API Server (Mock)",
        "version": "1.0.0",
        "endpoint": "/eval",
        "method": "POST",
        "status": "ready"
    }

@app.post("/eval", response_model=EvaluationResponse)
async def evaluate_question(request: EvaluationRequest):
    """Evaluate a healthcare question and return answer with reasoning."""
    
    try:
        question_text = request.question
        
        # Extract choices using regex
        choice_pattern = r'([ก-ง])\.([^ก-ง]+?)(?=\s*[ก-ง]\.|$)'
        choices = {}
        
        for match in re.finditer(choice_pattern, question_text):
            choice_letter = match.group(1)
            choice_text = match.group(2).strip()
            choices[choice_letter] = choice_text
        
        # If no choices found, try alternative pattern
        if not choices:
            alt_pattern = r'([ก-ง])\.\s*([^ก-ง]+?)(?=\s*[ก-ง]\.|$)'
            for match in re.finditer(alt_pattern, question_text):
                choice_letter = match.group(1)
                choice_text = match.group(2).strip()
                choices[choice_letter] = choice_text
        
        # If still no choices, create default choices
        if not choices:
            choices = {
                "ก": "ตัวเลือกที่ 1",
                "ข": "ตัวเลือกที่ 2", 
                "ค": "ตัวเลือกที่ 3",
                "ง": "ไม่มีข้อใดถูกต้อง"
            }
        
        # Analyze question using rule engine
        answer, reason = rule_engine.analyze_question(question_text, choices)
        
        # Validate answer format
        if answer not in ["ก", "ข", "ค", "ง"]:
            answer = "ง"
        
        return EvaluationResponse(
            answer=answer,
            reason=reason
        )
        
    except Exception as e:
        print(f"Error in evaluate_question: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "system_ready": True,
        "llm_available": False,
        "mode": "mock"
    }

if __name__ == "__main__":
    # Run the API server on port 5000
    uvicorn.run(
        "mock_api_server:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    ) 