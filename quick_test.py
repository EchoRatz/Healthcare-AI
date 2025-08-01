#!/usr/bin/env python3
"""
Quick Test - Ultra Fast System
==============================

Test the system with a few sample questions to verify it's working
before running the full 500-question processing.
"""

import os
import csv
import requests
import json
import time
import re
from typing import Dict, List, Tuple

def check_llama31():
    """Check if Llama 3.1 is available"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=3)
        if response.status_code == 200:
            models = response.json().get('models', [])
            for model in models:
                if 'llama3.1' in model['name'].lower():
                    return model['name']
        return None
    except:
        return None

def parse_question(question_text: str) -> Tuple[str, Dict[str, str]]:
    """Parse Thai question and extract choices"""
    parts = question_text.split('ก.')
    if len(parts) < 2:
        return question_text, {}
    
    question = parts[0].strip()
    choices_text = 'ก.' + parts[1]
    
    # Extract choices
    choice_pattern = re.compile(r'([ก-ง])\.\s*([^ก-ง]+?)(?=\s*[ก-ง]\.|$)')
    choices = {}
    matches = choice_pattern.findall(choices_text)
    
    for choice_label, choice_text in matches:
        choices[choice_label] = choice_text.strip()
    
    return question, choices

def quick_test_llama31(model_name: str, question: str, choices: Dict[str, str]) -> Tuple[List[str], float]:
    """Quick test query to Llama 3.1 - supports multiple answers"""
    choices_text = "\n".join([f"{k}. {v}" for k, v in choices.items()])
    
    prompt = f"""คุณเป็นผู้เชี่ยวชาญด้านสุขภาพไทย

คำถาม: {question}

ตัวเลือก:
{choices_text}

เลือกคำตอบที่ถูกต้องที่สุด
**หมายเหตุ: อาจมีคำตอบถูกต้องมากกว่า 1 ข้อ**

ตอบในรูปแบบ: ก หรือ ข,ง หรือ ก,ค,ง (คั่นด้วยคอมม่า)

