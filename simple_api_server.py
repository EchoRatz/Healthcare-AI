#!/usr/bin/env python3
"""
Simple Healthcare AI API Server
===============================

Direct API server using the working high-accuracy healthcare QA system.
No complex dependencies, just the core functionality.
"""

import os
import sys
import json
import re
from typing import Dict, Any

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Import the working high-accuracy system
from high_accuracy_healthcare_qa_system import HighAccuracyHealthcareQA

# Initialize FastAPI app
app = FastAPI(
    title="Healthcare AI API",
    description="Simple API for Thai Healthcare Q&A System",
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

# Global QA system
qa_system = None

def initialize_system():
    """Initialize the healthcare AI system."""
    global qa_system
    
    try:
        print("🏥 Initializing Healthcare AI System...")
        qa_system = HighAccuracyHealthcareQA()
        
        # Load knowledge base
        qa_system.load_knowledge_base()
        
        print("✅ System initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup."""
    success = initialize_system()
    if not success:
        print("⚠️ System initialization failed, but API will still work with fallback responses")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Healthcare AI API Server",
        "version": "1.0.0",
        "endpoint": "/eval",
        "method": "POST",
        "status": "ready" if qa_system else "initializing"
    }

@app.post("/eval", response_model=EvaluationResponse)
async def evaluate_question(request: EvaluationRequest):
    """Evaluate a healthcare question and return answer with reasoning."""
    
    try:
        # Parse the question to extract choices
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
            # Look for ก. ข. ค. ง. pattern
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
        
        # Process with QA system if available
        if qa_system:
            try:
                # Parse question
                question, extracted_choices = qa_system.parse_question_enhanced(question_text)
                
                # Use extracted choices if available, otherwise use regex choices
                if extracted_choices:
                    choices = extracted_choices
                
                # Analyze question
                question_analysis = qa_system.analyze_question_advanced(question)
                
                # Search for context
                context_matches = qa_system.search_context_semantic(question_analysis)
                
                # Check if LLM is available
                if qa_system.check_llama31():
                    # Query LLM
                    answers, confidence = qa_system.query_llama31_optimized(
                        question, choices, context_matches, question_analysis
                    )
                    
                    # Validate answer
                    answer_analysis = qa_system.validate_answer_advanced(
                        question, choices, answers, question_analysis
                    )
                    
                    # Get final answer
                    final_answers = answer_analysis.selected_answers if not answer_analysis.should_reject else answers
                    answer = ",".join(final_answers) if final_answers else "ง"
                    
                    # Create reasoning
                    reason = f"จากการวิเคราะห์คำถามและข้อมูลความรู้ที่เกี่ยวข้อง ได้คำตอบคือ {answer} เพราะ {answer_analysis.reasoning}"
                    
                else:
                    # Fallback: use keyword matching
                    answer = "ง"  # Default to "ง"
                    reason = "ไม่สามารถเชื่อมต่อกับ AI model ได้ จึงตอบข้อ ง"
                    
            except Exception as e:
                print(f"Error processing with QA system: {e}")
                answer = "ง"
                reason = f"เกิดข้อผิดพลาดในการประมวลผล: {str(e)}"
        else:
            # Fallback response when system is not initialized
            answer = "ง"
            reason = "ระบบยังไม่พร้อมใช้งาน กรุณาลองใหม่อีกครั้ง"
        
        # Ensure answer is a single choice
        if "," in answer:
            # Take the first answer if multiple
            answer = answer.split(",")[0].strip()
        
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
        "status": "healthy" if qa_system else "degraded",
        "system_ready": qa_system is not None,
        "llm_available": qa_system.check_llama31() if qa_system else False
    }

if __name__ == "__main__":
    # Run the API server on port 5000
    uvicorn.run(
        "simple_api_server:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    ) 