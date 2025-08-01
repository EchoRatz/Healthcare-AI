#!/usr/bin/env python3
"""
Quick test for batch processing with just the first 5 questions
"""

from thai_qa_processor import ThaiHealthcareQA
import csv
import os


def create_small_test_csv():
    """Create a small test CSV with first 5 questions"""

    # Read first 5 questions from test.csv
    with open("test.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        questions = list(reader)[:5]  # First 5 questions only

    # Write to small test file
    with open("quick_test.csv", "w", encoding="utf-8", newline="") as file:
        fieldnames = ["id", "question", "answer"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(questions)

    return "quick_test.csv"


def main():
    """Test batch processing with 5 questions"""

    print("🧪 Quick Batch Test - Thai Healthcare Q&A")
    print("=" * 60)
    print("จะทดสอบกับ 5 คำถามแรกจาก test.csv")
    print()

    try:
        # Create small test file
        print("📝 สร้างไฟล์ทดสอบ...")
        test_csv = create_small_test_csv()
        print(f"✅ สร้างไฟล์: {test_csv}")

        # Initialize Q&A system
        print("🚀 กำลังเริ่มต้นระบบ...")
        qa_system = ThaiHealthcareQA()
        print("✅ ระบบพร้อม!")

        # Process questions
        print("\n🔄 เริ่มประมวลผล...")
        qa_system.process_csv_questions(test_csv, "quick_test_answers.csv")

        qa_system.show_cache_stats()

        # Display results
        print("\n📊 ผลลัพธ์:")
        if os.path.exists("quick_test_answers.csv"):
            with open("quick_test_answers.csv", "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    print(f"Q{row['id']}: {row['answer']}")

        # Clean up test files
        if os.path.exists(test_csv):
            os.remove(test_csv)

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {str(e)}")
        print("💡 ตรวจสอบ:")
        print("   - Ollama รันอยู่หรือไม่")
        print("   - Models ติดตั้งแล้วหรือไม่")
        print("   - ไฟล์ test.csv มีอยู่หรือไม่")


if __name__ == "__main__":
    main()
