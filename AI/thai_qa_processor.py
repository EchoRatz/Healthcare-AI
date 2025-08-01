"""
Thai Healthcare Q&A System
Processes Thai multiple-choice questions about Thailand's health insurance system
using information from direct_extraction_corrected.txt files.
"""

from langchain_ollama.llms import OllamaLLM
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
import os
import re
from typing import List, Dict, Any


class ThaiHealthcareQA:
    def __init__(self):
        """Initialize the Thai Healthcare Q&A system"""
        self.model = OllamaLLM(model="llama3.2")
        self.embeddings = OllamaEmbeddings(model="mxbai-embed-large")
        self.db_location = "./thai_healthcare_db"
        self.vector_store = None
        self.retriever = None
        
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

    def parse_question(self, question_text: str) -> Dict[str, Any]:
        """Parse a Thai multiple choice question"""
        lines = question_text.strip().split('\n')
        
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

    def answer_question(self, question_text: str) -> str:
        """Answer a Thai multiple choice question"""
        try:
            # Parse the question
            parsed = self.parse_question(question_text)
            question = parsed["question"]
            choices = parsed["choices"]
            
            if not question or not choices:
                return "ไม่สามารถแยกวิเคราะห์คำถามได้ กรุณาตรวจสอบรูปแบบคำถาม"
            
            # Retrieve relevant context
            context_docs = self.retriever.invoke(question)
            context = "\n\n".join([doc.page_content for doc in context_docs])
            
            # Format choices
            formatted_choices = self.format_choices_for_prompt(choices)
            
            # Create prompt
            prompt = ChatPromptTemplate.from_template(self.prompt_template)
            chain = prompt | self.model
            
            # Generate answer
            result = chain.invoke({
                "context": context,
                "question": question,
                "choices": formatted_choices
            })
            
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
    
    def process_csv_questions(self, csv_file_path: str, output_file_path: str = None) -> None:
        """Process all questions from CSV file and save answers"""
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
                fieldnames = ['id', 'question', 'answer']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            
            print("=" * 60)
            print(f"🎉 เสร็จสิ้น! บันทึกผลลัพธ์ที่: {output_file_path}")
            print(f"📊 สถิติ:")
            print(f"   - คำถามทั้งหมด: {total_questions}")
            print(f"   - ประมวลผลสำเร็จ: {len([r for r in results if not r['answer'].startswith('ข้อผิดพลาด')])}")
            print(f"   - เกิดข้อผิดพลาด: {len([r for r in results if r['answer'].startswith('ข้อผิดพลาด')])}")
            
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