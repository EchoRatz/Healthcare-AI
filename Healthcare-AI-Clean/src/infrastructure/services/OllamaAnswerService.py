"""Ollama AI-powered answer service."""
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from ...domain.entities.Question import Question, Answer
from ...domain.services.AnswerService import AnswerService
from ...core.services.AnswerExtractor import AnswerExtractor


class OllamaAnswerService(AnswerService):
    """Ollama AI implementation of answer service."""
    
    def __init__(self, model_name: str = "llama3.2"):
        try:
            self.model = OllamaLLM(model=model_name)
            self.extractor = AnswerExtractor()
            self._setup_prompt()
            self._available = True
        except Exception as e:
            print(f"Error initializing Ollama: {e}")
            self._available = False
    
    def answer_question(self, question: Question) -> Answer:
        """Answer question using Ollama AI."""
        if not self._available:
            return Answer(question.id, "Service unavailable", confidence=0.0)
        
        try:
            # Format choices for prompt
            choices_text = self._format_choices(question.choices)
            
            # Create prompt
            prompt_input = {
                "question": question.text,
                "choices": choices_text,
                "context": "ใช้ความรู้เกี่ยวกับระบบหลักประกันสุขภาพไทย"
            }
            
            # Get AI response
            chain = self.prompt_template | self.model
            response = chain.invoke(prompt_input)
            
            # Extract clean answer
            clean_answer = self.extract_choice_only(response)
            
            return Answer(
                question_id=question.id,
                answer=clean_answer,
                confidence=0.8 if clean_answer in ["ก", "ข", "ค", "ง"] else 0.5
            )
            
        except Exception as e:
            return Answer(question.id, f"Error: {str(e)}", confidence=0.0)
    
    def extract_choice_only(self, ai_response: str) -> str:
        """Extract choice letters from AI response."""
        return self.extractor.extract_choice_only(ai_response)
    
    def is_available(self) -> bool:
        """Check if service is available."""
        return self._available
    
    def get_service_name(self) -> str:
        """Get service name."""
        return f"Ollama AI Service"
    
    def _setup_prompt(self) -> None:
        """Setup the Thai Q&A prompt template."""
        template = """
คุณเป็นผู้ช่วยที่เชี่ยวชาญในการตอบคำถามเกี่ยวกับระบบหลักประกันสุขภาพแห่งชาติของไทย

ใช้ข้อมูลต่อไปนี้ในการตอบคำถาม:
{context}

คำถาม: {question}
ตัวเลือก:
{choices}

คำสั่ง:
1. วิเคราะห์คำถามและตัวเลือกทั้งหมด
2. ตรวจสอบแต่ละตัวเลือกกับข้อมูลที่ให้มา
3. เลือกคำตอบที่ถูกต้องที่สุด
4. ตอบเฉพาะตัวอักษรเท่านั้น

รูปแบบการตอบ:
ตอบเฉพาะตัวอักษรที่ถูกต้อง เช่น "ก" หรือ "ข" หรือ "ค" หรือ "ง"
ห้ามใส่คำอธิบายเพิ่มเติม ตอบเฉพาะตัวอักษรเท่านั้น

หากไม่มีคำตอบที่ถูกต้องตามข้อมูล ให้ตอบ: "ไม่มีคำตอบที่ถูกต้อง"
"""
        self.prompt_template = ChatPromptTemplate.from_template(template)
    
    def _format_choices(self, choices: Dict[str, str]) -> str:
        """Format choices for prompt."""
        formatted = []
        for letter in ["ก", "ข", "ค", "ง"]:
            if letter in choices:
                formatted.append(f"{letter}. {choices[letter]}")
        return "\n".join(formatted)