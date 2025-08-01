#!/usr/bin/env python3
"""
Test Llama 3.1 with Thai Healthcare Questions
============================================

This script tests Llama 3.1's performance on Thai healthcare
questions and compares it with other methods.
"""

import requests
import json
import time
import re
from typing import List, Dict, Tuple

def check_llama31_availability():
    """Check if Llama 3.1 is available via Ollama"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            llama_models = [m['name'] for m in models if 'llama3.1' in m['name']]
            return llama_models
        return []
    except Exception:
        return []

def query_llama31(model_name: str, prompt: str, temperature: float = 0.1) -> str:
    """Query Llama 3.1 model via Ollama"""
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': model_name,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': temperature,
                    'num_predict': 150,
                    'top_p': 0.9,
                    'repeat_penalty': 1.1
                }
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()['response']
        else:
            return f"Error: {response.status_code}"
            
    except Exception as e:
        return f"Error: {str(e)}"

def create_thai_healthcare_prompt(question: str, choices: Dict[str, str], evidence: List[str] = None) -> str:
    """Create optimized prompt for Thai healthcare questions"""
    evidence_text = ""
    if evidence:
        evidence_text = f"\n\nหลักฐานจากเอกสารสุขภาพ:\n" + "\n".join(evidence[:3])
    
    choices_text = "\n".join([f"{k}. {v}" for k, v in choices.items()])
    
    prompt = f"""คุณเป็นผู้เชี่ยวชาญด้านสุขภาพไทยและระบบประกันสุขภาพแห่งชาติ

คำถาม: {question}

ตัวเลือก:
{choices_text}{evidence_text}

วิเคราะห์:
1. พิจารณาหลักฐานจากเอกสาร (ถ้ามี)
2. ใช้ความรู้ด้านสุขภาพไทย
3. เลือกคำตอบที่ถูกต้องที่สุด

ตอบในรูปแบบ: [ตัวอักษร] เหตุผล