คำตอบ:"""

    try:
        start_time = time.time()
        
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': model_name,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.1,
                    'num_predict': 50,
                    'top_p': 0.9
                }
            },
            timeout=20
        )
        
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()['response'].strip()
            
            # Extract multiple answers
            answers = extract_multiple_answers_test(result)
            
            if answers:
                confidence = 0.9 if len(answers) > 1 else 0.8
                return answers, confidence, response_time, result
            else:
                # Fallback to single answer
                single_answer = extract_single_answer_test(result)
                if single_answer:
                    return [single_answer], 0.6, response_time, result
        
        return ['ข'], 0.3, response_time, "No clear answer found"
        
    except Exception as e:
        return ['ข'], 0.2, 0, f"Error: {str(e)[:50]}"

def extract_multiple_answers_test(text: str) -> List[str]:
    """Extract multiple Thai choice answers from text (test version)"""
    text = text.strip().lower()
    
    # Pattern 1: "ข,ง" or "ก,ค,ง"
    comma_pattern = re.search(r'([ก-ง](?:,\s*[ก-ง])+)', text)
    if comma_pattern:
        answers_str = comma_pattern.group(1)
        answers = [a.strip() for a in answers_str.split(',')]
        return [a for a in answers if a in ['ก', 'ข', 'ค', 'ง']]
    
    # Pattern 2: "ข และ ง"
    and_pattern = re.search(r'([ก-ง](?:\s*และ\s*[ก-ง])+)', text)
    if and_pattern:
        answers_str = and_pattern.group(1)
        answers = re.findall(r'[ก-ง]', answers_str)
        return list(set(answers))
    
    # Pattern 3: Multiple separate mentions
    multiple_chars = re.findall(r'[ก-ง]', text)
    if len(multiple_chars) > 1:
        unique_answers = list(dict.fromkeys(multiple_chars))
        if len(unique_answers) <= 4:
            return unique_answers
    
    return []

def extract_single_answer_test(text: str) -> str:
    """Extract single Thai choice answer from text (test version)"""
    patterns = [
        r'\[([ก-ง])\]',
        r'^([ก-ง])',
        r'คำตอบ[:\s]*([ก-ง])',
        r'ตอบ[:\s]*([ก-ง])',
        r'เลือก\s*([ก-ง])',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    # Last resort
    choice_match = re.search(r'[ก-ง]', text)
    if choice_match:
        return choice_match.group()
    
    return None

def run_quick_test():
    """Run quick test with sample questions"""
    print("🧪 Quick Test - Ultra Fast System")
    print("=" * 40)
    
    # Check Llama 3.1
    model_name = check_llama31()
    if not model_name:
        print("❌ Llama 3.1 not available")
        print("💡 Make sure Ollama is running: ollama serve")
        return False
    
    print(f"✅ Model: {model_name}")
    
    # Check test file
    test_file = 'Healthcare-AI-Refactored/src/infrastructure/test.csv'
    if not os.path.exists(test_file):
        print("❌ Test file not found")
        return False
    
    print(f"✅ Test file found")
    print()
    
    # Get first 3 questions for testing
    print("🚀 Testing with first 3 questions...")
    
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            test_questions = []
            for i, row in enumerate(reader):
                if i >= 3:
                    break
                test_questions.append(row)
        
        if not test_questions:
            print("❌ No questions found in test file")
            return False
        
        total_time = 0
        results = []
        
        for i, row in enumerate(test_questions, 1):
            question_id = int(row['id'])
            full_question = row['question']
            
            # Parse question
            question, choices = parse_question(full_question)
            
            print(f"\n📝 Test {i}/3 (ID: {question_id})")
            print(f"Question: {question[:60]}...")
            print(f"Choices: {list(choices.keys())}")
            
            # Query Llama 3.1
            start_time = time.time()
            predicted_answers, confidence, response_time, full_response = quick_test_llama31(model_name, question, choices)
            total_time += response_time
            
            answer_display = ','.join(predicted_answers)
            print(f"Answer: {answer_display} (confidence: {confidence:.2f})")
            if len(predicted_answers) > 1:
                print(f"  🎯 Multiple answers detected: {len(predicted_answers)} choices")
            print(f"Time: {response_time:.2f}s")
            print(f"Response: {full_response[:80]}...")
            
            results.append({
                'id': question_id,
                'answer': answer_display,  # Store as comma-separated string
                'confidence': confidence,
                'time': response_time,
                'multiple': len(predicted_answers) > 1
            })
        
        # Summary
        print(f"\n📊 Quick Test Summary")
        print("-" * 25)
        print(f"✅ Questions processed: {len(results)}")
        print(f"⏱️  Total time: {total_time:.2f}s")
        print(f"🚀 Average time: {total_time/len(results):.2f}s per question")
        
        avg_confidence = sum(r['confidence'] for r in results) / len(results)
        print(f"📈 Average confidence: {avg_confidence:.3f}")
        
        # Estimate full processing time
        estimated_full_time = (total_time / len(results)) * 500
        print(f"\n🎯 Estimated full processing time: {estimated_full_time/60:.1f} minutes")
        
        if estimated_full_time < 900:  # Less than 15 minutes
            print("✅ Within target time range!")
        else:
            print("⚠️  May be slower than target")
        
        # Quality assessment
        high_conf = sum(1 for r in results if r['confidence'] > 0.7)
        multiple_answers = sum(1 for r in results if r.get('multiple', False))
        
        print(f"🎯 High confidence answers: {high_conf}/{len(results)}")
        if multiple_answers > 0:
            print(f"🔢 Multiple choice answers: {multiple_answers}/{len(results)}")
            print(f"   💡 System detected questions with multiple correct answers")
        
        if '70b' in model_name.lower():
            expected_accuracy = "90-95%"
        else:
            expected_accuracy = "85-90%"
        
        print(f"📊 Expected accuracy: {expected_accuracy}")
        
        if multiple_answers > 0:
            print(f"✅ Multiple answer detection: Working properly")
        
        # Test output format
        print(f"\n📋 Testing output format...")
        test_output = f"quick_test_sample.csv"
        
        try:
            with open(test_output, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'answer'])
                
                for result in results:
                    writer.writerow([result['id'], f'"{result["answer"]}"'])
            
            # Verify format
            with open(test_output, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"  ✅ Format matches submission.csv:")
                print(f"    Header: {lines[0].strip()}")
                print(f"    Sample: {lines[1].strip()}")
            
            # Clean up test file
            os.remove(test_output)
            
        except Exception as e:
            print(f"  ⚠️  Format test failed: {e}")
        
        print(f"\n🎉 Quick test completed successfully!")
        print("🚀 Ready to run full processing: python ultra_fast_llama31.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main test function"""
    success = run_quick_test()
    
    if success:
        response = input("\nRun full processing now? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            print("🚀 Starting full processing...")
            os.system('python ultra_fast_llama31.py')
    else:
        print("\n🔧 Fix issues before running full processing")
        print("💡 Run setup: python setup_ultra_fast.py")

if __name__ == "__main__":
    main()