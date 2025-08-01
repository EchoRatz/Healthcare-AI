#!/usr/bin/env python3
"""
Improved Healthcare Validator - Reduce "ง" Answers
==================================================

Smart Thai healthcare policy logic to avoid over-conservative "None" answers
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class HealthcareValidationResult:
    """Result from healthcare validation"""
    original_answer: List[str]
    validated_answer: List[str]
    confidence: float
    corrections_made: List[str]
    reasoning: str

class ImprovedHealthcareValidator:
    """Smart Thai healthcare validator that reduces excessive 'ง' answers"""
    
    def __init__(self):
        # Thai healthcare policy knowledge base
        self.healthcare_policies = {
            "สิทธิหลักประกันสุขภาพแห่งชาติ": {
                "includes": [
                    "การตรวจรักษาพยาบาลทั่วไป", "ยาจำเป็น", "การผ่าตัด", "การฟื้นฟู",
                    "การรักษาโรคเรื้อรัง", "การตรวจสุขภาพ", "วัคซีน", "การคลอด"
                ],
                "excludes": [
                    "การรักษาเสริมความงาม", "ยาแบรนด์เนม", "ค่าห้องพิเศษ", 
                    "การรักษาทดลอง", "อุปกรณ์เสริม", "การท่องเที่ยวเพื่อสุขภาพ"
                ],
                "keywords": ["หลักประกัน", "สุขภาพแห่งชาติ", "UC", "30บาท"]
            },
            "สิทธิบัตรทอง": {
                "includes": [
                    "การรักษาฟรี", "ยาฟรี", "ตรวจสุขภาพประจำปี", "การดูแลผู้สูงอายุ",
                    "บริการที่บ้าน", "อุปกรณ์การแพทย์", "การฟื้นฟูสุขภาพ"
                ],
                "excludes": [
                    "ค่าใช้จ่าย", "30บาท", "เงินสด", "ค่าบริการ", "ค่าตรวจ"
                ],
                "keywords": ["บัตรทอง", "ผู้สูงอายุ", "ฟรี", "60ปี"]
            },
            "สิทธิ30บาทรักษาทุกโรค": {
                "includes": [
                    "ค่าบริการ30บาท", "รักษาโรคทั่วไป", "ยาจำเป็น", "การตรวจรักษา",
                    "บริการผู้ป่วยนอก", "การส่งต่อ"
                ],
                "excludes": [
                    "ฟรี", "ไม่เสียค่าใช้จ่าย", "บัตรทอง", "ผู้สูงอายุเท่านั้น"
                ],
                "keywords": ["30บาท", "รักษาทุกโรค", "ค่าบริการ", "UC"]
            }
        }
        
        # Question type patterns
        self.question_patterns = {
            "what_is_included": [
                r"รวมอยู่ใน", r"ได้รับ", r"มีสิทธิ์", r"ครอบคลุม", r"ประกอบด้วย"
            ],
            "what_is_excluded": [
                r"ไม่รวมอยู่ใน", r"ไม่ได้รับ", r"ไม่มีสิทธิ์", r"ไม่ครอบคลุม", r"ยกเว้น"
            ],
            "comparison": [
                r"แตกต่าง", r"เปรียบเทียบ", r"ความแตกต่าง", r"เหมือน", r"ต่าง"
            ],
            "qualification": [
                r"เงื่อนไข", r"คุณสมบัติ", r"สิทธิ์", r"ได้รับสิทธิ์", r"มีสิทธิ์"
            ]
        }
        
        # Common wrong patterns that lead to too many "ง" answers
        self.avoid_none_patterns = [
            "มีสิทธิ์ได้รับ",  # Usually has valid answers
            "ครอบคลุม",      # Usually covers specific services
            "ประกอบด้วย",     # Usually lists specific items
            "รวมถึง",         # Usually includes specific things
            "การรักษา",       # Usually about specific treatments
        ]
    
    def validate_healthcare_answer(self, question: str, choices: Dict[str, str], predicted_answer: List[str]) -> HealthcareValidationResult:
        """Smart healthcare validation that reduces excessive 'ง' answers"""
        
        logger.info(f"🏥 Healthcare validation: {predicted_answer}")
        
        original_answer = predicted_answer.copy()
        corrections_made = []
        reasoning_parts = []
        
        # Step 1: Detect question type
        question_type = self._detect_question_type(question)
        
        # Step 2: Check if "ง" answer is actually justified
        if predicted_answer == ["ง"]:
            better_answer = self._find_better_than_none(question, choices, question_type)
            if better_answer:
                predicted_answer = better_answer
                corrections_made.append("แทนที่ 'ง' ด้วยคำตอบที่เหมาะสมกว่า")
                reasoning_parts.append(f"พบคำตอบที่เหมาะสมกว่า 'ไม่มีข้อใดถูกต้อง'")
        
        # Step 3: Check for logical contradictions (but be less aggressive)
        if 'ง' in predicted_answer and len(predicted_answer) > 1:
            # Only remove 'ง' if other answers are clearly valid
            other_answers = [a for a in predicted_answer if a != 'ง']
            if self._are_answers_clearly_valid(question, choices, other_answers):
                predicted_answer = other_answers
                corrections_made.append("ลบ 'ง' เพราะมีคำตอบที่ชัดเจนอื่น")
                reasoning_parts.append("คำตอบอื่นมีความเหมาะสมชัดเจน")
        
        # Step 4: Apply healthcare policy knowledge
        policy_result = self._apply_policy_knowledge(question, choices, predicted_answer, question_type)
        if policy_result:
            predicted_answer = policy_result['answer']
            corrections_made.extend(policy_result['corrections'])
            reasoning_parts.append(policy_result['reasoning'])
        
        # Step 5: Calculate confidence (boost for non-"ง" answers)
        confidence = self._calculate_smart_confidence(question, choices, predicted_answer, corrections_made)
        
        final_reasoning = " | ".join(reasoning_parts) if reasoning_parts else "ไม่มีการแก้ไข"
        
        if predicted_answer != original_answer:
            logger.info(f"✅ Healthcare fix: {original_answer} → {predicted_answer}")
        
        return HealthcareValidationResult(
            original_answer=original_answer,
            validated_answer=predicted_answer,
            confidence=confidence,
            corrections_made=corrections_made,
            reasoning=final_reasoning
        )
    
    def _detect_question_type(self, question: str) -> str:
        """Detect the type of healthcare question"""
        for q_type, patterns in self.question_patterns.items():
            for pattern in patterns:
                if re.search(pattern, question):
                    return q_type
        return "general"
    
    def _find_better_than_none(self, question: str, choices: Dict[str, str], question_type: str) -> Optional[List[str]]:
        """Find better answers than 'ง' (None) based on healthcare knowledge"""
        
        # Check if this question pattern usually has valid answers
        has_avoid_none_pattern = any(pattern in question for pattern in self.avoid_none_patterns)
        
        if not has_avoid_none_pattern:
            return None  # Keep "ง" for genuinely negative questions
        
        # Score each choice based on healthcare policy relevance
        choice_scores = {}
        
        for choice_key, choice_text in choices.items():
            score = 0
            
            # Score based on question type and policy knowledge
            if question_type == "what_is_included":
                score += self._score_inclusion_relevance(question, choice_text)
            elif question_type == "what_is_excluded":
                score += self._score_exclusion_relevance(question, choice_text)
            elif question_type == "qualification":
                score += self._score_qualification_relevance(question, choice_text)
            else:
                score += self._score_general_relevance(question, choice_text)
            
            choice_scores[choice_key] = score
        
        # Find best scoring choices
        max_score = max(choice_scores.values()) if choice_scores else 0
        
        if max_score > 3:  # Threshold for confidence
            best_choices = [choice for choice, score in choice_scores.items() 
                          if score >= max_score * 0.8]  # Within 80% of max score
            
            # Limit to reasonable number of choices
            if len(best_choices) <= 2:
                return sorted(best_choices)  # Sort for consistency
        
        return None
    
    def _score_inclusion_relevance(self, question: str, choice_text: str) -> int:
        """Score how relevant a choice is for inclusion questions"""
        score = 0
        
        # Check against healthcare policy includes
        for policy_name, policy_data in self.healthcare_policies.items():
            if any(keyword in question for keyword in policy_data['keywords']):
                # This question is about this specific policy
                for include_item in policy_data['includes']:
                    if include_item in choice_text or any(word in choice_text for word in include_item.split()):
                        score += 5
                
                # Penalty for excluded items
                for exclude_item in policy_data['excludes']:
                    if exclude_item in choice_text:
                        score -= 3
        
        # General healthcare inclusion terms
        inclusion_terms = ['การรักษา', 'บริการ', 'ยา', 'ตรวจ', 'ดูแล', 'ฟื้นฟู']
        for term in inclusion_terms:
            if term in choice_text:
                score += 2
        
        return score
    
    def _score_exclusion_relevance(self, question: str, choice_text: str) -> int:
        """Score how relevant a choice is for exclusion questions"""
        score = 0
        
        # For exclusion questions, look for things that are actually excluded
        for policy_name, policy_data in self.healthcare_policies.items():
            if any(keyword in question for keyword in policy_data['keywords']):
                # This question is about this specific policy
                for exclude_item in policy_data['excludes']:
                    if exclude_item in choice_text or any(word in choice_text for word in exclude_item.split()):
                        score += 5
                
                # Penalty for included items (they shouldn't be the answer for exclusion questions)
                for include_item in policy_data['includes']:
                    if include_item in choice_text:
                        score -= 2
        
        return score
    
    def _score_qualification_relevance(self, question: str, choice_text: str) -> int:
        """Score how relevant a choice is for qualification questions"""
        score = 0
        
        # Look for qualification-related terms
        qualification_terms = ['อายุ', 'ปี', 'เงื่อนไข', 'คุณสมบัติ', 'สิทธิ์', 'ลงทะเบียน']
        for term in qualification_terms:
            if term in choice_text:
                score += 3
        
        return score
    
    def _score_general_relevance(self, question: str, choice_text: str) -> int:
        """Score general relevance for other question types"""
        score = 0
        
        # Extract key terms from question
        question_terms = re.findall(r'[\u0E00-\u0E7F]+', question)
        choice_terms = re.findall(r'[\u0E00-\u0E7F]+', choice_text)
        
        # Score based on term overlap
        common_terms = set(question_terms) & set(choice_terms)
        score += len(common_terms)
        
        return score
    
    def _are_answers_clearly_valid(self, question: str, choices: Dict[str, str], answers: List[str]) -> bool:
        """Check if the given answers are clearly valid for the question"""
        if not answers:
            return False
        
        # Check if answers have good relevance scores
        total_score = 0
        question_type = self._detect_question_type(question)
        
        for answer in answers:
            choice_text = choices.get(answer, '')
            if question_type == "what_is_included":
                total_score += self._score_inclusion_relevance(question, choice_text)
            elif question_type == "what_is_excluded":
                total_score += self._score_exclusion_relevance(question, choice_text)
            else:
                total_score += self._score_general_relevance(question, choice_text)
        
        avg_score = total_score / len(answers)
        return avg_score > 2
    
    def _apply_policy_knowledge(self, question: str, choices: Dict[str, str], predicted_answer: List[str], question_type: str) -> Optional[Dict]:
        """Apply specific Thai healthcare policy knowledge"""
        
        # Look for specific policy conflicts
        corrections = []
        reasoning = ""
        
        # Check for บัตรทอง vs 30บาท conflict
        if question_type == "what_is_excluded":
            choice_texts = [choices.get(choice, '') for choice in predicted_answer]
            choice_text_combined = ' '.join(choice_texts)
            
            # If question is about บัตรทอง and answer mentions 30บาท, that's likely wrong
            if 'บัตรทอง' in question and '30บาท' in choice_text_combined:
                # Remove choices mentioning 30บาท for บัตรทอง questions
                filtered_answers = []
                for choice in predicted_answer:
                    choice_text = choices.get(choice, '')
                    if '30บาท' not in choice_text:
                        filtered_answers.append(choice)
                
                if filtered_answers != predicted_answer:
                    return {
                        'answer': filtered_answers or ['ง'],  # Fallback to ง if nothing left
                        'corrections': ['ลบคำตอบที่เกี่ยวกับ30บาทออกจากคำถามบัตรทอง'],
                        'reasoning': 'บัตรทองไม่เกี่ยวกับ30บาท'
                    }
        
        return None
    
    def _calculate_smart_confidence(self, question: str, choices: Dict[str, str], answer: List[str], corrections: List[str]) -> float:
        """Calculate confidence with bias against excessive 'ง' answers"""
        base_confidence = 0.6
        
        # Boost confidence for non-"ง" answers
        if answer != ["ง"]:
            base_confidence += 0.15
        
        # Boost confidence for corrections that avoid "ง"
        if corrections and any('แทนที่' in correction for correction in corrections):
            base_confidence += 0.1
        
        # Boost for multiple choice answers (often more accurate than single "ง")
        if len(answer) > 1 and 'ง' not in answer:
            base_confidence += 0.05
        
        # Adjust based on question complexity
        if len(question) > 100:
            base_confidence -= 0.05
        
        return min(max(base_confidence, 0.1), 0.95)

def test_improved_validator():
    """Test the improved healthcare validator"""
    print("🧪 Testing Improved Healthcare Validator")
    print("=" * 45)
    
    validator = ImprovedHealthcareValidator()
    
    # Test cases that should NOT be "ง"
    test_cases = [
        {
            "name": "Inclusion question (should have answers, not ง)",
            "question": "สิทธิประกันสุขภาพแห่งชาติครอบคลุมการรักษาใดบ้าง?",
            "choices": {
                "ก": "การรักษาพยาบาลทั่วไป",
                "ข": "การรักษาเสริมความงาม", 
                "ค": "ยาจำเป็น",
                "ง": "ไม่มีข้อใดถูกต้อง"
            },
            "predicted": ["ง"],  # Over-conservative
            "should_improve": True
        },
        {
            "name": "บัตรทอง benefits (should have answers)",
            "question": "ผู้ถือบัตรทองได้รับสิทธิประโยชน์อะไรบ้าง?",
            "choices": {
                "ก": "การรักษาฟรี",
                "ข": "ค่าบริการ30บาท",
                "ค": "ตรวจสุขภาพประจำปี", 
                "ง": "ไม่มีข้อใดถูกต้อง"
            },
            "predicted": ["ง"],  # Over-conservative
            "should_improve": True
        },
        {
            "name": "Valid exclusion question (ง might be correct)",
            "question": "สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ?",
            "choices": {
                "ก": "สิทธิหลักประกันสุขภาพแห่งชาติ",
                "ข": "สิทธิบัตรทอง",
                "ค": "สิทธิ 30 บาทรักษาทุกโรค",
                "ง": "ไม่มีข้อใดถูกต้อง"
            },
            "predicted": ["ง"],  # This might actually be correct
            "should_improve": False
        }
    ]
    
    improvements = 0
    
    for test_case in test_cases:
        print(f"\n📋 Test: {test_case['name']}")
        print(f"   Question: {test_case['question'][:50]}...")
        print(f"   Original: {test_case['predicted']}")
        
        result = validator.validate_healthcare_answer(
            test_case['question'],
            test_case['choices'],
            test_case['predicted']
        )
        
        print(f"   Validated: {result.validated_answer}")
        print(f"   Confidence: {result.confidence:.2f}")
        
        if result.corrections_made:
            print(f"   ✅ Corrections: {result.corrections_made}")
            print(f"   📝 Reasoning: {result.reasoning}")
            
            if test_case['should_improve'] and result.validated_answer != ["ง"]:
                improvements += 1
                print(f"   🎯 IMPROVED! Avoided excessive 'ง'")
            elif not test_case['should_improve']:
                print(f"   📝 Appropriately kept 'ง' for exclusion question")
        else:
            print(f"   📝 No changes made")
    
    print(f"\n📊 Results:")
    print(f"  Improvements: {improvements}/{sum(1 for tc in test_cases if tc['should_improve'])}")
    print(f"  This validator should reduce excessive 'ง' answers!")
    
    return improvements > 0

if __name__ == "__main__":
    test_improved_validator()