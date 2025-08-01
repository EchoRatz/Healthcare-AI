"""
FastAPI Application for Healthcare-AI Multiple Choice Questions
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path
import re
import os
from contextlib import asynccontextmanager

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / "src"))
sys.path.append(str(project_root))

from database.vector_store import VectorStore
from database.text_processor import TextProcessor
from database.search_engine import SearchEngine
from llm.mock_client import MockLLMClient
from rag.rag_pipeline import RAGPipeline
from config.settings import DEFAULT_CONFIG
from utils.logger import get_logger

logger = get_logger(__name__)

# Load matching sensitivity threshold from environment variable, fallback to 0.5 if not set
try:
    MATCHING_SENSITIVITY_THRESHOLD = float(os.getenv("MATCHING_SENSITIVITY_THRESHOLD", "0.5"))
except ValueError:
    MATCHING_SENSITIVITY_THRESHOLD = 0.5
    logger.warning("Invalid MATCHING_SENSITIVITY_THRESHOLD in .env, using default 0.5")

# Global variables for system components
search_engine: Optional[SearchEngine] = None
rag_pipeline: Optional[RAGPipeline] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup the RAG system."""
    global search_engine, rag_pipeline
    
    # Startup
    try:
        logger.info("Initializing Healthcare-AI system...")
        
        # Initialize components
        vector_store = VectorStore(dimension=DEFAULT_CONFIG.vector_dimension)
        text_processor = TextProcessor(model_name=DEFAULT_CONFIG.default_model)
        search_engine = SearchEngine(vector_store, text_processor)
        llm_client = MockLLMClient()
        
        # Create RAG pipeline
        rag_pipeline = RAGPipeline(search_engine, llm_client)
        
        # Load sample data
        sample_texts = [
            "การเรียนรู้เป็นกระบวนการสำคัญสำหรับการพัฒนาตนเอง",
            "สุขภาพดีมาจากการออกกำลังกายเป็นประจำและการรับประทานอาหารที่มีประโยชน์",
            "ความสุขเป็นสิ่งที่เกิดจากการมีจิตใจที่สงบ",
            "การศึกษาเป็นรากฐานของการพัฒนาประเทศ",
            "เทคโนโลยีช่วยทำให้ชีวิตสะดวกสบายมากขึ้น"
        ]
        
        count = search_engine.add_texts_from_list(sample_texts)
        logger.info(f"System initialized with {count} documents")
        
    except Exception as e:
        logger.error(f"Failed to initialize system: {e}")
        raise

    yield
    
    # Shutdown
    logger.info("Shutting down Healthcare-AI system...")

# FastAPI app instance with lifespan
app = FastAPI(
    title="Healthcare-AI Multiple Choice API",
    description="API for answering multiple choice questions using RAG pipeline",
    version="1.0.0",
    lifespan=lifespan
)

# Pydantic models
class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str


def extract_choices(question: str) -> dict:
    """Extract multiple choice options from question text."""
    choices = {}
    
    # More robust pattern matching for Thai choice letters
    # Look for Thai choice letters followed by period, then capture text until next choice or end
    choice_pattern = r'([ก-ง])\.([^ก-ง]*?)(?=\s+[ก-ง]\.|$)'
    matches = re.findall(choice_pattern, question, re.DOTALL)
    
    # If the above doesn't work, try a simpler approach
    if not matches:
        # Alternative pattern: split by choice letters and process
        parts = re.split(r'\s+([ก-ง])\.', question)
        if len(parts) > 1:
            for i in range(1, len(parts), 2):
                if i + 1 < len(parts):
                    choice_letter = parts[i]
                    choice_text = parts[i + 1].strip()
                    if choice_text:
                        choices[choice_letter] = choice_text
    else:
        for choice_letter, choice_text in matches:
            clean_text = choice_text.strip()
            if clean_text:
                choices[choice_letter] = clean_text
    
    return choices

def analyze_answer_with_rag(question: str, choices: dict) -> str:
    """Use RAG pipeline to analyze and answer the multiple choice question."""
    try:
        # Create a comprehensive query including all choices
        full_query = f"{question} ตัวเลือก: " + " ".join([f"{k}. {v}" for k, v in choices.items()])
        
        # Get answer from RAG pipeline
        result = rag_pipeline.answer_question(full_query, top_k=3)
        rag_answer = result["answer"].lower()
        
        # Simple logic to determine which choice(s) are correct
        # This is a basic implementation - you might want to make it more sophisticated
        selected_choices = []
        
        for choice_key, choice_text in choices.items():
            # Check if the choice content appears in the RAG answer or context
            choice_words = choice_text.lower().split()
            context_text = " ".join(result.get("context", [])).lower()
            
            # Count word matches
            matches = sum(1 for word in choice_words if word in rag_answer or word in context_text)
            
            # If significant portion of choice appears in answer/context, consider it correct
            if len(choice_words) > 0 and matches / len(choice_words) > MATCHING_SENSITIVITY_THRESHOLD:
                selected_choices.append(choice_key)
        
        # If no clear matches, try semantic similarity approach
        if not selected_choices:
            # Use RAG to directly ask which choice is correct
            direct_query = f"จากตัวเลือกต่อไปนี้ ข้อใดถูกต้อง? {question}"
            direct_result = rag_pipeline.answer_question(direct_query)
            
            # Look for choice indicators in the answer
            for choice_key in choices.keys():
                if choice_key in direct_result["answer"]:
                    selected_choices.append(choice_key)
        
        # Default fallback
        if not selected_choices:
            # Default to the first available choice if uncertain
            selected_choices = [next(iter(choices.keys()), "")]
        
        return ", ".join(selected_choices)
        
    except Exception as e:
        logger.error(f"Error in RAG analysis: {e}")
        # Default to the first available choice or an empty string if no choices exist
        return next(iter(choices.keys()), "")

@app.post("/answer", response_model=AnswerResponse)
async def answer_question(request: QuestionRequest):
    """
    Answer a multiple choice question using RAG pipeline.
    
    Expected format: "คำถาม ก.ตัวเลือก1 ข.ตัวเลือก2 ค.ตัวเลือก3 ง.ตัวเลือก4"
    """
    try:
        if not rag_pipeline:
            raise HTTPException(status_code=500, detail="RAG system not initialized")
        
        question_text = request.question.strip()
        
        if not question_text:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Extract choices from the question
        choices = extract_choices(question_text)
        
        if not choices:
            raise HTTPException(
                status_code=400, 
                detail="No valid choices found. Expected format: 'คำถาม ก.choice1 ข.choice2 ค.choice3 ง.choice4'"
            )
        
        logger.info(f"Processing question with {len(choices)} choices")
        
        # Analyze and get answer
        answer = analyze_answer_with_rag(question_text, choices)
        
        return AnswerResponse(answer=answer)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "system_ready": rag_pipeline is not None,
        "message": "Healthcare-AI API is running"
    }

@app.get("/stats")
async def get_stats():
    """Get system statistics."""
    if not rag_pipeline:
        raise HTTPException(status_code=500, detail="RAG system not initialized")
    
    try:
        info = rag_pipeline.get_pipeline_info()
        return {
            "total_documents": info['search_engine_stats']['total_texts'],
            "vector_dimension": info['search_engine_stats']['vector_dimension'],
            "llm_client": info['llm_info']['type'] if info['llm_info'] else 'None'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run(app, host="0.0.0.0", port=8001)