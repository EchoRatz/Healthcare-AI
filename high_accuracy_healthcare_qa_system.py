#!/usr/bin/env python3
"""
High-Accuracy Healthcare Q&A System for Llama 3.1 70B
=====================================================

Optimized system designed to achieve 75%+ accuracy with fast runtime.
Key improvements:
1. Advanced question understanding with intent classification
2. Semantic knowledge base indexing and retrieval
3. Optimized prompting for Llama 3.1 70B
4. Smart answer validation with policy awareness
5. Confidence-based answer selection
6. Fast processing with efficient algorithms
"""

import os
import sys
import csv
import json
import requests
import time
import re
import asyncio
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from collections import defaultdict, Counter
import numpy as np

@dataclass
class QuestionIntent:
    """Detailed question intent analysis"""
    primary_type: str  # 'inclusion', 'exclusion', 'factual', 'procedure', 'comparison', 'emergency'
    secondary_type: str  # Additional context
    keywords: List[str]
    entities: List[str]
    numbers: List[str]
    policy_terms: List[str]
    department_terms: List[str]
    confidence: float
    urgency_level: int  # 1-5 scale

@dataclass
class ContextMatch:
    """Context matching result"""
    content: str
    relevance_score: float
    source: str
    keywords_matched: List[str]
    policy_related: bool

@dataclass
class AnswerAnalysis:
    """Detailed answer analysis"""
    selected_answers: List[str]
    confidence: float
    reasoning: str
    policy_validation: bool
    context_support: float
    alternatives: List[str]
    should_reject: bool

