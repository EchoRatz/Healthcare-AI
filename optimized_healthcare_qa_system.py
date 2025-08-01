#!/usr/bin/env python3
"""
Optimized Healthcare Q&A System
===============================

High-performance version with single-choice enforcement:
1. Optimized for speed (target: <5 minutes for 500 questions)
2. Single-choice answers only (no multiple answers)
3. Reduced LLM calls and context processing
4. Efficient caching and batching
5. Simplified validation logic
"""

import os
import sys
import csv
import json
import requests
import time
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class QuestionAnalysis:
    """Simplified question analysis for performance"""
    keywords: List[str]
    question_type: str
    confidence: float

@dataclass
class SingleAnswerResult:
    """Result with single choice answer"""
    answer: str  # Single choice: ก, ข, ค, or ง
    confidence: float
    reasoning: str

class OptimizedHealthcareQA:
    """High-performance healthcare Q&A system with single-choice enforcement"""

    def __init__(self):
        self.model_name = None
        self.knowledge_base = {}
        self.session = requests.Session()
        
        # Performance optimizations
        self.batch_size = 10
        self.max_context_length = 1500  # Reduced from 3000
        self.timeout = 15  # Reduced timeout
        
        # Load essential data
        self._load_essential_data()

    def _load_essential_data(self):
        """Load only essential data for performance"""
        # Load knowledge base efficiently
        knowledge_file = "AI/full_dataset_learned_knowledge.txt"
        if os.path.exists(knowledge_file):
            with open(knowledge_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self._build_fast_index(content)

    def _build_fast_index(self, content: str):
        """Build fast keyword index"""
        sections = content.split('\n\n')
        for section in sections:
            if len(section.strip()) < 50:  # Skip very short sections
                continue
            keywords = self._extract_keywords_fast(section)
            for keyword in keywords:
                if keyword not in self.knowledge_base:
                    self.knowledge_base[keyword] = []
                self.knowledge_base[keyword].append(section[:200])  # Store only first 200 chars

    def _extract_keywords_fast(self, text: str) -> List[str]:
        """Fast keyword extraction"""
        # Thai healthcare keywords
        thai_keywords = [
            "สิทธิ", "หลักประกัน", "สุขภาพ", "การรักษา", "ยา", "โรงพยาบาล", 
            "แพทย์", "แผนก", "ฉุกเฉิน", "ค่าใช้จ่าย", "เบิกจ่าย", "ประกัน",
            "ฟัน", "ทันตกรรม", "ผ่าตัด", "คลอด", "เด็ก", "ผู้สูงอายุ"
        ]
        
        found_keywords = []
        for keyword in thai_keywords:
            if keyword in text:
                found_keywords.append(keyword)
        
        return found_keywords[:5]  # Limit to 5 keywords for speed

    def check_llama31(self) -> bool:
        """Check if Llama 3.1 or Llama 3.2 is available (preferring 3.1)"""
        try:
            response = self.session.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                
                # First, look for llama3.1 (preferred)
                for model in models:
                    model_name = model.get("name", "").lower()
                    if "llama3.1" in model_name:
                        self.model_name = model["name"]
                        return True
                
                # If llama3.1 not found, look for llama3.2 as fallback
                for model in models:
                    model_name = model.get("name", "").lower()
                    if "llama3.2" in model_name:
                        self.model_name = model["name"]
                        print(f"⚠️  Llama 3.1 not found, using {model['name']} as fallback")
                        return True
                        
            return False
        except:
            return False

    def analyze_question_fast(self, question: str) -> QuestionAnalysis:
        """Fast question analysis"""
        keywords = self._extract_keywords_fast(question)
        
        # Simple question type detection
        if any(word in question for word in ["สิทธิ", "เบิกจ่าย", "ค่าใช้จ่าย"]):
            question_type = "benefits"
        elif any(word in question for word in ["แผนก", "แพทย์", "การรักษา"]):
            question_type = "treatment"
        elif any(word in question for word in ["ฉุกเฉิน", "วิกฤต"]):
            question_type = "emergency"
        else:
            question_type = "general"
        
        confidence = min(len(keywords) / 3.0, 1.0)
        
        return QuestionAnalysis(keywords, question_type, confidence)

    def search_context_fast(self, analysis: QuestionAnalysis) -> str:
        """Fast context search"""
        context_parts = []
        total_length = 0
        
        for keyword in analysis.keywords:
            if keyword in self.knowledge_base and total_length < self.max_context_length:
                sections = self.knowledge_base[keyword]
                for section in sections[:2]:  # Limit to 2 sections per keyword
                    if total_length + len(section) < self.max_context_length:
                        context_parts.append(section)
                        total_length += len(section)
        
        return "\n".join(context_parts)

    def parse_question_fast(self, question_text: str) -> Tuple[str, Dict[str, str]]:
        """Fast question parsing"""
        # Extract choices using regex
        choice_pattern = r'([ก-ง])\.\s*([^ก-ง\n]+)'
        choices = {}
        
        matches = re.findall(choice_pattern, question_text)
        for choice, text in matches:
            choices[choice] = text.strip()
        
        # Extract question (everything before choices)
        question = question_text
        for choice in choices:
            question = question.replace(f"{choice}. {choices[choice]}", "")
        
        question = question.strip()
        
        return question, choices

    def query_llama31_optimized(self, question: str, choices: Dict[str, str], context: str) -> SingleAnswerResult:
        """Optimized LLM query with single-choice enforcement"""
        try:
            # Build optimized prompt
            prompt = self._build_optimized_prompt(question, choices, context)
            
            payload = {
                "model": self.model_name or "llama3.1:latest",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower temperature for consistency
                    "top_p": 0.8,
                    "num_predict": 100,  # Reduced token limit
                    "stop": ["\n\n", "Question:", "คำถาม:"]
                }
            }
            
            response = self.session.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                answer_text = result.get("response", "").strip()
                
                # Extract single answer
                single_answer = self._extract_single_answer(answer_text, choices)
                confidence = self._calculate_confidence_fast(answer_text, choices)
                
                return SingleAnswerResult(
                    answer=single_answer,
                    confidence=confidence,
                    reasoning=answer_text[:100]  # Truncate reasoning
                )
            else:
                return SingleAnswerResult("ง", 0.0, "LLM error")
                
        except Exception as e:
            return SingleAnswerResult("ง", 0.0, f"Error: {str(e)}")

    def _build_optimized_prompt(self, question: str, choices: Dict[str, str], context: str) -> str:
        """Build optimized prompt for single-choice answers"""
        choices_text = "\n".join([f"{k}. {v}" for k, v in choices.items()])
        
        return f"""Based on the following context, answer the question with ONLY ONE choice (ก, ข, ค, or ง).

Context:
{context}

Question: {question}

Choices:
{choices_text}

IMPORTANT: Choose only ONE answer. Respond with just the letter (ก, ข, ค, or ง).

Answer:"""

    def _extract_single_answer(self, text: str, choices: Dict[str, str]) -> str:
        """Extract single answer, enforcing single-choice rule"""
        # Look for single choice patterns
        patterns = [
            r"คำตอบ[:\s]*([ก-ง])",
            r"ตอบ[:\s]*([ก-ง])",
            r"เลือก[:\s]*([ก-ง])",
            r"Answer[:\s]*([ก-ง])",
            r"^[ก-ง]$"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                answer = match.group(1)
                if answer in choices:
                    return answer
        
        # Fallback: find the first ก-ง in the text
        answers = re.findall(r'[ก-ง]', text)
        if answers:
            # If multiple found, take the first one that's a valid choice
            for answer in answers:
                if answer in choices:
                    return answer
        
        # Default to ง if no valid answer found
        return "ง"

    def _calculate_confidence_fast(self, answer_text: str, choices: Dict[str, str]) -> float:
        """Fast confidence calculation"""
        confidence = 0.5  # Base confidence
        
        # Higher confidence if answer is clear
        if "คำตอบ" in answer_text or "ตอบ" in answer_text:
            confidence += 0.2
        
        # Lower confidence if answer is "ง" (none of the above)
        if "ง" in answer_text and len(answer_text) < 30:
            confidence -= 0.1
        
        return min(max(confidence, 0.0), 1.0)

    def process_questions_optimized(self, test_file: str) -> List[Dict]:
        """Optimized batch processing with single-choice enforcement"""
        if not self.check_llama31():
            print("❌ No Llama 3.1 or Llama 3.2 available")
            print("Please ensure a Llama model is installed and running:")
            print("  - Preferred: ollama pull llama3.1")
            print("  - Alternative: ollama pull llama3.2")
            return []

        print(f"✅ Using model: {self.model_name}")
        print("🚀 Starting optimized processing with single-choice enforcement...")

        # Load questions
        questions = []
        with open(test_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                questions.append(row)

        print(f"📊 Processing {len(questions)} questions...")

        results = []
        start_time = time.time()
        
        # Process in batches for better performance
        for i in range(0, len(questions), self.batch_size):
            batch = questions[i:i + self.batch_size]
            batch_results = self._process_batch(batch)
            results.extend(batch_results)
            
            # Progress update
            processed = min(i + self.batch_size, len(questions))
            elapsed = time.time() - start_time
            rate = processed / elapsed if elapsed > 0 else 0
            eta = (len(questions) - processed) / rate if rate > 0 else 0
            
            print(f"  📈 {processed}/{len(questions)} ({processed/len(questions)*100:.1f}%) | Rate: {rate:.1f} q/s | ETA: {eta/60:.1f}min")

        total_time = time.time() - start_time
        print(f"🎉 Optimized processing complete!")
        print(f"⏱️  Total time: {total_time/60:.1f} minutes")
        print(f"⚡ Average rate: {len(questions)/total_time:.1f} questions/second")

        return results

    def _process_batch(self, batch: List[Dict]) -> List[Dict]:
        """Process a batch of questions"""
        batch_results = []
        
        for row in batch:
            question_id = row['id']
            question_text = row['question']

            # Parse question
            question, choices = self.parse_question_fast(question_text)

            # Analyze question
            analysis = self.analyze_question_fast(question)

            # Search for context
            context = self.search_context_fast(analysis)

            # Query LLM with single-choice enforcement
            result = self.query_llama31_optimized(question, choices, context)

            batch_results.append({
                'id': question_id,
                'answer': result.answer,  # Single choice only
                'confidence': result.confidence,
                'reasoning': result.reasoning
            })

        return batch_results

    def save_results(self, results: List[Dict], output_file: str):
        """Save results to CSV"""
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'answer'])
            writer.writeheader()
            for result in results:
                writer.writerow({
                    'id': result['id'],
                    'answer': result['answer']
                })
        print(f"💾 Results saved to {output_file}")

def main():
    """Main function"""
    print("🏥 Optimized Healthcare Q&A System")
    print("=" * 50)
    
    qa_system = OptimizedHealthcareQA()
    
    # Process questions
    test_file = "AI/test_answers_with_cache.csv"
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return
    
    results = qa_system.process_questions_optimized(test_file)
    
    if results:
        output_file = "optimized_healthcare_submission.csv"
        qa_system.save_results(results, output_file)
        
        # Print summary
        single_answers = [r['answer'] for r in results if len(r['answer']) == 1]
        print(f"📊 Summary:")
        print(f"  Total questions: {len(results)}")
        print(f"  Single-choice answers: {len(single_answers)}")
        print(f"  Average confidence: {sum(r['confidence'] for r in results)/len(results):.2f}")

if __name__ == "__main__":
    main() 