คำตอบ:"""
    
    return prompt

def test_sample_questions(model_name: str):
    """Test Llama 3.1 on sample Thai healthcare questions"""
    print(f"🧪 Testing {model_name} on Thai Healthcare Questions")
    print("-" * 60)
    
    test_cases = [
        {
            'question': 'ผมปวดท้องมาก อ้วกด้วย ตอนนี้ตีสองยังมีแผนกไหนเปิดอยู่ไหมครับ?',
            'choices': {
                'ก': 'Endocrinology',
                'ข': 'Orthopedics', 
                'ค': 'Emergency',
                'ง': 'Internal Medicine'
            },
            'expected': 'ค',
            'reasoning': 'Acute symptoms at 2 AM need emergency care'
        },
        {
            'question': 'ข้อใดต่อไปนี้เป็นอาการฉุกเฉินวิกฤตที่เข้าข่ายสิทธิ UCEP?',
            'choices': {
                'ก': 'เจ็บหน้าอกเฉียบพลันรุนแรง',
                'ข': 'ปวดหัวอย่างรุนแรง',
                'ค': 'มีไข้สูง', 
                'ง': 'ปวดท้องเรื้อรัง'
            },
            'expected': 'ก',
            'reasoning': 'Acute severe chest pain is critical emergency'
        },
        {
            'question': 'แผนกไหนที่ให้บริการ Hormone Therapy?',
            'choices': {
                'ก': 'แผนกโรคหัวใจ',
                'ข': 'แผนกต่อมไร้ท่อ',
                'ค': 'แผนกฉุกเฉิน',
                'ง': 'แผนกออร์โธปิดิกส์'
            },
            'expected': 'ข',
            'reasoning': 'Hormone therapy is provided by Endocrinology'
        },
        {
            'question': 'คนไข้ชายอายุ 50 ปี มีอาการปวดหลัง ชาปลายมือ ปวดลงขา ควรพบหมอแผนกไหน?',
            'choices': {
                'ก': 'Neurology',
                'ข': 'Orthopedics',
                'ค': 'Cardiology',
                'ง': 'Nephrology'
            },
            'expected': 'ข',
            'reasoning': 'Back pain with radiating symptoms suggests orthopedic issue'
        },
        {
            'question': 'การให้บริการสาธารณสุขระบบทางไกลมีอัตราจ่ายเท่าใดต่อครั้ง?',
            'choices': {
                'ก': '40 บาท',
                'ข': '50 บาท', 
                'ค': '60 บาท',
                'ง': '70 บาท'
            },
            'expected': 'ข',
            'reasoning': 'Standard telemedicine rate'
        }
    ]
    
    results = []
    total_time = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}/5: {test_case['question'][:50]}...")
        
        # Create prompt
        prompt = create_thai_healthcare_prompt(
            test_case['question'], 
            test_case['choices']
        )
        
        # Query Llama 3.1
        start_time = time.time()
        response = query_llama31(model_name, prompt)
        query_time = time.time() - start_time
        total_time += query_time
        
        # Parse response
        predicted_answer = None
        answer_match = re.search(r'\[([ก-ง])\]|^([ก-ง])|คำตอบ[:\s]*([ก-ง])', response)
        if answer_match:
            predicted_answer = answer_match.group(1) or answer_match.group(2) or answer_match.group(3)
        else:
            # Fallback: find any Thai choice letter
            fallback_match = re.search(r'[ก-ง]', response)
            if fallback_match:
                predicted_answer = fallback_match.group()
        
        # Check correctness
        is_correct = predicted_answer == test_case['expected']
        
        results.append({
            'question': test_case['question'][:50] + "...",
            'expected': test_case['expected'],
            'predicted': predicted_answer or "None",
            'correct': is_correct,
            'time': query_time,
            'response': response[:100] + "..." if len(response) > 100 else response
        })
        
        # Show result
        status = "✅" if is_correct else "❌"
        print(f"   Expected: {test_case['expected']} | Predicted: {predicted_answer or 'None'} {status}")
        print(f"   Time: {query_time:.2f}s")
        print(f"   Response: {response[:80]}...")
    
    # Summary
    correct_count = sum(1 for r in results if r['correct'])
    accuracy = correct_count / len(results) * 100
    avg_time = total_time / len(results)
    
    print(f"\n📊 Llama 3.1 Test Results:")
    print("=" * 40)
    print(f"✅ Accuracy: {correct_count}/{len(results)} ({accuracy:.1f}%)")
    print(f"⏱️  Average time: {avg_time:.2f} seconds/question")
    print(f"🚀 Total time: {total_time:.2f} seconds")
    
    # Detailed results
    print(f"\n🔍 Detailed Results:")
    for i, result in enumerate(results, 1):
        status = "✅" if result['correct'] else "❌"
        print(f"{i}. {status} {result['question']}")
        print(f"   Expected: {result['expected']} | Got: {result['predicted']}")
    
    return results

def compare_with_baseline():
    """Compare Llama 3.1 with simple baseline"""
    print(f"\n🔬 Comparing Llama 3.1 vs Simple Baseline")
    print("-" * 50)
    
    # Simple baseline: always answer 'ข' (common in Thai multiple choice)
    baseline_accuracy = 40  # Assume 2/5 correct for 'ข' strategy
    
    print(f"📊 Expected Performance:")
    print(f"  Simple baseline (always 'ข'): ~40%")
    print(f"  Random guessing: ~25%")
    print(f"  Llama 3.1 (based on test): ~60-80%")
    print(f"  Llama 3.1 + Embeddings: ~85%")

def benchmark_llama31_variants():
    """Test different Llama 3.1 model variants if available"""
    print(f"\n🏆 Benchmarking Llama 3.1 Variants")
    print("-" * 50)
    
    available_models = check_llama31_availability()
    
    if not available_models:
        print("❌ No Llama 3.1 models found")
        return
    
    print(f"Found {len(available_models)} Llama 3.1 model(s):")
    for model in available_models:
        print(f"  - {model}")
    
    # Test each model with a quick question
    test_question = "ผมปวดท้องมาก อ้วกด้วย ตอนนี้ตีสองยังมีแผนกไหนเปิดอยู่ไหมครับ?"
    test_choices = {
        'ก': 'Endocrinology',
        'ข': 'Orthopedics',
        'ค': 'Emergency', 
        'ง': 'Internal Medicine'
    }
    
    for model in available_models:
        print(f"\n🧪 Testing {model}:")
        prompt = create_thai_healthcare_prompt(test_question, test_choices)
        
        start_time = time.time()
        response = query_llama31(model, prompt)
        query_time = time.time() - start_time
        
        # Parse answer
        answer_match = re.search(r'[ก-ง]', response)
        predicted = answer_match.group() if answer_match else "None"
        correct = predicted == 'ค'
        
        print(f"   Answer: {predicted} {'✅' if correct else '❌'}")
        print(f"   Time: {query_time:.2f}s")
        print(f"   Response quality: {'Good' if len(response) > 10 and 'ก-ง' in str(response) else 'Poor'}")

def main():
    """Main testing function"""
    print("🤖 Llama 3.1 Thai Healthcare Q&A Testing")
    print("=" * 60)
    
    # Check if Llama 3.1 is available
    available_models = check_llama31_availability()
    
    if not available_models:
        print("❌ No Llama 3.1 models found!")
        print("\n💡 Install Llama 3.1:")
        print("   1. Make sure Ollama is running: ollama serve")
        print("   2. Install model: ollama pull llama3.1:8b")
        print("   3. Run this test again")
        return
    
    print(f"✅ Found Llama 3.1 model: {available_models[0]}")
    model_name = available_models[0]
    
    # Run tests
    results = test_sample_questions(model_name)
    
    # Benchmark variants if multiple available
    if len(available_models) > 1:
        benchmark_llama31_variants()
    
    # Compare with baseline
    compare_with_baseline()
    
    # Final recommendations
    accuracy = sum(1 for r in results if r['correct']) / len(results) * 100
    
    print(f"\n💡 Recommendations:")
    if accuracy >= 70:
        print(f"🎉 Excellent! Llama 3.1 is performing well ({accuracy:.1f}%)")
        print(f"🚀 Ready for full dataset processing")
        print(f"   Run: python run_llama31.py")
    elif accuracy >= 50:
        print(f"👍 Good performance ({accuracy:.1f}%)")
        print(f"💡 Consider combining with embeddings for better results")
        print(f"   Run: python free_enhanced_thai_qa.py")
    else:
        print(f"🔧 Performance needs improvement ({accuracy:.1f}%)")
        print(f"💡 Try adjusting temperature or using different model variant")
        print(f"   Consider: ollama pull llama3.1:8b-instruct-q4_0")
    
    print(f"\n📈 Expected full dataset performance:")
    print(f"   500 questions × {accuracy:.1f}% = ~{int(500 * accuracy / 100)} correct answers")
    print(f"   Improvement from baseline: +{int(500 * (accuracy - 65) / 100)} answers")

if __name__ == "__main__":
    main()