class HighAccuracyHealthcareQA:
    """High-accuracy healthcare Q&A system optimized for Llama 3.1 70B"""

    def __init__(self):
        self.model_name = None
        self.knowledge_base = {}
        self.semantic_index = None
        self.vectorizer = None
        self.healthcare_policies = self._load_comprehensive_policies()
        self.question_patterns = self._load_advanced_patterns()
        self.department_mapping = self._load_department_mapping()
        self.emergency_keywords = self._load_emergency_keywords()
        self.number_patterns = self._load_number_patterns()
        self.cache = {}
        
    def _load_comprehensive_policies(self) -> Dict:
        """Load comprehensive Thai healthcare policy knowledge"""
        return {
            "สิทธิหลักประกันสุขภาพแห่งชาติ": {
                "includes": [
                    "การตรวจรักษาพยาบาลทั่วไป", "ยาจำเป็น", "การผ่าตัด", "การฟื้นฟู",
                    "การรักษาโรคเรื้อรัง", "การตรวจสุขภาพ", "วัคซีน", "การคลอด",
                    "การรักษาฉุกเฉิน", "การส่งต่อ", "การตรวจทางห้องปฏิบัติการ",
                    "การผ่าตัดฉุกเฉิน", "การรักษาในโรงพยาบาล", "การดูแลผู้ป่วยใน",
                    "การตรวจคัดกรอง", "การป้องกันโรค", "การฟื้นฟูสมรรถภาพ",
                    "การดูแลผู้สูงอายุ", "การดูแลเด็ก", "การดูแลหญิงตั้งครรภ์",
                    "การรักษาทันตกรรม", "การรักษาโรคไต", "การรักษาโรคหัวใจ",
                    "การรักษาโรคมะเร็ง", "การรักษาโรคเบาหวาน", "การรักษาโรคความดันโลหิตสูง"
                ],
                "excludes": [
                    "การรักษาเสริมความงาม", "ยาแบรนด์เนม", "ค่าห้องพิเศษ",
                    "การรักษาทดลอง", "อุปกรณ์เสริม", "การท่องเที่ยวเพื่อสุขภาพ",
                    "การรักษาที่ไม่จำเป็น", "ยาเสริม", "การตรวจที่ไม่จำเป็น",
                    "การรักษาในโรงพยาบาลเอกชนที่ไม่ได้อยู่ในระบบ", "การรักษาในต่างประเทศ"
                ],
                "keywords": ["หลักประกัน", "สุขภาพแห่งชาติ", "UC", "30บาท", "สปสช", "1330"],
                "coverage": "universal",
                "cost": "30บาท"
            },
            "สิทธิบัตรทอง": {
                "includes": [
                    "การรักษาฟรี", "ยาฟรี", "ตรวจสุขภาพประจำปี", "การดูแลผู้สูงอายุ",
                    "บริการที่บ้าน", "อุปกรณ์การแพทย์", "การฟื้นฟูสุขภาพ",
                    "การตรวจคัดกรอง", "การป้องกันโรค", "การดูแลระยะยาว",
                    "การรักษาโรคเรื้อรัง", "การดูแลผู้พิการ", "การฟื้นฟูสมรรถภาพ"
                ],
                "excludes": [
                    "ค่าใช้จ่าย", "30บาท", "เงินสด", "ค่าบริการ", "ค่าตรวจ"
                ],
                "keywords": ["บัตรทอง", "ผู้สูงอายุ", "ฟรี", "60ปี", "ผู้พิการ", "D1"],
                "coverage": "elderly_disabled",
                "cost": "ฟรี"
            },
            "สิทธิ30บาทรักษาทุกโรค": {
                "includes": [
                    "ค่าบริการ30บาท", "รักษาโรคทั่วไป", "ยาจำเป็น", "การตรวจรักษา",
                    "บริการผู้ป่วยนอก", "การส่งต่อ", "การตรวจพื้นฐาน"
                ],
                "excludes": [
                    "ฟรี", "ไม่เสียค่าใช้จ่าย", "บัตรทอง", "ผู้สูงอายุเท่านั้น"
                ],
                "keywords": ["30บาท", "รักษาทุกโรค", "ค่าบริการ", "UC"],
                "coverage": "general",
                "cost": "30บาท"
            },
            "สิทธิประกันสังคม": {
                "includes": [
                    "การรักษาพยาบาล", "ยา", "การตรวจ", "การผ่าตัด",
                    "การฟื้นฟู", "การดูแลผู้ป่วยใน", "การตรวจทางห้องปฏิบัติการ"
                ],
                "excludes": [
                    "การรักษาเสริมความงาม", "ยาแบรนด์เนม", "ค่าห้องพิเศษ"
                ],
                "keywords": ["ประกันสังคม", "ขสมก", "สวัสดิการ"],
                "coverage": "employed",
                "cost": "copay"
            }
        }
    
    def _load_advanced_patterns(self) -> Dict:
        """Load advanced patterns for question classification"""
        return {
            "inclusion": [
                r"รวมอยู่ใน", r"ได้รับ", r"มีสิทธิ์", r"ครอบคลุม", r"ประกอบด้วย",
                r"มีอะไรบ้าง", r"อะไรบ้าง", r"ซึ่งรวมถึง", r"รวมถึง", r"สามารถ",
                r"ให้บริการ", r"รับบริการ", r"ใช้สิทธิ", r"ครอบคลุม"
            ],
            "exclusion": [
                r"ไม่รวมอยู่ใน", r"ไม่ได้รับ", r"ไม่มีสิทธิ์", r"ไม่ครอบคลุม", r"ยกเว้น",
                r"ไม่ใช่", r"ไม่ใช่ข้อใด", r"ไม่ถูกต้อง", r"ไม่สามารถ", r"ไม่ให้บริการ"
            ],
            "factual": [
                r"เท่าใด", r"กี่บาท", r"กี่ครั้ง", r"กี่ปี", r"เมื่อใด",
                r"ที่ไหน", r"ใคร", r"อะไร", r"อย่างไร", r"อัตรา", r"ค่าใช้จ่าย",
                r"ราคา", r"จำนวน", r"ปริมาณ", r"ระยะเวลา"
            ],
            "procedure": [
                r"ขั้นตอน", r"วิธีการ", r"ต้องทำอย่างไร", r"ควรทำอะไร",
                r"ต้องใช้", r"ต้องมี", r"เงื่อนไข", r"กระบวนการ", r"ขั้นตอนการ"
            ],
            "comparison": [
                r"แตกต่าง", r"เปรียบเทียบ", r"ความแตกต่าง", r"เหมือน", r"ต่าง",
                r"มากกว่า", r"น้อยกว่า", r"เท่ากับ", r"สูงกว่า", r"ต่ำกว่า"
            ],
            "emergency": [
                r"ฉุกเฉิน", r"วิกฤต", r"เจ็บหน้าอก", r"หายใจลำบาก", r"หมดสติ",
                r"เลือดออก", r"อุบัติเหตุ", r"เจ็บป่วยฉุกเฉิน", r"UCEP"
            ],
            "department": [
                r"แผนก", r"department", r"แผนกไหน", r"แผนกใด", r"พบหมอ",
                r"ส่งแผนก", r"แผนกโรค", r"แผนกออร์โธปิดิกส์", r"แผนกโรคหัวใจ"
            ]
        }
    
    def _load_department_mapping(self) -> Dict:
        """Load department mapping for better classification"""
        return {
            "cardiology": ["โรคหัวใจ", "cardiology", "หัวใจ", "ความดัน", "หัวใจวาย"],
            "orthopedics": ["ออร์โธปิดิกส์", "orthopedics", "กระดูก", "ข้อ", "ปวดหลัง", "spine"],
            "emergency": ["ฉุกเฉิน", "emergency", "ER", "วิกฤต", "UCEP"],
            "neurology": ["ประสาท", "neurology", "สมอง", "เส้นประสาท"],
            "endocrinology": ["ต่อมไร้ท่อ", "endocrinology", "เบาหวาน", "ฮอร์โมน"],
            "internal_medicine": ["อายุรกรรม", "internal medicine", "อายุร"],
            "psychiatry": ["จิตเวช", "psychiatry", "จิต", "วิตกกังวล"],
            "nephrology": ["ไต", "nephrology", "ไตวาย", "ล้างไต"],
            "dental": ["ทันตกรรม", "dental", "ฟัน", "ทันต"],
            "pediatrics": ["กุมาร", "pediatrics", "เด็ก", "ทารก"]
        }
    
    def _load_emergency_keywords(self) -> Set:
        """Load emergency-related keywords"""
        return {
            "ฉุกเฉิน", "วิกฤต", "เจ็บหน้าอก", "หายใจลำบาก", "หมดสติ", "เลือดออก",
            "อุบัติเหตุ", "เจ็บป่วยฉุกเฉิน", "UCEP", "หัวใจวาย", "stroke",
            "emergency", "critical", "chest pain", "shortness of breath"
        }
    
    def _load_number_patterns(self) -> Dict:
        """Load patterns for number extraction"""
        return {
            "money": [r"(\d+(?:,\d+)*)\s*บาท", r"(\d+)\s*บาท/เม็ด", r"(\d+)\s*บาท/ครั้ง"],
            "age": [r"อายุ\s*(\d+)\s*ปี", r"(\d+)\s*ปี"],
            "time": [r"(\d{1,2}):(\d{2})", r"(\d+)\s*โมง", r"(\d+)\s*นาที"],
            "quantity": [r"(\d+)\s*ครั้ง", r"(\d+)\s*ขวด", r"(\d+)\s*อัน"],
            "year": [r"ปี\s*(\d{4})", r"พ\.ศ\.\s*(\d{4})", r"ค\.ศ\.\s*(\d{4})"]
        } 
    
    def check_llama31(self) -> bool:
        """Check for Llama 3.1 availability"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=3)
            if response.status_code == 200:
                models = response.json().get("models", [])
                for model in models:
                    if "llama3.1" in model["name"].lower():
                        self.model_name = model["name"]
                        return True
            return False
        except:
            return False
    
    def load_knowledge_base(self):
        """Load and create semantic index of knowledge base"""
        print("📚 Loading and indexing knowledge base...")
        
        doc_files = [
            "Healthcare-AI-Refactored/src/infrastructure/results_doc/direct_extraction_corrected.txt",
            "Healthcare-AI-Refactored/src/infrastructure/results_doc2/direct_extraction_corrected.txt",
            "Healthcare-AI-Refactored/src/infrastructure/results_doc3/direct_extraction_corrected.txt",
        ]
        
        all_content = []
        content_sections = []
        
        for i, doc_file in enumerate(doc_files, 1):
            if os.path.exists(doc_file):
                with open(doc_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    sections = self._split_into_sections(content)
                    
                    for j, section in enumerate(sections):
                        if len(section.strip()) > 100:  # Only meaningful sections
                            section_id = f"doc_{i}_section_{j}"
                            content_sections.append({
                                'id': section_id,
                                'content': section,
                                'doc_id': f"doc_{i}",
                                'keywords': self._extract_keywords_advanced(section)
                            })
                            all_content.append(section)
                    
                    print(f"  ✅ Document {i}: {len(sections)} sections indexed")
            else:
                print(f"  ⚠️  Document {i} not found: {doc_file}")
        
        # Create simple semantic search (without sklearn dependency)
        if all_content:
            self.knowledge_sections = content_sections
            print(f"  🧠 Knowledge base indexed with {len(all_content)} sections")
    
    def _split_into_sections(self, content: str) -> List[str]:
        """Split content into meaningful sections"""
        # Split by page markers
        sections = re.split(r'--- Page \d+ ---', content)
        
        # Further split by natural breaks
        final_sections = []
        for section in sections:
            if len(section.strip()) > 50:
                # Split by double newlines or Q/A patterns
                subsections = re.split(r'\n\n+', section)
                final_sections.extend([s.strip() for s in subsections if len(s.strip()) > 50])
        
        return final_sections
    
    def _extract_keywords_advanced(self, text: str) -> List[str]:
        """Extract relevant keywords with advanced techniques"""
        keywords = []
        
        # Thai healthcare specific keywords
        thai_keywords = [
            "สิทธิ", "หลักประกัน", "สุขภาพ", "การรักษา", "ยา", "ตรวจ", "ผ่าตัด",
            "โรงพยาบาล", "แพทย์", "ผู้ป่วย", "ค่าใช้จ่าย", "บริการ", "โรค",
            "การคลอด", "วัคซีน", "ฉุกเฉิน", "ส่งต่อ", "ใบส่งตัว", "บัตรทอง",
            "สปสช", "1330", "30บาท", "ฟรี", "ประกันสังคม", "ขสมก"
        ]
        
        # Extract policy terms
        for policy, info in self.healthcare_policies.items():
            if any(keyword in text for keyword in info["keywords"]):
                keywords.append(policy)
                keywords.extend(info["keywords"])
        
        # Extract department terms
        for dept, terms in self.department_mapping.items():
            if any(term in text for term in terms):
                keywords.append(dept)
                keywords.extend(terms)
        
        # Extract numbers
        for pattern_type, patterns in self.number_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text)
                keywords.extend(matches)
        
        # Extract Thai words (2+ characters)
        thai_words = re.findall(r'[ก-ฮ]{2,}', text)
        keywords.extend(thai_words[:10])  # Limit to top 10
        
        # Add specific keywords found in text
        for keyword in thai_keywords:
            if keyword in text:
                keywords.append(keyword)
        
        return list(set(keywords))  # Remove duplicates
    
    def analyze_question_advanced(self, question_text: str) -> QuestionIntent:
        """Advanced question analysis with multiple dimensions"""
        
        # Initialize analysis
        primary_type = "factual"
        secondary_type = "general"
        keywords = []
        entities = []
        numbers = []
        policy_terms = []
        department_terms = []
        confidence = 0.5
        urgency_level = 1
        
        # Detect question type with confidence scoring
        type_scores = defaultdict(float)
        for qtype, patterns in self.question_patterns.items():
            for pattern in patterns:
                if re.search(pattern, question_text, re.IGNORECASE):
                    type_scores[qtype] += 0.3
                    confidence += 0.1
        
        # Select primary type
        if type_scores:
            primary_type = max(type_scores, key=type_scores.get)
            if type_scores[primary_type] > 0.5:
                confidence += 0.2
        
        # Check for emergency
        if any(keyword in question_text.lower() for keyword in self.emergency_keywords):
            urgency_level = 5
            if primary_type == "factual":
                primary_type = "emergency"
        
        # Extract keywords and entities
        keywords = self._extract_keywords_advanced(question_text)
        
        # Extract policy terms
        for policy, info in self.healthcare_policies.items():
            if any(keyword in question_text for keyword in info["keywords"]):
                policy_terms.append(policy)
                entities.append(policy)
        
        # Extract department terms
        for dept, terms in self.department_mapping.items():
            if any(term in question_text.lower() for term in terms):
                department_terms.append(dept)
                entities.append(dept)
        
        # Extract numbers
        for pattern_type, patterns in self.number_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, question_text)
                numbers.extend(matches)
        
        # Determine secondary type
        if department_terms:
            secondary_type = "department"
        elif policy_terms:
            secondary_type = "policy"
        elif numbers:
            secondary_type = "numerical"
        
        return QuestionIntent(
            primary_type=primary_type,
            secondary_type=secondary_type,
            keywords=keywords,
            entities=entities,
            numbers=numbers,
            policy_terms=policy_terms,
            department_terms=department_terms,
            confidence=min(confidence, 1.0),
            urgency_level=urgency_level
        )
    
    def search_context_semantic(self, question_analysis: QuestionIntent, max_sections: int = 5) -> List[ContextMatch]:
        """Semantic search for relevant context using keyword matching"""
        if not hasattr(self, 'knowledge_sections'):
            return []
        
        # Score sections based on keyword overlap
        scored_sections = []
        for section in self.knowledge_sections:
            score = 0.0
            matched_keywords = []
            
            # Score based on keyword matches
            for keyword in question_analysis.keywords:
                if keyword in section['content']:
                    score += 0.2
                    matched_keywords.append(keyword)
            
            # Bonus for policy terms
            for policy in question_analysis.policy_terms:
                if policy in section['content']:
                    score += 0.3
            
            # Bonus for department terms
            for dept in question_analysis.department_terms:
                if dept in section['content']:
                    score += 0.2
            
            # Bonus for number matches
            for number in question_analysis.numbers:
                if number in section['content']:
                    score += 0.1
            
            if score > 0.1:  # Minimum relevance threshold
                scored_sections.append(ContextMatch(
                    content=section['content'],
                    relevance_score=score,
                    source=section['doc_id'],
                    keywords_matched=matched_keywords,
                    policy_related=any(policy in section['content'] for policy in question_analysis.policy_terms)
                ))
        
        # Sort by relevance and return top matches
        scored_sections.sort(key=lambda x: x.relevance_score, reverse=True)
        return scored_sections[:max_sections]
    
    def parse_question_enhanced(self, question_text: str) -> Tuple[str, Dict[str, str]]:
        """Enhanced question parsing with better choice extraction"""
        parts = question_text.split("ก.")
        if len(parts) < 2:
            return question_text, {}
        
        question = parts[0].strip()
        choices_text = "ก." + parts[1]
        
        # Enhanced choice extraction
        choice_pattern = re.compile(r"([ก-ง])\.\s*([^ก-ง]+?)(?=\s*[ก-ง]\.|$)")
        choices = {}
        
        for match in choice_pattern.finditer(choices_text):
            choice_letter = match.group(1)
            choice_text = match.group(2).strip()
            choices[choice_letter] = choice_text
        
        return question, choices
    
    def build_optimized_prompt(self, question: str, choices: Dict[str, str], 
                             context_matches: List[ContextMatch], 
                             question_analysis: QuestionIntent) -> str:
        """Build optimized prompt for Llama 3.1 70B"""
        
        # Combine relevant context
        context_parts = []
        for match in context_matches[:3]:  # Top 3 most relevant
            if match.relevance_score > 0.2:
                context_parts.append(match.content)
        
        context = "\n\n".join(context_parts) if context_parts else "ไม่มีข้อมูลเฉพาะเจาะจง"
        
        # Build structured prompt
        prompt = f"""คุณเป็นผู้เชี่ยวชาญด้านระบบหลักประกันสุขภาพแห่งชาติของไทยที่มีประสบการณ์มากกว่า 20 ปี

