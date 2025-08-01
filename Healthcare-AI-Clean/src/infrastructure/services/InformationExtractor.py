"""AI-powered information extraction service."""
import json
from typing import Optional, Dict, Any, List
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from ...domain.services.ExtractionService import ExtractionService
from ...domain.entities.CacheEntry import CacheEntry
import hashlib
from datetime import datetime


class InformationExtractor(ExtractionService):
    """AI-powered information extraction implementation."""
    
    def __init__(self, model_name: str = "llama3.2"):
        try:
            self.model = OllamaLLM(model=model_name)
            self._setup_extraction_template()
            self._available = True
        except Exception as e:
            print(f"Error initializing extractor: {e}")
            self._available = False
    
    def extract_information(self, question: str, answer: str) -> Optional[Dict[str, Any]]:
        """Extract key information from question-answer pair using AI."""
        if not self._available:
            return None
        
        try:
            prompt = ChatPromptTemplate.from_template(self.extraction_template)
            chain = prompt | self.model
            
            result = chain.invoke({"question": question, "answer": answer})
            
            return self.parse_extraction_result(result)
            
        except Exception as e:
            print(f"❌ Error extracting information: {e}")
            return None
    
    def parse_extraction_result(self, result: str) -> Optional[Dict[str, Any]]:
        """Parse extraction result."""
        try:
            # Clean up the response to extract JSON
            json_start = result.find("{")
            json_end = result.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = result[json_start:json_end]
                return json.loads(json_str)
            
        except json.JSONDecodeError:
            print(f"⚠️ Could not parse extraction result as JSON: {result[:200]}...")
        
        return None
    
    def create_cache_entries(self, extraction_data: Dict[str, Any]) -> List[CacheEntry]:
        """Create cache entries from extraction data."""
        entries = []
        
        if not extraction_data or not extraction_data.get("facts"):
            return entries
        
        for fact in extraction_data["facts"]:
            entry_id = hashlib.md5(
                f"{fact['type']}:{fact['key']}:{fact['value']}".encode()
            ).hexdigest()[:8]
            
            entry = CacheEntry(
                id=entry_id,
                fact_type=fact["type"],
                key=fact["key"],
                value=fact["value"],
                context=fact.get("context"),
                timestamp=datetime.now(),
                relevance_score=extraction_data.get("relevance_score", 0.0)
            )
            entries.append(entry)
        
        return entries
    
    def _setup_extraction_template(self) -> None:
        """Setup information extraction template."""
        self.extraction_template = """
คุณเป็นผู้เชี่ยวชาญในการสกัดข้อมูลสำคัญจากคำถามและคำตอบเกี่ยวกับระบบสุขภาพไทย

คำถาม: {question}
คำตอบ: {answer}

กรุณาสกัดข้อมูลสำคัญที่มีประโยชน์สำหรับการตอบคำถามในอนาคต:

ประเภทข้อมูลที่ควรสกัด:
1. ราคายา/บริการ (เช่น ยา X ราคา Y บาท)
2. อัตราค่าบริการ (เช่น บริการ X เหมาจ่าย Y บาท/ครั้ง)
3. สิทธิประโยชน์ (เช่น สิทธิ X ครอบคลุม Y)
4. เงื่อนไขการรักษา (เช่น อายุขั้นต่ำ, เงื่อนไข)
5. แผนกและบริการ (เช่น แผนก X เปิด Y เวลา)
6. ระเบียบและกฎหมาย (เช่น กฎ X มีผล Y)

รูปแบบผลลัพธ์ (ตอบเป็น JSON):
{{
  "facts": [
    {{
      "type": "ประเภทข้อมูล",
      "key": "หัวข้อหลัก",
      "value": "ข้อมูลสำคัญ",
      "context": "บริบทเพิ่มเติม"
    }}
  ],
  "relevance_score": 1-10
}}

หากไม่พบข้อมูลที่มีประโยชน์ ให้ตอบ: {{"facts": [], "relevance_score": 0}}
"""