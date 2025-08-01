#!/usr/bin/env python3
"""
Healthcare Q&A Processing Script

This script processes the healthcare Q&A dataset using the enhanced chain-of-thought system.
It reads questions from test.csv and generates answers in the format of test_sample_output.csv.
"""

import csv
import json
import time
import argparse
from typing import List, Dict, Any
from pathlib import Path

# Add the src directory to the Python path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from infrastructure.factories.EnhancedSystemFactory import EnhancedSystemFactory
from core.use_cases.ChainOfThoughtEngine import ChainOfThoughtEngine


class HealthcareQAProcessor:
    """Processor for healthcare Q&A dataset."""
    
    def __init__(self, config_path: str = "config/enhanced_system.json"):
        """Initialize the processor."""
        self.config_path = config_path
        self.factory = None
        self.engine = None
        self.setup_system()
    
    def setup_system(self) -> bool:
        """Setup the enhanced system."""
        try:
            print("Setting up enhanced chain-of-thought system...")
            self.factory = EnhancedSystemFactory(self.config_path)
            self.engine = self.factory.create_chain_of_thought_engine()
            print("✅ System setup complete!")
            return True
        except Exception as e:
            print(f"❌ Failed to setup system: {e}")
            return False
    
    def load_test_data(self, input_file: str) -> List[Dict[str, Any]]:
        """Load test data from CSV file."""
        try:
            questions = []
            with open(input_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    questions.append({
                        'id': int(row['id']),
                        'question': row['question'],
                        'expected_answer': row.get('answer', '')
                    })
            print(f"✅ Loaded {len(questions)} questions from {input_file}")
            return questions
        except Exception as e:
            print(f"❌ Failed to load test data: {e}")
            return []
    
    def process_question(self, question: str, question_id: int) -> Dict[str, Any]:
        """Process a single question."""
        try:
            print(f"Processing question {question_id}: {question[:100]}...")
            
            # Process with chain-of-thought engine
            result = self.engine.process_query(question)
            
            # Extract answer from the response
            answer = self.extract_answer_from_response(result.get('answer', ''))
            
            return {
                'id': question_id,
                'question': question,
                'answer': answer,
                'full_response': result.get('answer', ''),
                'processing_time': result.get('processing_time', 0),
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Failed to process question {question_id}: {e}")
            return {
                'id': question_id,
                'question': question,
                'answer': '',
                'full_response': '',
                'processing_time': 0,
                'success': False,
                'error': str(e)
            }
    
    def extract_answer_from_response(self, response: str) -> str:
        """Extract the answer choice from the response."""
        try:
            # Look for answer patterns like "ก.", "ข.", "ค.", "ง."
            import re
            
            # Find all answer choices mentioned
            answer_pattern = r'[ก-ง]\s*[.,]'
            answers = re.findall(answer_pattern, response)
            
            if answers:
                # Clean up the answers
                clean_answers = []
                for answer in answers:
                    clean_answer = answer.strip('., ')
                    if clean_answer in ['ก', 'ข', 'ค', 'ง']:
                        clean_answers.append(clean_answer)
                
                if clean_answers:
                    return ','.join(clean_answers)
            
            # If no clear answer found, try to extract from the end of response
            lines = response.split('\n')
            for line in reversed(lines):
                line = line.strip()
                if any(choice in line for choice in ['ก', 'ข', 'ค', 'ง']):
                    # Extract answer choices from this line
                    found_answers = []
                    for choice in ['ก', 'ข', 'ค', 'ง']:
                        if choice in line:
                            found_answers.append(choice)
                    if found_answers:
                        return ','.join(found_answers)
            
            return ''
            
        except Exception as e:
            print(f"Warning: Failed to extract answer from response: {e}")
            return ''
    
    def save_results(self, results: List[Dict[str, Any]], output_file: str):
        """Save results to CSV file."""
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['id', 'answer'])
                
                for result in results:
                    writer.writerow([result['id'], result['answer']])
            
            print(f"✅ Results saved to {output_file}")
            
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
    
    def save_detailed_results(self, results: List[Dict[str, Any]], output_file: str):
        """Save detailed results to JSON file."""
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(results, file, ensure_ascii=False, indent=2)
            
            print(f"✅ Detailed results saved to {output_file}")
            
        except Exception as e:
            print(f"❌ Failed to save detailed results: {e}")
    
    def process_batch(self, questions: List[Dict[str, Any]], batch_size: int = 5) -> List[Dict[str, Any]]:
        """Process questions in batches."""
        results = []
        total_questions = len(questions)
        
        print(f"Processing {total_questions} questions in batches of {batch_size}...")
        
        for i in range(0, total_questions, batch_size):
            batch = questions[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_questions + batch_size - 1) // batch_size
            
            print(f"\n--- Processing batch {batch_num}/{total_batches} ---")
            
            for question_data in batch:
                result = self.process_question(
                    question_data['question'], 
                    question_data['id']
                )
                results.append(result)
                
                # Small delay to avoid overwhelming the system
                time.sleep(0.5)
        
        return results
    
    def print_summary(self, results: List[Dict[str, Any]]):
        """Print processing summary."""
        total = len(results)
        successful = sum(1 for r in results if r.get('success', False))
        failed = total - successful
        
        print(f"\n{'='*60}")
        print("PROCESSING SUMMARY")
        print(f"{'='*60}")
        print(f"Total questions: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Success rate: {(successful/total)*100:.1f}%")
        
        if successful > 0:
            avg_time = sum(r.get('processing_time', 0) for r in results if r.get('success', False)) / successful
            print(f"Average processing time: {avg_time:.2f} seconds")
        
        print(f"{'='*60}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Process healthcare Q&A dataset')
    parser.add_argument('--input', default='src/infrastructure/test.csv', 
                       help='Input CSV file path')
    parser.add_argument('--output', default='test_output.csv', 
                       help='Output CSV file path')
    parser.add_argument('--detailed', default='detailed_results.json', 
                       help='Detailed results JSON file path')
    parser.add_argument('--config', default='config/enhanced_system.json', 
                       help='Configuration file path')
    parser.add_argument('--batch-size', type=int, default=5, 
                       help='Batch size for processing')
    parser.add_argument('--max-questions', type=int, default=None, 
                       help='Maximum number of questions to process')
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = HealthcareQAProcessor(args.config)
    
    if not processor.engine:
        print("❌ Failed to initialize system. Exiting.")
        return
    
    # Load test data
    questions = processor.load_test_data(args.input)
    
    if not questions:
        print("❌ No questions loaded. Exiting.")
        return
    
    # Limit questions if specified
    if args.max_questions:
        questions = questions[:args.max_questions]
        print(f"Limited to {len(questions)} questions")
    
    # Process questions
    print(f"\nStarting processing of {len(questions)} questions...")
    start_time = time.time()
    
    results = processor.process_batch(questions, args.batch_size)
    
    total_time = time.time() - start_time
    print(f"\nTotal processing time: {total_time:.2f} seconds")
    
    # Save results
    processor.save_results(results, args.output)
    processor.save_detailed_results(results, args.detailed)
    
    # Print summary
    processor.print_summary(results)
    
    print(f"\n✅ Processing complete!")
    print(f"Results saved to: {args.output}")
    print(f"Detailed results saved to: {args.detailed}")


if __name__ == "__main__":
    main() 