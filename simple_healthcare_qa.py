#!/usr/bin/env python3
"""
Simple Healthcare QA System
No external dependencies required - uses local knowledge base only
"""

import os
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class QuestionAnalysis:
    """Analysis of a question's intent and requirements"""
    question_type: str
    keywords: List[str]
    entities: List[str]
    context_needed: List[str]
    confidence: float


class SimpleHealthcareQA:
    """Simple healthcare Q&A system using local knowledge base only"""

    def __init__(self):
        self.knowledge_base = {}
        self.healthcare_policies = self._load_healthcare_policies()
        self.question_patterns = self._load_question_patterns()
        self.load_knowledge_base()

    def load_knowledge_base(self):
        """Load and index knowledge base for better search"""
        print("📚 Loading knowledge base...")
        
        doc_files = [
            "Healthcare-AI-Refactored/src/infrastructure/results_doc/direct_extraction_corrected.txt",
            "Healthcare-AI-Refactored/src/infrastructure/results_doc2/direct_extraction_corrected.txt",
            "Healthcare-AI-Refactored/src/infrastructure/results_doc3/direct_extraction_corrected.txt",
            "Healthcare-AI-Refactored/src/infrastructure/result_mcp/hospital_micro_facts.txt",
        ]
        
        for i, doc_file in enumerate(doc_files, 1):
            if os.path.exists(doc_file):
                with open(doc_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    self._index_document(content, f"doc_{i}")
                    print(f"  ✅ Document {i}: {len(content):,} chars indexed")
            else:
                print(f"  ⚠️  Document {i} not found: {doc_file}")
    
    def _index_document(self, content: str, doc_id: str):
        """Index document content for better search"""
        # Split into sections and index by keywords
        sections = content.split("--- Page")
        
        for section in sections:
            if len(section.strip()) < 50:  # Skip very short sections
                continue
                
            # Extract key terms
            keywords = self._extract_keywords(section)
            
            for keyword in keywords:
                if keyword not in self.knowledge_base:
                    self.knowledge_base[keyword] = []
                self.knowledge_base[keyword].append({
                    'doc_id': doc_id,
                    'content': section,
                    'relevance': self._calculate_relevance(keyword, section)
                })
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        # Thai healthcare specific keywords
        thai_keywords = [
            "สิทธิ", "หลักประกัน", "สุขภาพ", "การรักษา", "ยา", "ตรวจ", "ผ่าตัด",
            "โรงพยาบาล", "แพทย์", "ผู้ป่วย", "ค่าใช้จ่าย", "บริการ", "โรค",
            "การคลอด", "วัคซีน", "ฉุกเฉิน", "ส่งต่อ", "ใบส่งตัว", "บัตรทอง",
            "แผนก", "department", "cardiology", "emergency", "pediatrics"
        ]
        
        # Extract numbers and specific terms
        numbers = re.findall(r'\d+', text)
        specific_terms = re.findall(r'[ก-ฮ]{2,}', text)
        
        keywords = []
        for keyword in thai_keywords:
            if keyword in text:
                keywords.append(keyword)
        
        keywords.extend(numbers[:5])  # Limit numbers
        keywords.extend(specific_terms[:10])  # Limit specific terms
        
        return list(set(keywords))
    
    def _calculate_relevance(self, keyword: str, text: str) -> float:
        """Calculate relevance score for keyword in text"""
        if keyword not in text:
            return 0.0
        
        # Simple frequency-based relevance
        count = text.count(keyword)
        length = len(text)
        return min(count / (length / 1000), 1.0)  # Normalize by text length
    
    def analyze_question(self, question_text: str) -> QuestionAnalysis:
        """Analyze question to understand intent and requirements"""
        question_type = "factual"  # Default
        keywords = []
        entities = []
        context_needed = []
        confidence = 0.5
        
        # Detect question type
        for qtype, patterns in self.question_patterns.items():
            for pattern in patterns:
                if re.search(pattern, question_text):
                    question_type = qtype
                    confidence += 0.2
                    break
        
        # Extract keywords and entities
        keywords = self._extract_keywords(question_text)
        
        # Extract healthcare entities
        for policy, info in self.healthcare_policies.items():
            if any(keyword in question_text for keyword in info["keywords"]):
                entities.append(policy)
                context_needed.extend(info["keywords"])
        
        return QuestionAnalysis(
            question_type=question_type,
            keywords=keywords,
            entities=entities,
            context_needed=context_needed,
            confidence=confidence
        )
    
    def search_context(self, question_analysis: QuestionAnalysis, max_chars: int = 3000) -> str:
        """Search for relevant context based on question analysis"""
        relevant_sections = []
        total_chars = 0
        
        # Search by keywords
        for keyword in question_analysis.keywords:
            if keyword in self.knowledge_base:
                for entry in self.knowledge_base[keyword]:
                    if total_chars + len(entry['content']) <= max_chars:
                        relevant_sections.append(entry['content'])
                        total_chars += len(entry['content'])
                    else:
                        break
        
        # Search by entities
        for entity in question_analysis.entities:
            if entity in self.healthcare_policies:
                policy_info = self.healthcare_policies[entity]
                policy_text = f"Policy: {entity}\nIncludes: {', '.join(policy_info['includes'])}\nExcludes: {', '.join(policy_info['excludes'])}"
                if total_chars + len(policy_text) <= max_chars:
                    relevant_sections.append(policy_text)
                    total_chars += len(policy_text)
        
        return "\n\n".join(relevant_sections)
    
    def _load_healthcare_policies(self) -> Dict:
        """Load comprehensive Thai healthcare policy knowledge"""
        return {
            "สิทธิหลักประกันสุขภาพแห่งชาติ": {
                "includes": [
                    "การตรวจรักษาพยาบาลทั่วไป", "ยาจำเป็น", "การผ่าตัด", "การฟื้นฟู",
                    "การรักษาโรคเรื้อรัง", "การตรวจสุขภาพ", "วัคซีน", "การคลอด",
                    "การรักษาฉุกเฉิน", "การส่งต่อ", "การตรวจทางห้องปฏิบัติการ",
                    "การผ่าตัดฉุกเฉิน", "การรักษาในโรงพยาบาล", "การดูแลผู้ป่วยใน"
                ],
                "excludes": [
                    "การรักษาเสริมความงาม", "ยาแบรนด์เนม", "ค่าห้องพิเศษ",
                    "การรักษาทางเลือก", "การตรวจสุขภาพเพื่อการประกันชีวิต"
                ],
                "keywords": ["บัตรทอง", "หลักประกัน", "สิทธิ", "สวัสดิการ", "ฟรี"]
            },
            "สิทธิประกันสังคม": {
                "includes": [
                    "การรักษาพยาบาล", "ค่าจ้างทดแทน", "เงินชดเชย", "เงินสงเคราะห์",
                    "การฟื้นฟูสมรรถภาพ", "การตรวจสุขภาพ", "การคลอด", "การรักษาโรค"
                ],
                "excludes": [
                    "การรักษาเสริมความงาม", "การตรวจสุขภาพเพื่อการประกันชีวิต"
                ],
                "keywords": ["ประกันสังคม", "ประกัน", "สังคม", "สวัสดิการ"]
            }
        }
    
    def _load_question_patterns(self) -> Dict:
        """Load question pattern recognition rules"""
        return {
            "inclusion": [
                r"ครอบคลุม", r"รวม", r"มีสิทธิ", r"ได้รับ", r"ฟรี", r"ไม่เสียค่าใช้จ่าย"
            ],
            "exclusion": [
                r"ไม่ครอบคลุม", r"ไม่รวม", r"เสียค่าใช้จ่าย", r"ต้องจ่าย", r"ไม่ฟรี"
            ],
            "comparison": [
                r"ต่างกัน", r"เปรียบเทียบ", r"เหมือนกัน", r"ต่างจาก", r"มากกว่า", r"น้อยกว่า"
            ],
            "procedure": [
                r"ขั้นตอน", r"วิธีการ", r"ต้องทำ", r"ต้องไป", r"ต้องมี", r"ต้องเตรียม"
            ]
        }
    
    def answer_question(self, question: str) -> str:
        """Answer a healthcare question using local knowledge"""
        # Analyze question
        analysis = self.analyze_question(question)
        
        # Search for context
        context = self.search_context(analysis)
        
        if not context:
            return "ขออภัย ไม่พบข้อมูลที่เกี่ยวข้องกับคำถามของคุณ"
        
        # Extract relevant information
        relevant_info = context[:800] + "..." if len(context) > 800 else context
        
        # Find matching keywords
        keywords = self._extract_keywords(question)
        matched_keywords = [k for k in keywords if k in self.knowledge_base]
        
        # Build answer
        answer_parts = []
        answer_parts.append(f"📋 ข้อมูลที่เกี่ยวข้อง:")
        answer_parts.append(relevant_info)
        
        if matched_keywords:
            answer_parts.append(f"\n🔍 คำสำคัญที่พบ: {', '.join(matched_keywords[:5])}")
        
        # Add policy information if relevant
        for entity in analysis.entities:
            if entity in self.healthcare_policies:
                policy = self.healthcare_policies[entity]
                answer_parts.append(f"\n📋 นโยบาย {entity}:")
                answer_parts.append(f"  ✅ ครอบคลุม: {', '.join(policy['includes'][:5])}")
                answer_parts.append(f"  ❌ ไม่ครอบคลุม: {', '.join(policy['excludes'][:3])}")
        
        return "\n".join(answer_parts)
    
    def interactive_mode(self):
        """Interactive mode for asking questions"""
        print("🏥 Simple Healthcare QA System")
        print("=" * 50)
        print("Ask healthcare questions! Type 'quit' to exit.")
        print("Note: Uses local knowledge base only.")
        print("-" * 50)
        
        while True:
            try:
                question = input("\n💬 Your question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not question:
                    continue
                
                # Get answer
                answer = self.answer_question(question)
                print(f"\n🤖 Answer:\n{answer}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Main function"""
    print("🏥 Simple Healthcare QA System")
    print("=" * 50)
    
    qa_system = SimpleHealthcareQA()
    qa_system.interactive_mode()


if __name__ == "__main__":
    main() 