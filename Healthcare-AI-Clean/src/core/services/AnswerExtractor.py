"""Answer extraction service."""
import re
from typing import List


class AnswerExtractor:
    """Service to extract clean answers from AI responses."""
    
    def extract_choice_only(self, ai_response: str) -> str:
        """Extract only the choice letters from AI response."""
        response = ai_response.strip()
        
        # Check for "no answer" phrases first
        no_answer_phrases = [
            "ไม่มีคำตอบที่ถูกต้อง",
            "ไม่มีข้อใดถูกต้อง",
            "ไม่มีตัวเลือกที่ถูกต้อง",
            "ไม่พบข้อมูล",
            "ไม่มีข้อมูล",
            "ข้อมูลไม่เพียงพอ"
        ]
        
        response_lower = response.lower()
        for phrase in no_answer_phrases:
            if phrase.lower() in response_lower:
                return "ไม่มีคำตอบที่ถูกต้อง"
        
        # Look for Thai choice letters
        choice_patterns = [
            r"ตอบ[:\s]*([ก-ง](?:\s*,\s*[ก-ง])*)",
            r"คำตอบ[:\s]*([ก-ง](?:\s*,\s*[ก-ง])*)",
            r'"([ก-ง](?:\s*,\s*[ก-ง])*)"',
            r"([ก-ง](?:\s*,\s*[ก-ง])*)\s*$",
        ]
        
        for pattern in choice_patterns:
            matches = re.findall(pattern, response)
            if matches:
                return matches[-1].strip()
        
        # Look for individual Thai letters
        thai_letters = re.findall(r"[ก-ง]", response)
        if thai_letters:
            unique_letters = []
            for letter in thai_letters:
                if letter not in unique_letters:
                    unique_letters.append(letter)
            
            if 1 <= len(unique_letters) <= 4:
                return ", ".join(unique_letters)
        
        # Fallback
        return response[:50] + "..." if len(response) > 50 else response
    
    def validate_answer_format(self, answer: str) -> bool:
        """Validate if answer is in correct format."""
        answer = answer.strip()
        
        # Check if it's a valid Thai choice letter
        if re.match(r"^[ก-ง]$", answer):
            return True
        
        # Check if it's multiple choice letters
        if re.match(r"^[ก-ง](?:\s*,\s*[ก-ง])*$", answer):
            return True
        
        # Check if it's "no answer" response
        if "ไม่มีคำตอบที่ถูกต้อง" in answer:
            return True
        
        return False