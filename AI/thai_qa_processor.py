"""
Thai Healthcare Q&A System
Processes Thai multiple-choice questions about Thailand's health insurance system
using information from direct_extraction_corrected.txt files.
"""

import threading
import time  # เพิ่มบรรทัดนี้
import concurrent.futures  # เพิ่มบรรทัดนี้
from queue import Queue  # เพิ่มบรรทัดนี้
from langchain_ollama.llms import OllamaLLM
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
import os
import re
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional


class ThaiHealthcareQA:
    def __init__(self):
        """Initialize the Thai Healthcare Q&A system"""
        self.model = OllamaLLM(model="llama3.2")
        self.embeddings = OllamaEmbeddings(model="mxbai-embed-large")
        self.db_location = "./thai_healthcare_db"
        self.vector_store = None
        self.retriever = None
        
        # Knowledge cache system
        self.knowledge_cache_file = "./knowledge_cache.json"
        self.knowledge_cache = self.load_knowledge_cache()
        self.cache_enabled = True

        # Thread safety
        self.cache_lock = threading.Lock()
        self.stats_lock = threading.Lock()
        self.thread_stats = {
            'processed': 0,
            'successful': 0,
            'errors': 0
        }
        
        # Thai Q&A prompt template
        self.prompt_template = """
คุณเป็นผู้ช่วยที่เชี่ยวชาญในการตอบคำถามเกี่ยวกับระบบหลักประกันสุखภาพแห่งชาติของไทย

ใช้ข้อมูลต่อไปนี้ในการตอบคำถาม:
{context}

คำถาม: {question}
ตัวเลือก:
{choices}

คำสั่ง:
1. วิเคราะห์คำถามและตัวเลือกทั้งหมด
2. ตรวจสอบแต่ละตัวเลือกกับข้อมูลที่ให้มา
3. เลือกคำตอบที่ถูกต้องทั้งหมด (อาจมีมากกว่าหนึ่งข้อ)
4. ตอบเฉพาะตัวอักษรเท่านั้น

รูปแบบการตอบ:
ตอบเฉพาะตัวอักษรที่ถูกต้อง เช่น "ก" หรือ "ก, ค" หรือ "ข, ค, ง"

หากไม่มีคำตอบที่ถูกต้องตามข้อมูล ให้ตอบ: "ไม่มีคำตอบที่ถูกต้อง"
"""

        # Information extraction template
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

        self.setup_vector_database()

    def load_healthcare_documents(self) -> List[Document]:
        """Load and process healthcare documents from all available files"""
        documents = []
        
        # List of healthcare document files
        healthcare_files = [
            "results_doc/direct_extraction_corrected.txt",
            "results_doc2/direct_extraction_corrected.txt", 
            "results_doc3/direct_extraction_corrected.txt"
        ]
        
        for file_path in healthcare_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Split content by pages for better chunking
                    pages = re.split(r'--- Page \d+ ---', content)
                    
                    for i, page_content in enumerate(pages):
                        if page_content.strip():
                            # Create document for each page
                            doc = Document(
                                page_content=page_content.strip(),
                                metadata={
                                    "source": file_path,
                                    "page": i,
                                    "type": "healthcare_guide"
                                }
                            )
                            documents.append(doc)
                            
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
            else:
                print(f"File not found: {file_path}")
        
        print(f"Loaded {len(documents)} document chunks from healthcare files")
        return documents

    def setup_vector_database(self):
        """Set up the vector database with healthcare documents"""
        # Check if database already exists
        add_documents = not os.path.exists(self.db_location)
        
        if add_documents:
            print("Creating new vector database...")
            documents = self.load_healthcare_documents()
            
            if not documents:
                raise ValueError("No healthcare documents found to load!")
            
            # Create vector store
            self.vector_store = Chroma(
                collection_name="thai_healthcare",
                persist_directory=self.db_location,
                embedding_function=self.embeddings
            )
            
            # Add documents to vector store
            self.vector_store.add_documents(documents=documents)
            print("Documents added to vector database")
        else:
            print("Loading existing vector database...")
            self.vector_store = Chroma(
                collection_name="thai_healthcare",
                persist_directory=self.db_location,
                embedding_function=self.embeddings
            )
        
        # Create retriever
        self.retriever = self.vector_store.as_retriever(
            search_kwargs={"k": 5}
        )

    def load_knowledge_cache(self) -> Dict[str, Any]:
        """Load knowledge cache from file"""
        try:
            if os.path.exists(self.knowledge_cache_file):
                with open(self.knowledge_cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                print(f"📚 Loaded {len(cache.get('facts', []))} cached facts")
                return cache
        except Exception as e:
            print(f"⚠️  Error loading cache: {e}")
        
        return {"facts": [], "last_updated": None, "version": "1.0"}

    def save_knowledge_cache(self):
        """Save knowledge cache to file"""
        try:
            self.knowledge_cache["last_updated"] = datetime.now().isoformat()
            with open(self.knowledge_cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_cache, f, ensure_ascii=False, indent=2)
            print(f"💾 Saved cache with {len(self.knowledge_cache['facts'])} facts")
        except Exception as e:
            print(f"❌ Error saving cache: {e}")

    def extract_information(self, question: str, answer: str) -> Optional[Dict[str, Any]]:
        """Extract key information from question-answer pair using AI"""
        if not self.cache_enabled:
            return None
        
        try:
            prompt = ChatPromptTemplate.from_template(self.extraction_template)
            chain = prompt | self.model
            
            result = chain.invoke({
                "question": question,
                "answer": answer
            })
            
            # Try to parse JSON response
            try:
                # Clean up the response to extract JSON
                json_start = result.find('{')
                json_end = result.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = result[json_start:json_end]
                    extracted_info = json.loads(json_str)
                    
                    # Add metadata
                    if "facts" in extracted_info and extracted_info["facts"]:
                        for fact in extracted_info["facts"]:
                            fact["timestamp"] = datetime.now().isoformat()
                            fact["source_question"] = question[:100] + "..." if len(question) > 100 else question
                    
                    return extracted_info
                    
            except json.JSONDecodeError:
                print(f"⚠️  Could not parse extraction result as JSON: {result[:200]}...")
                return None
                
        except Exception as e:
            print(f"❌ Error extracting information: {e}")
            return None

    def add_to_cache(self, extracted_info: Dict[str, Any]):
        """Add extracted information to knowledge cache"""
        if not extracted_info or not extracted_info.get("facts"):
            return
        
        relevance_score = extracted_info.get("relevance_score", 0)
        
        # Only cache information with decent relevance score
        if relevance_score >= 5:
            for fact in extracted_info["facts"]:
                # Create a hash to avoid duplicates
                fact_hash = hashlib.md5(
                    f"{fact['type']}:{fact['key']}:{fact['value']}".encode()
                ).hexdigest()[:8]
                
                fact["id"] = fact_hash
                
                # Check if already exists
                existing_ids = {f.get("id") for f in self.knowledge_cache["facts"]}
                if fact_hash not in existing_ids:
                    self.knowledge_cache["facts"].append(fact)
                    print(f"✅ Cached: {fact['type']} - {fact['key']}")

    def search_cached_knowledge(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search cached knowledge for relevant facts"""
        if not self.knowledge_cache["facts"]:
            return []
        
        relevant_facts = []
        query_lower = query.lower()
        
        for fact in self.knowledge_cache["facts"]:
            # Simple relevance scoring based on keyword matching
            score = 0
            fact_text = f"{fact['key']} {fact['value']} {fact.get('context', '')}".lower()
            
            # Check for keyword matches
            query_words = query_lower.split()
            for word in query_words:
                if len(word) > 2 and word in fact_text:
                    score += 1
            
            if score > 0:
                fact_copy = fact.copy()
                fact_copy["search_score"] = score
                relevant_facts.append(fact_copy)
        
        # Sort by relevance score and return top results
        relevant_facts.sort(key=lambda x: x["search_score"], reverse=True)
        return relevant_facts[:top_k]

    def parse_question(self, question_text: str) -> Dict[str, Any]:
        """Parse a Thai multiple choice question"""
        # Handle both multi-line and single-line CSV formats
        text = question_text.strip()
        
        # Check if this is a single-line CSV format (choices embedded in question)
        if '\n' not in text and any(letter in text for letter in ['ก.', 'ข.', 'ค.', 'ง.']):
            return self._parse_single_line_format(text)
        else:
            return self._parse_multi_line_format(text)
    
    def _parse_single_line_format(self, text: str) -> Dict[str, Any]:
        """Parse single-line CSV format: question  ก. choice1 ข. choice2 ค. choice3 ง. choice4"""
        choices = {}
        
        # Find all Thai choice patterns in the text
        choice_pattern = r'([ก-ง])\.\s*(.+?)(?=\s+[ก-ง]\.|$)'
        matches = re.findall(choice_pattern, text)
        
        for letter, choice_text in matches:
            choices[letter] = choice_text.strip()
        
        # Extract question part (everything before the first choice)
        first_choice_match = re.search(r'\s+([ก-ง])\.', text)
        if first_choice_match:
            question = text[:first_choice_match.start()].strip()
        else:
            question = text.strip()
        
        return {
            "question": question,
            "choices": choices
        }
    
    def _parse_multi_line_format(self, text: str) -> Dict[str, Any]:
        """Parse multi-line format where each choice is on a separate line"""
        lines = text.split('\n')
        
        # Find the main question (usually the first few lines before choices)
        question_lines = []
        choices = {}
        
        current_section = "question"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a choice (starts with ก., ข., ค., ง.)
            choice_match = re.match(r'^([ก-ง])[.\s]*(.+)', line)
            if choice_match:
                current_section = "choices"
                choice_letter = choice_match.group(1)
                choice_text = choice_match.group(2)
                choices[choice_letter] = choice_text
            elif current_section == "question":
                question_lines.append(line)
        
        question = ' '.join(question_lines)
        
        return {
            "question": question,
            "choices": choices
        }

    def format_choices_for_prompt(self, choices: Dict[str, str]) -> str:
        """Format choices for the prompt"""
        formatted = []
        for letter in ['ก', 'ข', 'ค', 'ง']:
            if letter in choices:
                formatted.append(f"{letter}. {choices[letter]}")
        return '\n'.join(formatted)

    def answer_question(self, question_text: str, enable_caching: bool = True) -> str:
        """Answer a Thai question (multiple choice or open-ended) with enhanced knowledge caching"""
        try:
            # Check if this is a multiple choice question or open-ended
            if any(letter in question_text for letter in ['ก.', 'ข.', 'ค.', 'ง.']):
                return self._answer_multiple_choice(question_text, enable_caching)
            else:
                return self._answer_open_ended(question_text, enable_caching)
                
        except Exception as e:
            return f"เกิดข้อผิดพลาด: {str(e)}"

    def _answer_multiple_choice(self, question_text: str, enable_caching: bool = True) -> str:
        """Answer a multiple choice question"""
        try:
            # Parse the question
            parsed = self.parse_question(question_text)
            question = parsed["question"]
            choices = parsed["choices"]
            
            if not question or not choices:
                return "ไม่สามารถแยกวิเคราะห์คำถามได้ กรุณาตรวจสอบรูปแบบคำถาม"
            
            # Retrieve relevant context from original documents
            context_docs = self.retriever.invoke(question)
            document_context = "\n\n".join([doc.page_content for doc in context_docs])
            
            # Search cached knowledge for relevant facts
            cached_facts = self.search_cached_knowledge(question)
            cached_context = ""
            if cached_facts:
                cached_context = "\n\n=== ข้อมูลจากการเรียนรู้ก่อนหน้า ===\n"
                for fact in cached_facts:
                    cached_context += f"• {fact['type']}: {fact['key']} - {fact['value']}"
                    if fact.get('context'):
                        cached_context += f" ({fact['context']})"
                    cached_context += "\n"
                print(f"🧠 Using {len(cached_facts)} cached facts")
            
            # Combine contexts
            full_context = document_context
            if cached_context:
                full_context += "\n" + cached_context
            
            # Format choices
            formatted_choices = self.format_choices_for_prompt(choices)
            
            # Create enhanced prompt
            enhanced_prompt_template = self.prompt_template + """

หมายเหตุ: ใช้ทั้งข้อมูลจากเอกสารหลักและข้อมูลที่เรียนรู้จากคำถามก่อนหน้าในการตอบ
"""
            
            prompt = ChatPromptTemplate.from_template(enhanced_prompt_template)
            chain = prompt | self.model
            
            # Generate answer
            result = chain.invoke({
                "context": full_context,
                "question": question,
                "choices": formatted_choices
            })
            
            # Extract and cache information from this Q&A pair
            if enable_caching and self.cache_enabled:
                try:
                    extracted_info = self.extract_information(question, result)
                    if extracted_info:
                        self.add_to_cache(extracted_info)
                        # Save cache periodically (every 5 new facts)
                        if len(self.knowledge_cache["facts"]) % 5 == 0:
                            self.save_knowledge_cache()
                except Exception as e:
                    print(f"⚠️  Cache extraction failed: {e}")
            
            return result
            
        except Exception as e:
            return f"เกิดข้อผิดพลาด: {str(e)}"

    def _answer_open_ended(self, question_text: str, enable_caching: bool = True) -> str:
        """Answer an open-ended question using both documents and cached knowledge"""
        try:
            question = question_text.strip()
            
            # Retrieve relevant context from original documents
            context_docs = self.retriever.invoke(question)
            document_context = "\n\n".join([doc.page_content for doc in context_docs])
            
            # Search cached knowledge for relevant facts
            cached_facts = self.search_cached_knowledge(question)
            cached_context = ""
            if cached_facts:
                cached_context = "\n\n=== ข้อมูลจากการเรียนรู้ก่อนหน้า ===\n"
                for fact in cached_facts:
                    cached_context += f"• {fact['type']}: {fact['key']} - {fact['value']}"
                    if fact.get('context'):
                        cached_context += f" ({fact['context']})"
                    cached_context += "\n"
                print(f"🧠 Using {len(cached_facts)} cached facts for open-ended question")
            
            # Combine contexts
            full_context = document_context
            if cached_context:
                full_context += "\n" + cached_context
            
            # Create open-ended prompt template
            open_ended_template = """
คุณเป็นผู้ช่วยที่เชี่ยวชาญในการตอบคำถามเกี่ยวกับระบบหลักประกันสุขภาพแห่งชาติของไทย

ใช้ข้อมูลต่อไปนี้ในการตอบคำถาม:
{context}

คำถาม: {question}

คำสั่ง:
1. ตอบคำถามอย่างชัดเจนและครบถ้วน
2. ใช้ข้อมูลจากเอกสารหลักและข้อมูลที่เรียนรู้มาก่อนหน้า
3. ถ้าไม่มีข้อมูลเพียงพอ ให้บอกว่า "ไม่พบข้อมูลที่เกี่ยวข้องในฐานข้อมูล"
4. ตอบเป็นภาษาไทยและให้ข้อมูลที่เป็นประโยชน์

หมายเหตุ: ใช้ทั้งข้อมูลจากเอกสารหลักและข้อมูลที่เรียนรู้จากคำถามก่อนหน้าในการตอบ
"""
            
            prompt = ChatPromptTemplate.from_template(open_ended_template)
            chain = prompt | self.model
            
            # Generate answer
            result = chain.invoke({
                "context": full_context,
                "question": question
            })
            
            # Extract and cache information from this Q&A pair (if meaningful answer was generated)
            if enable_caching and self.cache_enabled and "ไม่พบข้อมูล" not in result:
                try:
                    extracted_info = self.extract_information(question, result)
                    if extracted_info:
                        self.add_to_cache(extracted_info)
                        # Save cache periodically (every 5 new facts)
                        if len(self.knowledge_cache["facts"]) % 5 == 0:
                            self.save_knowledge_cache()
                except Exception as e:
                    print(f"⚠️  Cache extraction failed: {e}")
            
            return result
            
        except Exception as e:
            return f"เกิดข้อผิดพลาด: {str(e)}"

    def interactive_qa(self):
        """Run interactive Q&A session"""
        print("\n=== ระบบตอบคำถามเกี่ยวกับหลักประกันสุขภาพแห่งชาติ ===")
        print("กรุณาใส่คำถามพร้อมตัวเลือก (พิมพ์ 'quit' เพื่อออก)")
        print("\nตัวอย่างรูปแบบ:")
        print("ผมปวดท้องมาก อ้วกด้วย ตอนนี้ตีสองยังมีแผนกไหนเปิดอยู่ไหมครับ?")
        print("ก. Endocrinology")
        print("ข. Orthopedics")
        print("ค. Emergency")
        print("ง. Internal Medicine")
        print("\n" + "="*60)
        
        while True:
            print("\nกรุณาใส่คำถาม (หรือ 'quit' เพื่อออก):")
            question = input().strip()
            
            if question.lower() == 'quit':
                print("ขอบคุณที่ใช้บริการ!")
                break
            
            if not question:
                continue
            
            # Collect multi-line input for choices
            print("กรุณาใส่ตัวเลือก (กด Enter เมื่อเสร็จ):")
            choices_lines = []
            while True:
                line = input()
                if not line.strip():
                    break
                choices_lines.append(line)
            
            full_question = question + "\n" + "\n".join(choices_lines)
            
            print("\n" + "="*60)
            print("กำลังประมวลผล...")
            
            answer = self.answer_question(full_question)
            print("\nคำตอบ:")
            print(answer)
            print("="*60)
    
    def process_csv_questions(self, csv_file_path: str, output_file_path: str = None, clean_format: bool = False) -> None:
        """Process all questions from CSV file and save answers
        
        Args:
            csv_file_path: Path to input CSV file
            output_file_path: Path to output CSV file (optional)
            clean_format: If True, output only id,answer columns (default: id,question,answer)
        """
        import csv
        import os
        from datetime import datetime
        
        print(f"🚀 เริ่มประมวลผล CSV: {csv_file_path}")
        
        # Default output file if not provided
        if output_file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file_path = f"thai_qa_answers_{timestamp}.csv"
        
        results = []
        
        try:
            # Read CSV file
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                questions = list(reader)
            
            total_questions = len(questions)
            print(f"📝 พบคำถามทั้งหมด: {total_questions} ข้อ")
            print("=" * 60)
            
            # Process each question
            for i, row in enumerate(questions, 1):
                question_id = row['id']
                question_text = row['question']
                
                print(f"⏳ กำลังประมวลผลคำถาม {i}/{total_questions} (ID: {question_id})")
                
                try:
                    # Get answer from AI
                    answer = self.answer_question(question_text)
                    
                    # Clean up answer (remove extra whitespace, newlines)
                    clean_answer = ' '.join(answer.split())
                    
                    results.append({
                        'id': question_id,
                        'question': question_text,
                        'answer': clean_answer
                    })
                    
                    print(f"✅ คำตอบ: {clean_answer}")
                    
                except Exception as e:
                    error_msg = f"ข้อผิดพลาด: {str(e)}"
                    results.append({
                        'id': question_id,
                        'question': question_text,
                        'answer': error_msg
                    })
                    print(f"❌ {error_msg}")
                
                print("-" * 40)
            
            # Save results to CSV
            with open(output_file_path, 'w', encoding='utf-8', newline='') as file:
                if clean_format:
                    # Clean format: only id and answer columns
                    fieldnames = ['id', 'answer']
                    clean_results = [{'id': r['id'], 'answer': r['answer']} for r in results]
                else:
                    # Standard format: id, question, and answer columns
                    fieldnames = ['id', 'question', 'answer']
                    clean_results = results
                
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(clean_results)
            
            print("=" * 60)
            print(f"🎉 เสร็จสิ้น! บันทึกผลลัพธ์ที่: {output_file_path}")
            print(f"📊 สถิติ:")
            print(f"   - คำถามทั้งหมด: {total_questions}")
            print(f"   - ประมวลผลสำเร็จ: {len([r for r in results if not r['answer'].startswith('ข้อผิดพลาด')])}")
            print(f"   - เกิดข้อผิดพลาด: {len([r for r in results if r['answer'].startswith('ข้อผิดพลาด')])}")
            
            # Save final cache
            if self.cache_enabled:
                self.save_knowledge_cache()
                print(f"💾 Final cache: {len(self.knowledge_cache['facts'])} facts saved")
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการอ่านไฟล์: {str(e)}")
    
    def process_csv_batch(self, csv_file_path: str, batch_size: int = 10, output_file_path: str = None) -> None:
        """Process CSV in smaller batches to prevent memory issues"""
        import csv
        import os
        from datetime import datetime
        
        print(f"🚀 เริ่มประมวลผลแบบ Batch: {csv_file_path}")
        print(f"📦 ขนาด Batch: {batch_size} คำถาม")
        
        # Default output file if not provided
        if output_file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file_path = f"thai_qa_answers_batch_{timestamp}.csv"
        
        try:
            # Read CSV file
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                questions = list(reader)
            
            total_questions = len(questions)
            total_batches = (total_questions + batch_size - 1) // batch_size
            
            print(f"📝 คำถามทั้งหมด: {total_questions} ข้อ")
            print(f"📦 จำนวน Batch: {total_batches}")
            print("=" * 60)
            
            # Process in batches
            all_results = []
            
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, total_questions)
                batch_questions = questions[start_idx:end_idx]
                
                print(f"🔄 Batch {batch_num + 1}/{total_batches} (คำถาม {start_idx + 1}-{end_idx})")
                
                batch_results = []
                for i, row in enumerate(batch_questions):
                    question_id = row['id']
                    question_text = row['question']
                    
                    try:
                        answer = self.answer_question(question_text)
                        clean_answer = ' '.join(answer.split())
                        
                        batch_results.append({
                            'id': question_id,
                            'question': question_text,
                            'answer': clean_answer
                        })
                        
                        print(f"  ✅ Q{question_id}: {clean_answer}")
                        
                    except Exception as e:
                        error_msg = f"ข้อผิดพลาด: {str(e)}"
                        batch_results.append({
                            'id': question_id,
                            'question': question_text,
                            'answer': error_msg
                        })
                        print(f"  ❌ Q{question_id}: {error_msg}")
                
                all_results.extend(batch_results)
                print(f"✅ Batch {batch_num + 1} เสร็จสิ้น")
                print("-" * 40)
            
            # Save all results
            with open(output_file_path, 'w', encoding='utf-8', newline='') as file:
                fieldnames = ['id', 'question', 'answer']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_results)
            
            print("=" * 60)
            print(f"🎉 เสร็จสิ้นทั้งหมด! บันทึกที่: {output_file_path}")
            
            # Statistics
            successful = len([r for r in all_results if not r['answer'].startswith('ข้อผิดพลาด')])
            errors = len([r for r in all_results if r['answer'].startswith('ข้อผิดพลาด')])
            
            print(f"📊 สถิติ:")
            print(f"   - คำถามทั้งหมด: {total_questions}")
            print(f"   - ประมวลผลสำเร็จ: {successful}")
            print(f"   - เกิดข้อผิดพลาด: {errors}")
            print(f"   - อัตราความสำเร็จ: {(successful/total_questions)*100:.1f}%")
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการประมวลผล: {str(e)}")

    def show_cache_stats(self):
        """Display cache statistics"""
        facts = self.knowledge_cache.get("facts", [])
        print(f"\n📊 Knowledge Cache Statistics:")
        print(f"   Total facts: {len(facts)}")
        
        if facts:
            # Count by type
            type_counts = {}
            for fact in facts:
                fact_type = fact.get("type", "Unknown")
                type_counts[fact_type] = type_counts.get(fact_type, 0) + 1
            
            print(f"   Facts by type:")
            for fact_type, count in sorted(type_counts.items()):
                print(f"     - {fact_type}: {count}")
            
            last_updated = self.knowledge_cache.get("last_updated")
            if last_updated:
                print(f"   Last updated: {last_updated}")

    def clear_cache(self):
        """Clear the knowledge cache"""
        self.knowledge_cache = {"facts": [], "last_updated": None, "version": "1.0"}
        try:
            if os.path.exists(self.knowledge_cache_file):
                os.remove(self.knowledge_cache_file)
            print("🗑️  Knowledge cache cleared")
        except Exception as e:
            print(f"❌ Error clearing cache: {e}")

    def export_cache_to_text(self, filename: str = "knowledge_cache_export.txt"):
        """Export cache to readable text file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# Thai Healthcare Knowledge Cache Export\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n")
                f.write(f"# Total facts: {len(self.knowledge_cache['facts'])}\n\n")
                
                # Group by type
                facts_by_type = {}
                for fact in self.knowledge_cache["facts"]:
                    fact_type = fact.get("type", "Unknown")
                    if fact_type not in facts_by_type:
                        facts_by_type[fact_type] = []
                    facts_by_type[fact_type].append(fact)
                
                for fact_type, facts in sorted(facts_by_type.items()):
                    f.write(f"## {fact_type}\n\n")
                    for fact in facts:
                        f.write(f"**{fact['key']}**: {fact['value']}")
                        if fact.get('context'):
                            f.write(f" ({fact['context']})")
                        f.write(f"\n  - Source: {fact.get('source_question', 'Unknown')}\n")
                        f.write(f"  - Timestamp: {fact.get('timestamp', 'Unknown')}\n\n")
                
            print(f"📄 Cache exported to: {filename}")
            
        except Exception as e:
            print(f"❌ Error exporting cache: {e}")

    def _process_single_question_thread_safe(self, question_data):
        """Thread-safe version of processing a single question"""
        question_id = question_data['id']
        question_text = question_data['question']
        
        try:
            # Get answer from AI
            answer = self.answer_question(question_text, enable_caching=True)
            
            # Clean up answer
            clean_answer = ' '.join(answer.split())
            
            # Update thread-safe stats
            with self.stats_lock:
                self.thread_stats['processed'] += 1
                self.thread_stats['successful'] += 1
            
            return {
                'id': question_id,
                'question': question_text,
                'answer': clean_answer,
                'status': 'success'
            }
            
        except Exception as e:
            error_msg = f"ข้อผิดพลาด: {str(e)}"
            
            # Update thread-safe stats
            with self.stats_lock:
                self.thread_stats['processed'] += 1
                self.thread_stats['errors'] += 1
            
            return {
                'id': question_id,
                'question': question_text,
                'answer': error_msg,
                'status': 'error'
            }
        
    def process_csv_multithreaded(self, csv_file_path: str, output_file_path: str = None, 
                                 max_threads: int = 120, clean_format: bool = False) -> None:
        """Process CSV questions using multiple threads (up to 120 threads)"""
        import csv
        import os
        from datetime import datetime
        
        print(f"🚀 เริ่มประมวลผลแบบ Multi-threaded: {csv_file_path}")
        print(f"🔧 จำนวน Threads: {max_threads}")
        
        # Default output file if not provided
        if output_file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file_path = f"thai_qa_answers_threaded_{timestamp}.csv"
        
        # Reset thread stats
        with self.stats_lock:
            self.thread_stats = {'processed': 0, 'successful': 0, 'errors': 0}
        
        try:
            # Read CSV file
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                questions = list(reader)
            
            total_questions = len(questions)
            print(f"📝 คำถามทั้งหมด: {total_questions} ข้อ")
            print("=" * 60)
            
            # Start processing with thread pool
            start_time = time.time()  # ใช้ time จาก import
            results = [None] * total_questions
            
            # Process questions using ThreadPoolExecutor
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
                # Submit all tasks
                future_to_index = {}
                for i, question_data in enumerate(questions):
                    future = executor.submit(self._process_single_question_thread_safe, question_data)
                    future_to_index[future] = i
                
                # Progress tracking
                completed = 0
                for future in concurrent.futures.as_completed(future_to_index):
                    index = future_to_index[future]
                    completed += 1
                    
                    try:
                        result = future.result()
                        results[index] = result
                        
                        # Show progress
                        if completed % 50 == 0 or completed == total_questions:
                            progress = (completed / total_questions) * 100
                            print(f"⏳ ความคืบหน้า: {completed}/{total_questions} ({progress:.1f}%)")
                        
                    except Exception as e:
                        # Fallback error handling
                        question_data = questions[index]
                        results[index] = {
                            'id': question_data['id'],
                            'question': question_data['question'],
                            'answer': f"Thread error: {str(e)}",
                            'status': 'thread_error'
                        }
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            print(f"\n⏱️  เวลาประมวลผลทั้งหมด: {processing_time:.2f} วินาที")
            print(f"⚡ ความเร็วเฉลี่ย: {total_questions/processing_time:.2f} คำถาม/วินาที")
            
            # Save results to CSV
            with open(output_file_path, 'w', encoding='utf-8', newline='') as file:
                if clean_format:
                    fieldnames = ['id', 'answer']
                    clean_results = [{'id': r['id'], 'answer': r['answer']} for r in results]
                else:
                    fieldnames = ['id', 'question', 'answer']
                    clean_results = results
                
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(clean_results)
            
            # Final statistics
            successful_count = sum(1 for r in results if r and r.get('status') == 'success')
            error_count = sum(1 for r in results if r and r.get('status') in ['error', 'thread_error'])
            
            print("=" * 60)
            print(f"🎉 เสร็จสิ้น! บันทึกผลลัพธ์ที่: {output_file_path}")
            print(f"📊 สถิติการประมวลผล:")
            print(f"   - คำถามทั้งหมด: {total_questions}")
            print(f"   - ประมวลผลสำเร็จ: {successful_count}")
            print(f"   - เกิดข้อผิดพลาด: {error_count}")
            print(f"   - อัตราความสำเร็จ: {(successful_count/total_questions)*100:.1f}%")
            print(f"   - เวลาเฉลี่ย/คำถาม: {processing_time/total_questions:.3f} วินาที")
            print(f"   - Threads ที่ใช้: {max_threads}")
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการประมวลผล: {str(e)}")
            import traceback
            traceback.print_exc()

    def add_to_cache(self, extracted_info: Dict[str, Any]):
        """Thread-safe version of add_to_cache"""
        if not extracted_info or not extracted_info.get("facts"):
            return
        
        relevance_score = extracted_info.get("relevance_score", 0)
        
        # Only cache information with decent relevance score
        if relevance_score >= 5:
            with self.cache_lock:  # Thread-safe cache access
                for fact in extracted_info["facts"]:
                    # Create a hash to avoid duplicates
                    fact_hash = hashlib.md5(
                        f"{fact['type']}:{fact['key']}:{fact['value']}".encode()
                    ).hexdigest()[:8]
                    
                    fact["id"] = fact_hash
                    
                    # Check if already exists
                    existing_ids = {f.get("id") for f in self.knowledge_cache["facts"]}
                    if fact_hash not in existing_ids:
                        self.knowledge_cache["facts"].append(fact)
                        print(f"✅ Cached: {fact['type']} - {fact['key']}")

    def process_csv_adaptive_threads(self, csv_file_path: str, output_file_path: str = None, 
                                   clean_format: bool = False) -> None:
        """Adaptive threading based on system resources and question count"""
        import csv
        import psutil
        
        try:
            # Read questions to determine optimal thread count
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                questions = list(reader)
            
            total_questions = len(questions)
            cpu_count = psutil.cpu_count()
            available_memory_gb = psutil.virtual_memory().available / (1024**3)
            
            # Adaptive thread calculation
            if total_questions <= 50:
                optimal_threads = min(20, cpu_count * 2)
            elif total_questions <= 200:
                optimal_threads = min(60, cpu_count * 4)
            else:
                optimal_threads = min(120, cpu_count * 6)
            
            # Adjust based on available memory (rough estimate: 100MB per thread)
            memory_limit_threads = int(available_memory_gb * 10)  # 100MB per thread
            optimal_threads = min(optimal_threads, memory_limit_threads)
            
            print(f"🤖 การปรับแต่งอัตโนมัติ:")
            print(f"   - CPU cores: {cpu_count}")
            print(f"   - Available memory: {available_memory_gb:.1f} GB")
            print(f"   - Questions: {total_questions}")
            print(f"   - Optimal threads: {optimal_threads}")
            
            # Use the multithreaded processor
            self.process_csv_multithreaded(
                csv_file_path=csv_file_path,
                output_file_path=output_file_path,
                max_threads=optimal_threads,
                clean_format=clean_format
            )
            
        except Exception as e:
            print(f"❌ Error in adaptive threading: {e}")
            # Fallback to standard processing
            print("🔄 Falling back to standard processing...")
            self.process_csv_questions(csv_file_path, output_file_path, clean_format)


def main():
    """Main function to run the Thai Healthcare Q&A system"""
    try:
        qa_system = ThaiHealthcareQA()
        qa_system.interactive_qa()
    except Exception as e:
        print(f"Error initializing system: {e}")
        print("Please make sure Ollama is running and the required models are installed.")


if __name__ == "__main__":
    main()