#!/usr/bin/env python3
"""
Healthcare AI API Server
========================

Simple API server with a single evaluation endpoint.
Matches the specification: POST /eval with question and returns answer + reason
"""

import os
import sys
import json
import time
from typing import Dict, Any

# Add the refactored project to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Healthcare-AI-Refactored', 'src'))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Import from refactored architecture
from core.use_cases.ProcessQuestion import ProcessQuestion
from core.use_cases.SearchDocuments import SearchDocuments
from infrastructure.llm.OllamaClient import OllamaClient
from infrastructure.database.FAISSVectorStore import FAISSVectorStore
from shared.config.Config import AppConfig
from shared.logging.LoggerMixin import get_logger

# Initialize FastAPI app
app = FastAPI(
    title="Healthcare AI API",
    description="API for Thai Healthcare Q&A System",
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

# Global variables for system components
llm_client = None
vector_store = None
process_question_use_case = None
search_documents_use_case = None
logger = None

def initialize_system():
    """Initialize the healthcare AI system components."""
    global llm_client, vector_store, process_question_use_case, search_documents_use_case, logger
    
    try:
        # Initialize configuration
        config = AppConfig.from_file("Healthcare-AI-Refactored/config/app.json")
        logger = get_logger(__name__)
        
        logger.info("Initializing Healthcare AI API Server...")
        
        # Initialize LLM client
        llm_client = OllamaClient()
        logger.info("LLM client initialized")
        
        # Initialize vector store
        vector_store = FAISSVectorStore()
        vector_store.load_documents()
        logger.info("Vector store initialized and documents loaded")
        
        # Initialize use cases
        search_documents_use_case = SearchDocuments(vector_store)
        process_question_use_case = ProcessQuestion(llm_client, search_documents_use_case)
        logger.info("Use cases initialized")
        
        logger.info("Healthcare AI system initialization complete")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize system: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup."""
    success = initialize_system()
    if not success:
        logger.error("Failed to initialize system on startup")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Healthcare AI API Server",
        "version": "1.0.0",
        "endpoint": "/eval",
        "method": "POST"
    }

@app.post("/eval", response_model=EvaluationResponse)
async def evaluate_question(request: EvaluationRequest):
    """Evaluate a healthcare question and return answer with reasoning."""
    if not process_question_use_case:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        # Process the question
        result = process_question_use_case.process(
            question=request.question,
            context_size=3
        )
        
        # Extract answer from the response
        answer_text = result.get("answer", "")
        
        # Parse the answer to extract choice (ก, ข, ค, ง)
        import re
        choice_match = re.search(r'[ก-ง]', answer_text)
        if choice_match:
            answer = choice_match.group(0)
        else:
            # Default to "ง" if no choice found
            answer = "ง"
        
        # Create reasoning
        reason = f"จากการวิเคราะห์คำถามและข้อมูลความรู้ที่เกี่ยวข้อง ได้คำตอบคือ {answer} เพราะ {answer_text}"
        
        return EvaluationResponse(
            answer=answer,
            reason=reason
        )
        
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

if __name__ == "__main__":
    # Run the API server on port 5000 to match the specification
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )
