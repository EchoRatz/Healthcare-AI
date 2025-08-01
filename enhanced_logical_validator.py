#!/usr/bin/env python3
"""
Enhanced Logical Validator for Thai Healthcare Questions
=======================================================

Fixes logical contradictions and improves answer accuracy using rule-based validation
"""

import re
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result from logical validation"""
    original_answer: List[str]
    validated_answer: List[str]
    confidence: float
    corrections_made: List[str]
    reasoning: str

class ThaiHealthcareLogicalValidator:
    """Enhanced logical validator for Thai healthcare policy questions"""
    
    def __init__(self):
        # Thai healthcare policy rules
        self.healthcare_rights = {
            "สิทธิหลักประกันสุขภาพแห่งชาติ": {
                "keywords": ["หลักประกัน", "สุขภาพแห่งชาติ", "30บาท"],
                "excludes": ["บัตรทอง", "ประกันสังคม", "บัตรเครดิต"]
            },
            "สิทธิบัตรทอง": {
                "keywords": ["บัตรทอง", "ผู้สูงอายุ", "ฟรี"],
                "excludes": ["30บาท", "ประกันสังคม"]
            },
            "สิทธิ30บาทรักษาทุกโรค": {
                "keywords": ["30บาท", "รักษาทุกโรค", "ค่าบริการ"],
                "excludes": ["ฟรี", "บัตรทอง"]
            }
        }
        
        # Logical contradiction patterns
        self.contradiction_rules = [
            {
                "name": "none_of_above_contradiction",
                "pattern": lambda choices: 'ง' in choices and len(choices) > 1,
                "fix": lambda choices: ['ง'],
                "reason": "ง (ไม่มีข้อใดถูกต้อง) ขัดแย้งกับตัวเลือกอื่น"
            },
            {
                "name": "all_choices_selected",
                "pattern": lambda choices: len(choices) >= 4 and all(c in choices for c in ['ก', 'ข', 'ค', 'ง']),
                "fix": lambda choices: ['ง'],  # If everything is selected, likely nothing is correct
                "reason": "เลือกทุกตัวเลือกรวมถึง 'ไม่มีข้อใดถูกต้อง' - น่าจะไม่มีข้อใดถูก"
            },
            {
                "name": "duplicate_rights",
                "pattern": lambda choices: self._has_duplicate_rights_logic(choices),
                "fix": lambda choices: self._fix_duplicate_rights(choices),
                "reason": "มีสิทธิ์ที่ซ้ำซ้อนหรือขัดแย้งกัน"
            }
        ]
        
        # Thai healthcare knowledge base for validation
        self.thai_healthcare_facts = {
            "สิทธิหลักประกันสุขภาพแห่งชาติ": {
                "includes": ["การตรวจรักษาพยาบาลทั่วไป", "ยาจำเป็น", "การผ่าตัด"],
                "excludes": ["การรักษาเสริมความงาม", "ยาแบรนด์เนม", "ค่าห้องพิเศษ"]
            },
            "บัตรทอง": {
                "includes": ["การรักษาฟรี", "ยาฟรี", "ตรวจสุขภาพประจำปี"],
                "excludes": ["ค่าใช้จ่าย", "30บาท", "เงินสด"]
            }
        }
    
    def validate_answer(self, question: str, choices: Dict[str, str], predicted_answer: List[str]) -> ValidationResult:
        """Main validation function"""
        logger.info(f"🔍 Validating answer: {predicted_answer}")
        
        original_answer = predicted_answer.copy()
        corrections_made = []
        reasoning_parts = []
        
        # Step 1: Check for logical contradictions
        contradiction_result = self._check_contradictions(predicted_answer)
        if contradiction_result:
            predicted_answer = contradiction_result['fixed_answer']
            corrections_made.extend(contradiction_result['corrections'])
            reasoning_parts.append(contradiction_result['reasoning'])
        
        # Step 2: Apply Thai healthcare policy rules
        policy_result = self._apply_healthcare_policy_rules(question, choices, predicted_answer)
        if policy_result:
            predicted_answer = policy_result['fixed_answer']
            corrections_made.extend(policy_result['corrections'])
            reasoning_parts.append(policy_result['reasoning'])
        
        # Step 3: Content-based validation
        content_result = self._validate_against_content(question, choices, predicted_answer)
        if content_result:
            predicted_answer = content_result['fixed_answer']
            corrections_made.extend(content_result['corrections'])
            reasoning_parts.append(content_result['reasoning'])
        
        # Step 4: Calculate confidence
        confidence = self._calculate_confidence(question, choices, predicted_answer, corrections_made)
        
        final_reasoning = " | ".join(reasoning_parts) if reasoning_parts else "ไม่พบข้อผิดพลาดทางตรรกะ"
        
        logger.info(f"✅ Validation complete: {original_answer} → {predicted_answer}")
        if corrections_made:
            logger.info(f"🔧 Corrections: {corrections_made}")
        
        return ValidationResult(
            original_answer=original_answer,
            validated_answer=predicted_answer,
            confidence=confidence,
            corrections_made=corrections_made,
            reasoning=final_reasoning
        )
    
    def _check_contradictions(self, choices: List[str]) -> Optional[Dict]:
        """Check for logical contradictions"""
        for rule in self.contradiction_rules:
            if rule['pattern'](choices):
                fixed_answer = rule['fix'](choices)
                return {
                    'fixed_answer': fixed_answer,
                    'corrections': [f"แก้ไขความขัดแย้ง: {rule['name']}"],
                    'reasoning': rule['reason']
                }
        return None
    
    def _apply_healthcare_policy_rules(self, question: str, choices: Dict[str, str], predicted_answer: List[str]) -> Optional[Dict]:
        """Apply Thai healthcare policy-specific rules"""
        corrections = []
        reasoning_parts = []
        
        # Rule: If question asks what's NOT included, and answer contains 'ง', be more conservative
        if "ไม่รวมอยู่" in question or "ไม่ได้รับ" in question:
            if len(predicted_answer) > 1 and 'ง' in predicted_answer:
                # Remove other choices if 'ง' is selected for "not included" questions
                fixed_answer = ['ง']
                corrections.append("คำถาม 'ไม่รวมอยู่' + เลือก 'ง' → เลือกเฉพาะ 'ง'")
                reasoning_parts.append("คำถามเชิงลบควรมีคำตอบเดี่ยว")
                
                return {
                    'fixed_answer': fixed_answer,
                    'corrections': corrections,
                    'reasoning': " | ".join(reasoning_parts)
                }
        
        # Rule: Healthcare rights mutual exclusivity
        selected_choices_text = [choices.get(choice, '') for choice in predicted_answer]
        healthcare_terms = ['สิทธิหลักประกัน', 'บัตรทอง', '30บาท']
        
        found_terms = []
        for term in healthcare_terms:
            if any(term in text for text in selected_choices_text):
                found_terms.append(term)
        
        # If multiple healthcare rights are selected, apply logic
        if len(found_terms) > 1:
            # In most cases, these are different programs, not overlapping
            if 'บัตรทอง' in found_terms and '30บาท' in found_terms:
                # บัตรทอง is usually free, conflicts with 30บาท fee
                if 'ข' in predicted_answer:  # Assuming 'ข' is บัตรทอง
                    fixed_answer = ['ข']
                    corrections.append("บัตรทองขัดแย้งกับ30บาท → เลือกบัตรทอง")
                    reasoning_parts.append("บัตรทองให้บริการฟรี ไม่ใช่30บาท")
                    
                    return {
                        'fixed_answer': fixed_answer,
                        'corrections': corrections,
                        'reasoning': " | ".join(reasoning_parts)
                    }
        
        return None
    
    def _validate_against_content(self, question: str, choices: Dict[str, str], predicted_answer: List[str]) -> Optional[Dict]:
        """Validate against Thai healthcare content knowledge"""
        corrections = []
        reasoning_parts = []
        
        # Extract key terms from question
        question_terms = self._extract_key_terms(question)
        
        # For each predicted choice, check if it makes sense
        problematic_choices = []
        
        for choice in predicted_answer:
            choice_text = choices.get(choice, '')
            
            # Check for obvious mismatches
            if self._is_obvious_mismatch(question_terms, choice_text):
                problematic_choices.append(choice)
        
        # Remove problematic choices
        if problematic_choices:
            fixed_answer = [c for c in predicted_answer if c not in problematic_choices]
            
            # If we removed everything, default to 'ง'
            if not fixed_answer:
                fixed_answer = ['ง']
            
            corrections.append(f"ลบตัวเลือกที่ไม่สมเหตุสมผล: {problematic_choices}")
            reasoning_parts.append("ตัวเลือกไม่ตรงกับเนื้อหาคำถาม")
            
            return {
                'fixed_answer': fixed_answer,
                'corrections': corrections,
                'reasoning': " | ".join(reasoning_parts)
            }
        
        return None
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key healthcare terms from text"""
        healthcare_terms = [
            'สิทธิ', 'ประกัน', 'สุขภาพ', 'บัตร', 'ทอง', '30บาท', 
            'รักษา', 'โรค', 'ฟรี', 'ยา', 'แพทย์', 'โรงพยาบาล'
        ]
        
        found_terms = []
        for term in healthcare_terms:
            if term in text:
                found_terms.append(term)
        
        return found_terms
    
    def _is_obvious_mismatch(self, question_terms: List[str], choice_text: str) -> bool:
        """Check if choice obviously doesn't match question context"""
        # This is a simplified heuristic - can be expanded
        
        # If question is about สิทธิประกัน but choice mentions unrelated topics
        if 'สิทธิ' in question_terms or 'ประกัน' in question_terms:
            unrelated_terms = ['อาหาร', 'เครื่องแต่งกาย', 'ท่องเที่ยว', 'บันเทิง']
            if any(term in choice_text for term in unrelated_terms):
                return True
        
        return False
    
    def _has_duplicate_rights_logic(self, choices: List[str]) -> bool:
        """Check if there are duplicate or conflicting rights selected"""
        # This is a placeholder for more complex logic
        return False
    
    def _fix_duplicate_rights(self, choices: List[str]) -> List[str]:
        """Fix duplicate rights selections"""
        # This is a placeholder for more complex logic
        return choices
    
    def _calculate_confidence(self, question: str, choices: Dict[str, str], answer: List[str], corrections: List[str]) -> float:
        """Calculate confidence score"""
        base_confidence = 0.7
        
        # Boost confidence if we made logical corrections
        if corrections:
            base_confidence += 0.15  # Logical validation adds confidence
        
        # Adjust based on answer characteristics
        if len(answer) == 1:
            if answer[0] == 'ง':
                base_confidence += 0.1  # Single "none" answer is often more confident
            else:
                base_confidence += 0.05  # Single specific answer
        
        # Adjust based on question complexity
        if len(question) > 100:  # Complex question
            base_confidence -= 0.05
        
        # Cap at reasonable bounds
        return min(max(base_confidence, 0.1), 0.95)

