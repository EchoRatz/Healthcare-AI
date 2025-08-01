#!/usr/bin/env python3
"""
Process test.csv and generate clean CSV output with just id,answer columns
"""

from thai_qa_processor import ThaiHealthcareQA
import csv
import time

def process_test_csv():
    """Process test.csv and create clean id,answer CSV output"""
    print("🚀 Processing test.csv with Intelligent Knowledge Caching")
    print("=" * 60)
    print("Output: Clean CSV with id,answer columns only")
    print("=" * 60)
    
    # Initialize the system
    print("\n🔧 Initializing Thai Healthcare Q&A System...")
    qa_system = ThaiHealthcareQA()
    
    # Show initial cache
    print("📊 Initial knowledge cache:")
    qa_system.show_cache_stats()
    
    start_time = time.time()
    
    try:
        # Read the test CSV
        print(f"\n📖 Reading test.csv...")
        with open('test.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            questions = list(reader)
        
        total_questions = len(questions)
        print(f"📝 Found {total_questions} questions to process")
        print("\n" + "=" * 60)
        
        # Prepare results for clean CSV
        results = []
        
        # Process each question
        for i, row in enumerate(questions, 1):
            question_id = row['id']
            question_text = row['question']
            
            print(f"⏳ Processing question {i}/{total_questions} (ID: {question_id})")
            
            try:
                # Get answer from AI
                answer = qa_system.answer_question(question_text)
                
                # Clean up answer (remove extra whitespace, newlines)
                clean_answer = ' '.join(answer.split())
                
                # Add to results - ONLY id and answer (no question)
                results.append({
                    'id': question_id,
                    'answer': clean_answer
                })
                
                print(f"✅ Answer: {clean_answer[:50]}{'...' if len(clean_answer) > 50 else ''}")
                
            except Exception as e:
                print(f"❌ Error processing question {question_id}: {str(e)}")
                results.append({
                    'id': question_id,
                    'answer': f"Error: {str(e)}"
                })
            
            print("-" * 40)
            
            # Save periodically (every 50 questions)
            if i % 50 == 0:
                save_results(results, 'test_answers_clean.csv')
                print(f"💾 Saved {len(results)} answers so far...")
        
        # Save final results
        save_results(results, 'test_answers_clean.csv')
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print("\n" + "=" * 60)
        print("🎉 Processing Complete!")
        print(f"⏱️  Total time: {processing_time:.1f} seconds")
        print(f"📝 Questions processed: {len(results)}")
        print(f"✅ Output saved to: test_answers_clean.csv")
        print("=" * 60)
        
        # Show final cache stats
        print("\n📊 Final knowledge cache:")
        qa_system.show_cache_stats()
        
        # Export learned knowledge
        qa_system.export_cache_to_text("test_learned_knowledge.txt")
        print("💾 Learned knowledge exported to: test_learned_knowledge.txt")
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")

def save_results(results, filename):
    """Save results to CSV with clean id,answer format"""
    with open(filename, 'w', encoding='utf-8', newline='') as file:
        # Write ONLY id,answer columns (no question column)
        fieldnames = ['id', 'answer']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    try:
        process_test_csv()
    except KeyboardInterrupt:
        print("\n\n⏸️  Processing interrupted by user")
        print("💾 Partial results may have been saved to test_answers_clean.csv")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Make sure Ollama is running and required models are available")