"""Interactive Q&A entry point."""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from infrastructure.repositories.CsvQuestionRepository import CsvQuestionRepository
from infrastructure.services.SimpleAnswerService import SimpleAnswerService
from core.services.QuestionParser import QuestionParser
from core.use_cases.ProcessSingleQuestion import ProcessSingleQuestion


class InteractiveQA:
    """Interactive Q&A session handler."""
    
    def __init__(self):
        self.question_repo = CsvQuestionRepository()
        self.answer_service = SimpleAnswerService()
        self.parser = QuestionParser()
        self.processor = ProcessSingleQuestion(self.answer_service)
    
    def run(self) -> None:
        """Run interactive Q&A session."""
        print("🎯 Healthcare AI - Interactive Q&A")
        print("=" * 50)
        print("Enter Thai healthcare questions with multiple choices.")
        print("Type 'quit', 'exit', or 'q' to stop.")
        print("Type 'help' for format examples.")
        print()
        
        question_id = 1
        
        while True:
            try:
                print(f"Question {question_id}:")
                user_input = input("❓ ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                if not user_input:
                    continue
                
                # Parse and process question
                question = self.parser.parse_from_text(str(question_id), user_input)
                
                if not question.choices:
                    print("⚠️  No multiple choices detected. Please include ก. ข. ค. ง. options.")
                    continue
                
                # Get answer
                answer = self.processor.execute(question)
                
                print(f"💡 Answer: {answer.answer}")
                print(f"🎯 Confidence: {answer.confidence:.2f}")
                print()
                
                question_id += 1
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _show_help(self) -> None:
        """Show help information."""
        print("\n📋 Question Format Examples:")
        print("=" * 30)
        print("Single line format:")
        print("ผมปวดท้องมาก ตอนนี้ควรไปแผนกไหน? ก. Emergency ข. Internal Medicine ค. Surgery ง. Cardiology")
        print()
        print("Multi-line format:")
        print("ยาใช้รักษาโรคหัวใจมีราคาเท่าใด?")
        print("ก. 100 บาท")
        print("ข. 200 บาท")
        print("ค. 300 บาท")
        print("ง. 400 บาท")
        print("=" * 30)
        print()


def main():
    """Main entry point."""
    try:
        qa = InteractiveQA()
        qa.run()
    except Exception as e:
        print(f"❌ Error starting interactive session: {e}")


if __name__ == "__main__":
    main()