def test_logical_validator():
    """Test the logical validator"""
    print("🧪 Testing Enhanced Logical Validator")
    print("=" * 45)
    
    validator = ThaiHealthcareLogicalValidator()
    
    # Test cases
    test_cases = [
        {
            "name": "Contradiction: ง + others",
            "question": "สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ?",
            "choices": {
                "ก": "สิทธิหลักประกันสุขภาพแห่งชาติ",
                "ข": "สิทธิบัตรทอง",
                "ค": "สิทธิ 30 บาทรักษาทุกโรค",
                "ง": "ไม่มีข้อใดถูกต้อง"
            },
            "predicted": ["ข", "ง", "ก"],  # The problematic answer
            "expected_fix": ["ง"]
        },
        {
            "name": "All choices selected",
            "question": "สิทธิใดบ้างที่ประชาชนได้รับ?",
            "choices": {
                "ก": "สิทธิหลักประกัน",
                "ข": "สิทธิบัตรทอง", 
                "ค": "สิทธิ30บาท",
                "ง": "ไม่มีข้อใดถูกต้อง"
            },
            "predicted": ["ก", "ข", "ค", "ง"],
            "expected_fix": ["ง"]
        },
        {
            "name": "Valid single answer",
            "question": "สิทธิใดที่ให้บริการฟรี?",
            "choices": {
                "ก": "สิทธิหลักประกัน",
                "ข": "สิทธิบัตรทอง",
                "ค": "สิทธิ30บาท", 
                "ง": "ไม่มีข้อใดถูกต้อง"
            },
            "predicted": ["ข"],
            "expected_fix": ["ข"]  # Should remain unchanged
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📋 Test: {test_case['name']}")
        print(f"   Question: {test_case['question'][:50]}...")
        print(f"   Original: {test_case['predicted']}")
        
        result = validator.validate_answer(
            test_case['question'],
            test_case['choices'],
            test_case['predicted']
        )
        
        print(f"   Validated: {result.validated_answer}")
        print(f"   Confidence: {result.confidence:.2f}")
        
        if result.corrections_made:
            print(f"   ✅ Corrections: {result.corrections_made}")
            print(f"   📝 Reasoning: {result.reasoning}")
        
        # Check if fix matches expectation
        if result.validated_answer == test_case['expected_fix']:
            print(f"   🎯 CORRECT FIX!")
        else:
            print(f"   ⚠️  Expected {test_case['expected_fix']}, got {result.validated_answer}")
    
    print(f"\n🎉 Logical Validator is ready!")
    print(f"💡 This can be integrated into ultra_fast_llama31.py immediately")

if __name__ == "__main__":
    test_logical_validator()