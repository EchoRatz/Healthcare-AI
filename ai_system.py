#!/usr/bin/env python3
"""
🤖 AI Query System - ระบบตอบคำถามอัจฉริยะ
ตอบคำถามในรูปแบบที่กำหนดไว้เท่านั้น 3 ประเภท

Author: Refactored Version
Date: 2025-07-31
"""
import os
import json
import hashlib
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class QueryResponse:
    """โครงสร้างข้อมูลสำหรับคำตอบ"""
    message: str
    source: str
    confidence: float
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")


class VectorDatabase:
    """ฐานข้อมูลเวกเตอร์ที่เรียบง่าย"""
    
    def __init__(self, dimension: int = 100):
        self.dimension = dimension
        self.vectors: List[List[float]] = []
        self.metadata: List[Dict] = []
        
    def add_data(self, text: str, category: str = "general") -> bool:
        """เพิ่มข้อมูลลงในฐานข้อมูล"""
        try:
            vector = self._text_to_vector(text)
            metadata = {
                "text": text,
                "category": category,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.vectors.append(vector)
            self.metadata.append(metadata)
            return True
        except Exception as e:
            print(f"❌ Error adding data: {e}")
            return False
    
    def search_similar(self, query_text: str, threshold: float = 0.7, top_k: int = 3) -> List[Dict]:
        """ค้นหาข้อมูลที่คล้ายกัน"""
        if not self.vectors:
            return []
        
        query_vector = self._text_to_vector(query_text)
        results = []
        
        for i, vector in enumerate(self.vectors):
            similarity = self._calculate_similarity(query_vector, vector)
            
            if similarity >= threshold:
                results.append({
                    "similarity": similarity,
                    "metadata": self.metadata[i],
                    "index": i
                })
        
        # เรียงตามความคล้ายกัน
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
    
    def _text_to_vector(self, text: str) -> List[float]:
        """แปลงข้อความเป็นเวกเตอร์"""
        text = text.lower().strip()
        
        # สร้างเวกเตอร์จาก hash ของข้อความ
        vector = []
        for i in range(self.dimension):
            hash_input = f"{text}_{i}"
            hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
            normalized_value = (hash_value % 10000) / 10000.0
            vector.append(normalized_value)
        
        return vector
    
    def _calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """คำนวณ cosine similarity"""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def get_stats(self) -> Dict:
        """ข้อมูลสถิติของฐานข้อมูล"""
        return {
            "total_items": len(self.vectors),
            "dimension": self.dimension,
            "categories": list(set(item.get("category", "unknown") for item in self.metadata))
        }


class WebSearchAnalyzer:
    """ตัววิเคราะห์ว่าควรค้นหาจากเว็บหรือไม่"""
    
    WEB_KEYWORDS = [
        # คำภาษาไทย
        "ข่าว", "ล่าสุด", "ปัจจุบัน", "วันนี้", "ตอนนี้", "ราคา", "สภาพอากาศ",
        "อุณหภูมิ", "หุ้น", "ตลาด", "เหตุการณ์", "สถานการณ์",
        
        # คำภาษาอังกฤษ
        "news", "latest", "current", "today", "now", "price", "weather",
        "temperature", "stock", "market", "event", "situation", "real-time"
    ]
    
    TIME_INDICATORS = [
        "วันนี้", "ตอนนี้", "ปัจจุบัน", "ล่าสุด", "เมื่อไหร่",
        "today", "now", "current", "latest", "when", "real-time"
    ]
    
    @classmethod
    def needs_web_search(cls, query: str) -> bool:
        """ตรวจสอบว่าคำถามต้องการข้อมูลจากเว็บหรือไม่"""
        query_lower = query.lower()
        
        # ตรวจสอบคำที่บ่งบอกว่าต้องการข้อมูลจากเว็บ
        for keyword in cls.WEB_KEYWORDS:
            if keyword in query_lower:
                return True
        
        # ตรวจสอบคำที่บ่งบอกเวลา
        for indicator in cls.TIME_INDICATORS:
            if indicator in query_lower:
                return True
        
        return False


class PersonalQuestionDetector:
    """ตัวตรวจจับคำถามส่วนตัว"""
    
    PERSONAL_INDICATORS = [
        # คำภาษาไทย
        "ฉัน", "กู", "คุณ", "เธอ", "ความคิดเห็น", "รู้สึก", "ชอบ", "เกลียด",
        "อยาก", "ต้องการ", "ควร", "น่าจะ", "คิดว่า", "เห็นด้วย",
        
        # คำภาษาอังกฤษ
        "i ", "you ", "my ", "your ", "opinion", "feel", "like", "love", "hate",
        "want", "should", "think", "believe", "prefer", "agree"
    ]
    
    SUBJECTIVE_WORDS = [
        "ดี", "เลว", "สวย", "น่าเกลียด", "ดีที่สุด", "แย่ที่สุด",
        "good", "bad", "beautiful", "ugly", "best", "worst", "better", "worse"
    ]
    
    @classmethod
    def is_personal_question(cls, query: str) -> bool:
        """ตรวจสอบว่าเป็นคำถามส่วนตัวหรือไม่"""
        query_lower = query.lower()
        
        # ตรวจสอบคำที่บ่งบอกความเป็นส่วนตัว
        for indicator in cls.PERSONAL_INDICATORS:
            if indicator in query_lower:
                return True
        
        # ตรวจสอบคำที่แสดงความคิดเห็นส่วนตัว
        for word in cls.SUBJECTIVE_WORDS:
            if word in query_lower:
                return True
        
        return False


class AIQuerySystem:
    """ระบบ AI สำหรับตอบคำถาม - เวอร์ชันที่ refactor แล้ว"""
    
    # คำตอบที่กำหนดไว้
    RESPONSES = {
        "no_answer": "ไม่สามารถตอบคำถามได้",
        "web_answer": "สามารถตอบคำถามได้โดยใช้ข้อมูลจากอินเตอร์เน็ต",
        "vector_answer": "สามารถตอบคำถามได้โดยใช้ข้อมูลจาก vector database"
    }
    
    def __init__(self, vector_threshold: float = 0.7):
        self.vector_db = VectorDatabase()
        self.vector_threshold = vector_threshold
        self.web_analyzer = WebSearchAnalyzer()
        self.personal_detector = PersonalQuestionDetector()
        
        # เพิ่มข้อมูลตัวอย่าง
        self._load_sample_data()
        
        print("🤖 AI Query System initialized successfully!")
        print(f"📊 Database: {self.vector_db.get_stats()['total_items']} items loaded")
    
    def _load_sample_data(self):
        """โหลดข้อมูลตัวอย่าง"""
        sample_data = [
            ("Python เป็นภาษาโปรแกรมมิ่งที่ใช้งานง่าย เหมาะสำหรับผู้เริ่มต้น", "programming"),
            ("Machine Learning คือการเรียนรู้ของเครื่อง ใช้อัลกอริทึมวิเคราะห์ข้อมูล", "ai"),
            ("Vector Database ใช้สำหรับจัดเก็บข้อมูลแบบเวกเตอร์ เพื่อการค้นหาที่มีประสิทธิภาพ", "database"),
            ("Deep Learning เป็นส่วนหนึ่งของ Machine Learning ที่ใช้ Neural Network", "ai"),
            ("Data Science คือการวิเคราะห์ข้อมูลเพื่อหาข้อมูลเชิงลึก", "data"),
            ("JavaScript เป็นภาษาโปรแกรมมิ่งสำหรับพัฒนาเว็บไซต์", "programming"),
            ("React เป็น JavaScript library สำหรับสร้าง user interface", "web"),
            ("SQL ใช้สำหรับจัดการฐานข้อมูลเชิงสัมพันธ์", "database")
        ]
        
        for text, category in sample_data:
            self.vector_db.add_data(text, category)
    
    def process_query(self, question: str) -> QueryResponse:
        """ประมวลผลคำถามและส่งคืนคำตอบ"""
        if not question or not question.strip():
            return QueryResponse(
                message=self.RESPONSES["no_answer"],
                source="validation_error",
                confidence=1.0
            )
        
        # 1. ตรวจสอบคำถามส่วนตัว
        if self.personal_detector.is_personal_question(question):
            return QueryResponse(
                message=self.RESPONSES["no_answer"],
                source="personal_question",
                confidence=0.9
            )
        
        # 2. ค้นหาใน Vector Database
        vector_results = self.vector_db.search_similar(question, self.vector_threshold)
        if vector_results:
            best_match = vector_results[0]
            return QueryResponse(
                message=self.RESPONSES["vector_answer"],
                source="vector_database",
                confidence=best_match["similarity"]
            )
        
        # 3. ตรวจสอบว่าควรค้นหาจากเว็บ
        if self.web_analyzer.needs_web_search(question):
            return QueryResponse(
                message=self.RESPONSES["web_answer"],
                source="web_search",
                confidence=0.8
            )
        
        # 4. ไม่สามารถตอบได้
        return QueryResponse(
            message=self.RESPONSES["no_answer"],
            source="no_match",
            confidence=0.0
        )
    
    def add_knowledge(self, text: str, category: str = "user_added") -> bool:
        """เพิ่มความรู้ใหม่เข้าสู่ระบบ"""
        return self.vector_db.add_data(text, category)
    
    def get_system_info(self) -> Dict:
        """ข้อมูลของระบบ"""
        db_stats = self.vector_db.get_stats()
        return {
            "system_name": "AI Query System (Refactored)",
            "version": "2.0.0",
            "database_stats": db_stats,
            "vector_threshold": self.vector_threshold,
            "response_types": list(self.RESPONSES.keys())
        }
    
    def search_knowledge(self, query: str, top_k: int = 5) -> List[Dict]:
        """ค้นหาความรู้ในระบบ"""
        return self.vector_db.search_similar(query, threshold=0.3, top_k=top_k)


def run_interactive_demo():
    """โหมดโต้ตอบสำหรับทดสอบระบบ"""
    print("\n" + "="*60)
    print("🤖 AI Query System - Interactive Demo")
    print("="*60)
    print("\nคำสั่งที่ใช้ได้:")
    print("  - พิมพ์คำถามเพื่อทดสอบ")
    print("  - 'add: ข้อความ' เพื่อเพิ่มความรู้")
    print("  - 'search: คำค้นหา' เพื่อค้นหาความรู้")
    print("  - 'info' เพื่อดูข้อมูลระบบ")
    print("  - 'quit' เพื่อออก")
    print("-"*60)
    
    ai_system = AIQuerySystem()
    
    while True:
        try:
            user_input = input("\n💬 คำถาม: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 ขอบคุณที่ใช้งาน!")
                break
            
            elif user_input.startswith('add:'):
                knowledge = user_input[4:].strip()
                if ai_system.add_knowledge(knowledge):
                    print(f"✅ เพิ่มความรู้สำเร็จ: {knowledge}")
                else:
                    print("❌ เพิ่มความรู้ไม่สำเร็จ")
            
            elif user_input.startswith('search:'):
                query = user_input[7:].strip()
                results = ai_system.search_knowledge(query)
                
                if results:
                    print(f"🔍 พบ {len(results)} ผลลัพธ์:")
                    for i, result in enumerate(results, 1):
                        text = result['metadata']['text'][:50] + "..."
                        similarity = result['similarity'] * 100
                        print(f"  {i}. [{similarity:.1f}%] {text}")
                else:
                    print("❌ ไม่พบข้อมูลที่ตรงกัน")
            
            elif user_input.lower() == 'info':
                info = ai_system.get_system_info()
                print(f"📊 ข้อมูลระบบ:")
                print(f"  - ชื่อ: {info['system_name']}")
                print(f"  - เวอร์ชัน: {info['version']}")
                print(f"  - จำนวนข้อมูล: {info['database_stats']['total_items']}")
                print(f"  - หมวดหมู่: {', '.join(info['database_stats']['categories'])}")
            
            else:
                # ประมวลผลคำถามปกติ
                response = ai_system.process_query(user_input)
                
                print(f"\n🎯 คำตอบ: {response.message}")
                print(f"📍 แหล่งที่มา: {response.source}")
                print(f"🎲 ความมั่นใจ: {response.confidence:.2f}")
                print(f"⏰ เวลา: {response.timestamp}")
        
        except KeyboardInterrupt:
            print("\n👋 ขอบคุณที่ใช้งาน!")
            break
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")


def run_test_suite():
    """ชุดทดสอบระบบ"""
    print("\n" + "="*60)
    print("🧪 Running Test Suite")
    print("="*60)
    
    ai_system = AIQuerySystem()
    
    test_cases = [
        # คำถามที่ควรตอบจาก Vector Database
        ("Python คืออะไร", "vector_answer"),
        ("Machine Learning คืออะไร", "vector_answer"),
        ("Vector Database คืออะไร", "vector_answer"),
        
        # คำถามที่ควรตอบจากเว็บ
        ("ข่าวล่าสุดวันนี้", "web_answer"),
        ("ราคาทองคำปัจจุบัน", "web_answer"),
        ("สภาพอากาศตอนนี้", "web_answer"),
        
        # คำถามส่วนตัวที่ไม่ควรตอบ
        ("ฉันชอบสีอะไร", "no_answer"),
        ("คุณคิดว่าฉันสวยไหม", "no_answer"),
        ("ความคิดเห็นของคุณเกี่ยวกับการเมือง", "no_answer"),
        
        # คำถามที่ไม่สามารถตอบได้
        ("abcdefghijk", "no_answer"),
        ("คำถามที่แปลกประหลาด", "no_answer")
    ]
    
    correct = 0
    total = len(test_cases)
    
    for i, (question, expected) in enumerate(test_cases, 1):
        response = ai_system.process_query(question)
        expected_message = ai_system.RESPONSES[expected]
        is_correct = response.message == expected_message
        
        status = "✅" if is_correct else "❌"
        print(f"{status} Test {i:2d}: {question}")
        print(f"     Expected: {expected}")
        print(f"     Got: {response.source} ({response.confidence:.2f})")
        
        if is_correct:
            correct += 1
        print()
    
    accuracy = (correct / total) * 100
    print(f"📊 ผลการทดสอบ: {correct}/{total} ({accuracy:.1f}%)")
    
    if accuracy == 100:
        print("🎉 ผ่านการทดสอบทั้งหมด!")
    else:
        print("⚠️  มีการทดสอบที่ไม่ผ่าน กรุณาตรวจสอบ")


def main():
    """หน้าต่างหลักของโปรแกรม"""
    print("🤖 AI Query System (Refactored Version)")
    print("ระบบตอบคำถามที่ปรับปรุงใหม่ให้อ่านง่ายขึ้น")
    print("\nเลือกโหมดการใช้งาน:")
    print("1. Interactive Demo (โต้ตอบ)")
    print("2. Run Tests (ทดสอบระบบ)")
    print("3. Exit (ออก)")
    
    while True:
        try:
            choice = input("\nเลือก (1-3): ").strip()
            
            if choice == '1':
                run_interactive_demo()
                break
            elif choice == '2':
                run_test_suite()
                break
            elif choice == '3':
                print("👋 ขอบคุณที่ใช้งาน!")
                break
            else:
                print("❌ กรุณาเลือก 1-3")
        
        except KeyboardInterrupt:
            print("\n👋 ขอบคุณที่ใช้งาน!")
            break


if __name__ == "__main__":
    main()
