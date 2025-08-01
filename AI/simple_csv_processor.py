#!/usr/bin/env python3
"""
Simple CSV processor that can work without heavy ML dependencies
For testing and demonstrating the CSV processing workflow
"""

import csv
import os
import re
from datetime import datetime


class SimpleThaiQA:
    """Simple Thai Q&A processor for testing CSV workflow"""
    
    def __init__(self):
        """Initialize the simple processor"""
        print("🔧 Initializing Simple Thai Q&A Processor...")
        print("   ⚠️  Note: This is a demo version for CSV processing workflow")
        print("   📚 For actual AI answers, install langchain dependencies and Ollama")
        
    def parse_question(self, question_text: str) -> dict:
        """Parse question and extract choices"""
        try:
            # Split question from choices
            lines = question_text.strip().split()
            
            # Find where choices start (look for ก.)
            question_parts = []
            choices = {}
            current_section = "question"
            
            for i, word in enumerate(lines):
                if re.match(r'^[ก-ง]\.', word):
                    current_section = "choices"
                    # Extract choice
                    choice_match = re.match(r'^([ก-ง])\.(.+)', ' '.join(lines[i:]))
                    if choice_match:
                        letter = choice_match.group(1)
                        # Find the rest of this choice
                        choice_text = []
                        j = i + 1
                        while j < len(lines) and not re.match(r'^[ก-ง]\.', lines[j]):
                            choice_text.append(lines[j])
                            j += 1
                        
                        full_choice = word[2:] + ' ' + ' '.join(choice_text) if choice_text else word[2:]
                        choices[letter] = full_choice.strip()
                elif current_section == "question":
                    question_parts.append(word)
            
            question = ' '.join(question_parts)
            
            return {
                "question": question,
                "choices": choices
            }
            
        except Exception as e:
            return {
                "question": question_text,
                "choices": {}
            }
    
    def answer_question(self, question_text: str) -> str:
        """Simple rule-based answering for demo purposes"""
        
        # Parse the question
        parsed = self.parse_question(question_text)
        question = parsed["question"]
        choices = parsed["choices"]
        
        if not choices:
            return "ไม่สามารถแยกวิเคราะห์ตัวเลือกได้"
        
        # Simple rule-based logic for demonstration
        question_lower = question.lower()
        
        # Emergency-related keywords
        if any(word in question_lower for word in ['ปวดท้อง', 'อ้วก', 'ตีสอง', 'ฉุกเฉิน']):
            if 'emergency' in str(choices).lower() or 'ฉุกเฉิน' in str(choices):
                return 'ค'
        
        # Time-related or specific department questions
        if 'แผนก' in question:
            if 'emergency' in str(choices).lower():
                return 'ค'
            elif 'orthopedics' in str(choices).lower() and ('ปวดหลัง' in question or 'กระดูก' in question):
                return 'ข'
            elif 'cardiology' in str(choices).lower() and ('หัวใจ' in question or 'เจ็บหน้าอก' in question):
                return 'ก'
        
        # Medicine/drug related
        if 'ยา' in question or 'บาท' in question:
            # Usually middle options for pricing
            return 'ข'
            
        # Rights and benefits related
        if 'สิทธิ' in question or 'หลักประกัน' in question:
            if 'ไม่' in question and 'ถูกต้อง' in str(choices):
                return 'ง'
            else:
                return 'ก'
        
        # Age-related questions
        if 'อายุ' in question and 'ปี' in question:
            return 'ข'  # Usually middle age ranges
            
        # Default fallback - choose first option
        available_choices = list(choices.keys())
        if available_choices:
            return available_choices[0]
        
        return 'ก'  # Ultimate fallback
    
    def process_csv_questions(self, csv_file_path: str, output_file_path: str = None) -> None:
        """Process all questions from CSV file"""
        
        if output_file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file_path = f"simple_answers_{timestamp}.csv"
        
        print(f"📝 Processing: {csv_file_path}")
        print(f"💾 Output: {output_file_path}")
        print("=" * 50)
        
        results = []
        
        try:
            # Read CSV file
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                questions = list(reader)
            
            total_questions = len(questions)
            print(f"📊 Found {total_questions} questions")
            print()
            
            # Process each question
            for i, row in enumerate(questions, 1):
                question_id = row['id']
                question_text = row['question']
                
                print(f"⏳ Processing Q{question_id} ({i}/{total_questions})")
                
                try:
                    answer = self.answer_question(question_text)
                    
                    results.append({
                        'id': question_id,
                        'question': question_text,
                        'answer': answer
                    })
                    
                    print(f"   ✅ Answer: {answer}")
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    results.append({
                        'id': question_id,
                        'question': question_text,
                        'answer': error_msg
                    })
                    print(f"   ❌ {error_msg}")
                
                # Show progress every 25 questions
                if i % 25 == 0:
                    print(f"   📈 Progress: {i}/{total_questions} ({(i/total_questions)*100:.1f}%)")
                    print()
            
            # Save results
            with open(output_file_path, 'w', encoding='utf-8', newline='') as file:
                fieldnames = ['id', 'question', 'answer']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            
            # Summary
            successful = len([r for r in results if not r['answer'].startswith('Error')])
            errors = len([r for r in results if r['answer'].startswith('Error')])
            
            print("=" * 50)
            print("🎉 Processing Complete!")
            print(f"📊 Statistics:")
            print(f"   - Total questions: {total_questions}")
            print(f"   - Successful: {successful}")
            print(f"   - Errors: {errors}")
            print(f"   - Success rate: {(successful/total_questions)*100:.1f}%")
            print(f"📁 Results saved to: {output_file_path}")
            
            # Show sample results
            print(f"\n📋 Sample Results:")
            for i, result in enumerate(results[:5]):
                print(f"   Q{result['id']}: {result['answer']}")
            if len(results) > 5:
                print("   ...")
                
        except Exception as e:
            print(f"❌ Error processing CSV: {str(e)}")


def main():
    """Main function"""
    
    # Look for test.csv
    csv_file = None
    possible_paths = ["test.csv", "../test.csv", "AI/test.csv"]
    
    for path in possible_paths:
        if os.path.exists(path):
            csv_file = path
            break
    
    if not csv_file:
        print("❌ test.csv not found!")
        print("🔍 Looking in:", possible_paths)
        return
    
    print("🎯 Simple Thai Healthcare Q&A CSV Processor")
    print("=" * 60)
    print("⚠️  DEMO VERSION - Uses simple rule-based logic")
    print("📚 For AI-powered answers, use the full system with Ollama")
    print("=" * 60)
    
    # Initialize processor
    processor = SimpleThaiQA()
    
    print(f"\n📁 Found CSV file: {csv_file}")
    
    # Process the CSV
    processor.process_csv_questions(csv_file, "simple_test_answers.csv")
    
    print("\n💡 Next Steps:")
    print("   1. Install dependencies: pip install langchain-ollama langchain-chroma")
    print("   2. Install Ollama and models: ollama pull llama3.2")
    print("   3. Run full system: python batch_test_processor.py")


if __name__ == "__main__":
    main()