#!/usr/bin/env python3
"""
Healthcare Q&A Processing Script

This script processes the healthcare Q&A dataset using the enhanced AI system.
It reads questions from test.csv and generates answers in the expected format.
"""

import sys
import csv
import argparse
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import re

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from infrastructure.factories.EnhancedSystemFactory import EnhancedSystemFactory


class HealthcareQAProcessor:
    """Processor for healthcare Q&A dataset."""
    
    def __init__(self, config_path: str = "config/enhanced_system.json"):
        """Initialize the processor with the enhanced system."""
        self.factory = EnhancedSystemFactory(config_path)
        self.engine = self.factory.create_chain_of_thought_engine()
        
    def load_test_data(self, input_file: str) -> List[Dict[str, Any]]:
        """Load test data from CSV file."""
        questions = []
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    questions.append({
                        'id': int(row['id']),
                        'question': row['question'],
                        'answer': row.get('answer', '')
                    })
                    
            print(f"Loaded {len(questions)} questions from {input_file}")
            return questions
            
        except Exception as e:
            print(f"Error loading test data: {e}")
            return []
    
    def extract_answer_from_response(self, response: str) -> str:
        """Extract answer choice (ก, ข, ค, ง) from LLM response."""
        # Look for Thai answer choices in the response
        answer_patterns = [
            r'[กขคง]\s*[\.\)]',  # ก. ข. ค. ง.
            r'[กขคง]\s*[\.\)]\s*[^กขคง]',  # ก. answer ข. answer
            r'คำตอบคือ\s*[กขคง]',  # คำตอบคือ ก
            r'ตอบ\s*[กขคง]',  # ตอบ ก
            r'เลือก\s*[กขคง]',  # เลือก ก
        ]
        
        for pattern in answer_patterns:
            match = re.search(pattern, response)
            if match:
                # Extract the Thai character
                answer_char = re.search(r'[กขคง]', match.group())
                if answer_char:
                    return answer_char.group()
        
        # If no clear pattern found, look for the first ก, ข, ค, ง in the response
        first_answer = re.search(r'[กขคง]', response)
        if first_answer:
            return first_answer.group()
        
        return ""
    
    def process_question(self, question: str) -> str:
        """Process a single question and return the answer."""
        try:
            result = self.engine.process_query(question)
            answer = result.get('answer', '')
            
            # Extract answer choice from the response
            extracted_answer = self.extract_answer_from_response(answer)
            
            if extracted_answer:
                return extracted_answer
            else:
                print(f"Warning: Could not extract answer choice from response: {answer[:100]}...")
                return ""
                
        except Exception as e:
            print(f"Error processing question: {e}")
            return ""
    
    def save_results(self, results: List[Dict[str, Any]], output_file: str):
        """Save results to CSV file."""
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'answer'])
                
                for result in results:
                    writer.writerow([result['id'], result['answer']])
                    
            print(f"Results saved to {output_file}")
            
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def process_batch(self, questions: List[Dict[str, Any]], 
                     batch_size: int = 5, 
                     max_questions: Optional[int] = None) -> List[Dict[str, Any]]:
        """Process questions in batches."""
        results = []
        
        # Limit questions if specified
        if max_questions:
            questions = questions[:max_questions]
        
        total_questions = len(questions)
        print(f"Processing {total_questions} questions in batches of {batch_size}")
        
        for i in range(0, total_questions, batch_size):
            batch = questions[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_questions + batch_size - 1) // batch_size
            
            print(f"\nProcessing batch {batch_num}/{total_batches} ({len(batch)} questions)")
            
            for j, question_data in enumerate(batch):
                question_id = question_data['id']
                question_text = question_data['question']
                
                print(f"  Processing question {question_id} ({i + j + 1}/{total_questions})")
                
                start_time = time.time()
                answer = self.process_question(question_text)
                processing_time = time.time() - start_time
                
                results.append({
                    'id': question_id,
                    'answer': answer
                })
                
                print(f"    Answer: {answer} (took {processing_time:.2f}s)")
            
            # Small delay between batches to avoid overwhelming the system
            if i + batch_size < total_questions:
                time.sleep(1)
        
        return results
    
    def run(self, input_file: str, output_file: str, 
            batch_size: int = 5, max_questions: Optional[int] = None):
        """Run the complete processing pipeline."""
        print("=" * 60)
        print("HEALTHCARE Q&A PROCESSING")
        print("=" * 60)
        
        # Load test data
        questions = self.load_test_data(input_file)
        if not questions:
            print("No questions loaded. Exiting.")
            return
        
        # Process questions
        start_time = time.time()
        results = self.process_batch(questions, batch_size, max_questions)
        total_time = time.time() - start_time
        
        # Save results
        self.save_results(results, output_file)
        
        # Print summary
        print("\n" + "=" * 60)
        print("PROCESSING SUMMARY")
        print("=" * 60)
        print(f"Total questions processed: {len(results)}")
        print(f"Total processing time: {total_time:.2f} seconds")
        print(f"Average time per question: {total_time/len(results):.2f} seconds")
        
        # Count answers
        answer_counts = {}
        for result in results:
            answer = result['answer']
            answer_counts[answer] = answer_counts.get(answer, 0) + 1
        
        print(f"\nAnswer distribution:")
        for answer, count in sorted(answer_counts.items()):
            print(f"  {answer}: {count} ({count/len(results)*100:.1f}%)")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Process healthcare Q&A dataset')
    parser.add_argument('--input', '-i', 
                       default='src/infrastructure/test.csv',
                       help='Input CSV file (default: src/infrastructure/test.csv)')
    parser.add_argument('--output', '-o', 
                       default='test_sample_output.csv',
                       help='Output CSV file (default: test_sample_output.csv)')
    parser.add_argument('--batch-size', '-b', 
                       type=int, default=5,
                       help='Batch size for processing (default: 5)')
    parser.add_argument('--max-questions', '-m', 
                       type=int, default=None,
                       help='Maximum number of questions to process (default: all)')
    parser.add_argument('--config', '-c', 
                       default='config/enhanced_system.json',
                       help='Configuration file (default: config/enhanced_system.json)')
    
    args = parser.parse_args()
    
    # Create processor
    processor = HealthcareQAProcessor(args.config)
    
    # Run processing
    processor.run(
        input_file=args.input,
        output_file=args.output,
        batch_size=args.batch_size,
        max_questions=args.max_questions
    )


if __name__ == "__main__":
    main() 