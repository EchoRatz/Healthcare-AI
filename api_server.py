#!/usr/bin/env python3
"""
Healthcare AI API Server
========================

FastAPI server for the Healthcare AI Q&A system.
Provides REST API endpoints for question processing and batch operations.
"""

import os
import sys
import csv
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add the refactored project to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Healthcare-AI-Refactored', 'src'))

from fastapi import FastAPI, HTTPException, BackgroundTasks
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
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
class QuestionRequest(BaseModel):
    question: str = Field(..., description="The question to process")
    context_size: int = Field(default=3, description="Number of context documents to use")
    model_name: Optional[str] = Field(default=None, description="LLM model to use")

class BatchRequest(BaseModel):
    questions: List[str] = Field(..., description="List of questions to process")
    context_size: int = Field(default=3, description="Number of context documents to use")
    model_name: Optional[str] = Field(default=None, description="LLM model to use")

class QuestionResponse(BaseModel):
    question: str
    answer: str
    confidence: float
    sources: List[Dict[str, Any]]
    processing_time: float
    timestamp: str
    model_used: str

class BatchResponse(BaseModel):
    results: List[QuestionResponse]
    total_questions: int
    successful_questions: int
    failed_questions: int
    total_processing_time: float
    average_confidence: float

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    model_available: bool
    knowledge_base_loaded: bool
    vector_store_ready: bool

class SystemStatus(BaseModel):
    llm_status: str
    vector_store_status: str
    knowledge_base_status: str
    model_name: Optional[str] = None
    documents_loaded: int = 0

# Global variables for system components
llm_client = None
vector_store = None
process_question_use_case = None
search_documents_use_case = None
logger = None
config = None

def initialize_system():
    """Initialize the healthcare AI system components."""
    global llm_client, vector_store, process_question_use_case, search_documents_use_case, logger, config
    
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

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Healthcare AI API Server",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "status": "/status"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    model_available = llm_client is not None and llm_client.is_available() if llm_client else False
    knowledge_base_loaded = vector_store is not None and vector_store.is_loaded() if vector_store else False
    vector_store_ready = vector_store is not None if vector_store else False
    
    return HealthResponse(
        status="healthy" if all([model_available, knowledge_base_loaded, vector_store_ready]) else "degraded",
        timestamp=datetime.now().isoformat(),
        model_available=model_available,
        knowledge_base_loaded=knowledge_base_loaded,
        vector_store_ready=vector_store_ready
    )

@app.get("/status", response_model=SystemStatus)
async def system_status():
    """Get detailed system status."""
    if not llm_client or not vector_store:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    return SystemStatus(
        llm_status="available" if llm_client.is_available() else "unavailable",
        vector_store_status="ready" if vector_store.is_loaded() else "not_ready",
        knowledge_base_status="loaded" if vector_store.is_loaded() else "not_loaded",
        model_name=llm_client.get_model_name() if llm_client else None,
        documents_loaded=vector_store.get_document_count() if vector_store else 0
    )

@app.post("/question", response_model=QuestionResponse)
async def process_question(request: QuestionRequest):
    """Process a single question."""
    if not process_question_use_case:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    start_time = time.time()
    
    try:
        # Process the question
        result = process_question_use_case.process(
            question=request.question,
            context_size=request.context_size,
            model_name=request.model_name
        )
        
        processing_time = time.time() - start_time
        
        return QuestionResponse(
            question=result["question"],
            answer=result["answer"],
            confidence=result["confidence"],
            sources=result["sources"],
            processing_time=processing_time,
            timestamp=result["timestamp"],
            model_used=llm_client.get_model_name() if llm_client else "unknown"
        )
        
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.post("/batch", response_model=BatchResponse)
async def process_batch(request: BatchRequest, background_tasks: BackgroundTasks):
    """Process multiple questions in batch."""
    if not process_question_use_case:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    start_time = time.time()
    results = []
    successful = 0
    failed = 0
    
    try:
        # Process questions in batch
        batch_results = process_question_use_case.process_batch(
            questions=request.questions,
            context_size=request.context_size,
            model_name=request.model_name
        )
        
        # Convert results to response format
        for i, result in enumerate(batch_results):
            try:
                question_response = QuestionResponse(
                    question=result["question"],
                    answer=result["answer"],
                    confidence=result["confidence"],
                    sources=result["sources"],
                    processing_time=0.0,  # Individual processing time not tracked in batch
                    timestamp=result["timestamp"],
                    model_used=llm_client.get_model_name() if llm_client else "unknown"
                )
                results.append(question_response)
                successful += 1
            except Exception as e:
                logger.error(f"Error processing question {i}: {e}")
                failed += 1
        
        total_time = time.time() - start_time
        avg_confidence = sum(r.confidence for r in results) / len(results) if results else 0.0
        
        return BatchResponse(
            results=results,
            total_questions=len(request.questions),
            successful_questions=successful,
            failed_questions=failed,
            total_processing_time=total_time,
            average_confidence=avg_confidence
        )
        
    except Exception as e:
        logger.error(f"Error processing batch: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing batch: {str(e)}")

@app.post("/reload")
async def reload_system():
    """Reload the system components."""
    try:
        success = initialize_system()
        if success:
            return {"message": "System reloaded successfully", "status": "success"}
        else:
            raise HTTPException(status_code=500, detail="Failed to reload system")
    except Exception as e:
        logger.error(f"Error reloading system: {e}")
        raise HTTPException(status_code=500, detail=f"Error reloading system: {str(e)}")

@app.get("/models")
async def list_available_models():
    """List available LLM models."""
    if not llm_client:
        raise HTTPException(status_code=503, detail="LLM client not initialized")
    
    try:
        models = llm_client.list_available_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing models: {str(e)}")

@app.post("/test")
async def test_endpoint():
    """Test endpoint for basic functionality."""
    test_question = "ผู้ป่วยมีสิทธิ์รับบริการอะไรบ้างในระบบหลักประกันสุขภาพแห่งชาติ?"
    
    try:
        result = process_question_use_case.process(test_question) if process_question_use_case else None
        
        return {
            "test_question": test_question,
            "result": result,
            "system_ready": process_question_use_case is not None,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Test endpoint error: {e}")
        return {
            "test_question": test_question,
            "error": str(e),
            "system_ready": False,
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Run the API server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