ข้อมูลความรู้ที่เกี่ยวข้อง:
{context}

คำถาม: {question}

ตัวเลือก:
"""
        
        for letter, text in choices.items():
            prompt += f"{letter}. {text}\n"
        
        prompt += f"""
ประเภทคำถาม: {question_analysis.primary_type}
คำสำคัญ: {', '.join(question_analysis.keywords[:5])}
เอนทิตี้ที่เกี่ยวข้อง: {', '.join(question_analysis.entities[:3])}
ระดับความเร่งด่วน: {question_analysis.urgency_level}/5

คำแนะนำในการตอบ:
1. วิเคราะห์คำถามอย่างละเอียดตามประเภทที่ระบุ
2. ใช้ข้อมูลความรู้ที่ให้มาเป็นหลัก
3. หากมีหลายคำตอบที่ถูกต้อง ให้ระบุทั้งหมด
4. หากไม่มีคำตอบที่ถูกต้องในตัวเลือก ให้ตอบ "ง"
5. ตอบเฉพาะตัวอักษร เช่น "ก" หรือ "ข,ค" หรือ "ง"
6. อย่าตอบ "ง" ถ้ามีตัวเลือกที่ถูกต้อง

คำตอบ:"""
        
        return prompt
    
    def query_llama31_optimized(self, question: str, choices: Dict[str, str], 
                               context_matches: List[ContextMatch], 
                               question_analysis: QuestionIntent) -> Tuple[List[str], float]:
        """Optimized query to Llama 3.1 70B"""
        
        # Build optimized prompt
        prompt = self.build_optimized_prompt(question, choices, context_matches, question_analysis)
        
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Very low temperature for consistency
                        "top_p": 0.9,
                        "top_k": 40,
                        "repeat_penalty": 1.1,
                        "num_predict": 50  # Limit response length
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                answer_text = result.get("response", "").strip()
                
                # Extract answers with enhanced parsing
                answers = self._extract_answers_optimized(answer_text, choices)
                confidence = self._calculate_confidence_advanced(answer_text, question_analysis, context_matches)
                
                return answers, confidence
            else:
                print(f"❌ API Error: {response.status_code}")
                return [], 0.0
                
        except Exception as e:
            print(f"❌ Query Error: {e}")
            return [], 0.0
    
    def _extract_answers_optimized(self, text: str, choices: Dict[str, str]) -> List[str]:
        """Optimized answer extraction with multiple fallback strategies"""
        
        # Multiple patterns for answer extraction
        patterns = [
            r"คำตอบ[:\s]*([ก-ง](?:[,\s]+[ก-ง])*)",
            r"ตอบ[:\s]*([ก-ง](?:[,\s]+[ก-ง])*)",
            r"([ก-ง](?:[,\s]+[ก-ง])*)",
            r"ตัวเลือก[:\s]*([ก-ง](?:[,\s]+[ก-ง])*)",
            r"เลือก[:\s]*([ก-ง](?:[,\s]+[ก-ง])*)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                answer_text = match.group(1)
                # Clean and validate
                answers = re.findall(r'[ก-ง]', answer_text)
                if answers:
                    return list(set(answers))  # Remove duplicates
        
        # Fallback: look for any ก-ง in the text
        answers = re.findall(r'[ก-ง]', text)
        if answers:
            return list(set(answers))
        
        return []
    
    def _calculate_confidence_advanced(self, answer_text: str, question_analysis: QuestionIntent, 
                                     context_matches: List[ContextMatch]) -> float:
        """Advanced confidence calculation"""
        confidence = 0.5  # Base confidence
        
        # Higher confidence if answer is clear
        if "คำตอบ" in answer_text or "ตอบ" in answer_text:
            confidence += 0.2
        
        # Higher confidence if question analysis was successful
        confidence += question_analysis.confidence * 0.3
        
        # Higher confidence if we have relevant context
        if context_matches and any(match.relevance_score > 0.3 for match in context_matches):
            confidence += 0.2
        
        # Lower confidence if answer is "ง" and we have good context
        if "ง" in answer_text and context_matches and any(match.relevance_score > 0.4 for match in context_matches):
            confidence -= 0.1
        
        # Higher confidence for emergency questions
        if question_analysis.urgency_level >= 4:
            confidence += 0.1
        
        return min(max(confidence, 0.0), 1.0)
    
    def validate_answer_advanced(self, question: str, choices: Dict[str, str], 
                               answers: List[str], question_analysis: QuestionIntent) -> AnswerAnalysis:
        """Advanced answer validation with policy awareness"""
        
        if not answers:
            return AnswerAnalysis([], 0.0, "No answers found", False, 0.0, [], True)
        
        # Check for logical contradictions
        if "ง" in answers and len(answers) > 1:
            return AnswerAnalysis(
                ["ง"], 0.3, 
                "Contradiction: 'ง' cannot be combined with other answers",
                False, 0.3, ["ง"], False
            )
        
        # Check for all choices selected
        if len(answers) >= 4 and all(c in answers for c in ['ก', 'ข', 'ค', 'ง']):
            return AnswerAnalysis(
                ["ง"], 0.2,
                "All choices selected including 'ง' - likely none are correct",
                False, 0.2, ["ง"], False
            )
        
        # Validate against healthcare policies
        policy_validation = self._validate_against_policies_advanced(question, choices, answers, question_analysis)
        if not policy_validation:
            return AnswerAnalysis(
                answers, 0.4,
                "Policy validation failed",
                False, 0.4, answers, False
            )
        
        # Check for emergency context
        if question_analysis.urgency_level >= 4:
            # Emergency questions should have specific answers
            if "ง" in answers and len(answers) == 1:
                return AnswerAnalysis(
                    answers, 0.3,
                    "Emergency question should have specific answer, not 'ง'",
                    True, 0.3, answers, True
                )
        
        return AnswerAnalysis(
            answers, 0.8, 
            "Answer validated successfully", 
            True, 0.8, answers, False
        )
    
    def _validate_against_policies_advanced(self, question: str, choices: Dict[str, str], 
                                          answers: List[str], question_analysis: QuestionIntent) -> bool:
        """Advanced policy validation"""
        
        # Check for policy-specific contradictions
        for policy, info in self.healthcare_policies.items():
            if any(keyword in question for keyword in info["keywords"]):
                # Check if answers contradict policy
                for answer in answers:
                    choice_text = choices.get(answer, "")
                    if any(exclude in choice_text for exclude in info["excludes"]):
                        return False
        
        # Check for department-specific logic
        if question_analysis.department_terms:
            # Department questions should have specific answers
            if "ง" in answers and len(answers) == 1 and question_analysis.primary_type != "exclusion":
                return False
        
        return True
    
    def process_questions_high_accuracy(self, test_file: str) -> List[Dict]:
        """Process questions with high accuracy optimization"""

        if not self.check_llama31():
            print("❌ Llama 3.1 not available")
            return []

        print(f"✅ Using model: {self.model_name}")

        # Load knowledge base
        self.load_knowledge_base()

        # Load test questions
        questions = []
        with open(test_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                questions.append(row)

        print(f"🚀 Processing {len(questions)} questions with high accuracy optimization...")

        results = []
        start_time = time.time()

        for i, row in enumerate(questions, 1):
            question_id = row['id']
            question_text = row['question']

            # Parse question
            question, choices = self.parse_question_enhanced(question_text)

            # Analyze question
            question_analysis = self.analyze_question_advanced(question)

            # Search for context
            context_matches = self.search_context_semantic(question_analysis)

            # Query LLM
            answers, confidence = self.query_llama31_optimized(question, choices, context_matches, question_analysis)

            # Validate answer
            answer_analysis = self.validate_answer_advanced(question, choices, answers, question_analysis)

            # Apply final answer
            final_answers = answer_analysis.selected_answers if not answer_analysis.should_reject else answers

            # Format answer
            answer_str = ",".join(final_answers) if final_answers else "ง"

            results.append({
                'id': question_id,
                'answer': answer_str,
                'confidence': confidence,
                'validation_passed': answer_analysis.policy_validation,
                'reasoning': answer_analysis.reasoning,
                'question_type': question_analysis.primary_type,
                'urgency_level': question_analysis.urgency_level,
                'context_relevance': max([match.relevance_score for match in context_matches]) if context_matches else 0.0
            })

            # Progress update
            if i % 25 == 0:
                elapsed = time.time() - start_time
                rate = i / elapsed
                eta = (len(questions) - i) / rate if rate > 0 else 0
                print(f"  📊 {i}/{len(questions)} ({i/len(questions)*100:.1f}%) | Rate: {rate:.1f} q/s | ETA: {eta/60:.1f}min")

        total_time = time.time() - start_time
        print(f"🎉 High accuracy processing complete!")
        print(f"⏱️  Total time: {total_time/60:.1f} minutes")

        return results
    
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
        
        print(f"💾 Results saved to: {output_file}")

async def main():
    """Main function"""
    print("🏥 HIGH-ACCURACY HEALTHCARE Q&A SYSTEM FOR LLAMA 3.1 70B")
    print("=" * 70)

    qa_system = HighAccuracyHealthcareQA()

    # Process questions
    test_file = "Healthcare-AI-Refactored/src/infrastructure/test.csv"
    results = await qa_system.process_questions_high_accuracy(test_file)

    if results:
        # Save results
        output_file = "high_accuracy_healthcare_submission.csv"
        qa_system.save_results(results, output_file)

        # Print detailed summary
        total_questions = len(results)
        high_confidence = sum(1 for r in results if r['confidence'] > 0.7)
        validation_passed = sum(1 for r in results if r['validation_passed'])
        emergency_questions = sum(1 for r in results if r['urgency_level'] >= 4)
        avg_confidence = sum(r['confidence'] for r in results) / total_questions
        avg_context_relevance = sum(r['context_relevance'] for r in results) / total_questions

        print(f"\n📊 DETAILED SUMMARY:")
        print(f"  Total questions: {total_questions}")
        print(f"  High confidence answers: {high_confidence} ({high_confidence/total_questions*100:.1f}%)")
        print(f"  Validation passed: {validation_passed} ({validation_passed/total_questions*100:.1f}%)")
        print(f"  Emergency questions: {emergency_questions}")
        print(f"  Average confidence: {avg_confidence:.3f}")
        print(f"  Average context relevance: {avg_context_relevance:.3f}")
        
        # Question type breakdown
        type_counts = Counter(r['question_type'] for r in results)
        print(f"\n📋 Question Type Breakdown:")
        for qtype, count in type_counts.most_common():
            print(f"  {qtype}: {count} ({count/total_questions*100:.1f}%)")
    else:
        print("❌ No results generated")

if __name__ == "__main__":
    asyncio.run(main()) 