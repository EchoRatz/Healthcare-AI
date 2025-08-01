"""Use case for batch processing CSV files."""
import time
from datetime import datetime
from typing import List

# Fix: Use absolute imports
from domain.entities.Question import Question
from domain.entities.ProcessingResult import BatchResult, ProcessingStats
from domain.repositories.QuestionRepository import QuestionRepository
from domain.services.AnswerService import AnswerService
from .ProcessSingleQuestion import ProcessSingleQuestion


class ProcessCsvBatch:
    """Use case for batch processing CSV files."""
    
    def __init__(self, question_repo: QuestionRepository, answer_service: AnswerService):
        self.question_repo = question_repo
        self.process_question = ProcessSingleQuestion(answer_service)
    
    def execute(self, input_file: str, output_file: str, batch_size: int = 10, clean_format: bool = False) -> BatchResult:
        """Execute batch processing."""
        # Load questions
        questions = self.question_repo.load_from_csv(input_file)
        
        # Initialize stats
        stats = ProcessingStats(
            total_questions=len(questions),
            successful=0,
            errors=0,
            start_time=datetime.now()
        )
        
        results = []
        
        # Process in batches
        for i in range(0, len(questions), batch_size):
            batch = questions[i:i + batch_size]
            batch_results = self._process_batch(batch, i // batch_size + 1, len(questions) // batch_size + 1)
            
            for result in batch_results:
                results.append(result)
                if not result['answer'].startswith('Error'):
                    stats.successful += 1
                else:
                    stats.errors += 1
        
        stats.end_time = datetime.now()
        
        # Save results
        self.question_repo.save_answers_to_csv(results, output_file, clean_format)
        
        return BatchResult(results=results, stats=stats, output_file=output_file)
    
    def _process_batch(self, questions: List[Question], batch_num: int, total_batches: int) -> List[dict]:
        """Process a single batch of questions."""
        print(f"🔄 Processing batch {batch_num}/{total_batches}")
        
        batch_results = []
        for question in questions:
            answer = self.process_question.execute(question)
            
            batch_results.append({
                'id': question.id,
                'question': question.text,
                'answer': answer.answer
            })
            
            print(f"  ✅ Q{question.id}: {answer.answer}")
        
        return batch_results