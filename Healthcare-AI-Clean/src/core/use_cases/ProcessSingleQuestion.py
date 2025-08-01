"""Use case for processing a single question."""
import time
from ...domain.entities.Question import Question, Answer
from ...domain.services.AnswerService import AnswerService


class ProcessSingleQuestion:
    """Use case to process a single question."""
    
    def __init__(self, answer_service: AnswerService):
        self.answer_service = answer_service
    
    def execute(self, question: Question) -> Answer:
        """Process a single question and return answer."""
        start_time = time.time()
        
        try:
            if not self.answer_service.is_available():
                return Answer(
                    question_id=question.id,
                    answer="Service unavailable",
                    confidence=0.0,
                    processing_time=time.time() - start_time
                )
            
            answer = self.answer_service.answer_question(question)
            answer.processing_time = time.time() - start_time
            
            return answer
            
        except Exception as e:
            return Answer(
                question_id=question.id,
                answer=f"Error: {str(e)}",
                confidence=0.0,
                processing_time=time.time() - start_time
            )