"""Quick test entry point."""
import sys
import os
import csv
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from infrastructure.repositories.CsvQuestionRepository import CsvQuestionRepository
from infrastructure.services.SimpleAnswerService import SimpleAnswerService
from core.use_cases.ProcessCsvBatch import ProcessCsvBatch


def create_sample_csv() -> str:
    """Create sample CSV file for testing."""
    sample_questions = [
        {
            'id': '1', 
            'question': 'ผมปวดท้องมาก อ้วกด้วย ตอนนี้ตีสองยังมีแผนกไหนเปิดอยู่ไหมครับ?  ก. Endocrinology ข. Orthopedics ค. Emergency ง. Internal Medicine',
            'answer': ''
        },
        {
            'id': '2', 
            'question': 'ยา Clopidogrel mg tablet ในปี 2567 จ่ายในอัตราเท่าใดต่อเม็ดในกรณีผู้ป่วยนอก (OP)?  ก. 2 บาท/เม็ด ข. 3 บาท/เม็ด ค. 4 บาท/เม็ด ง. 5 บาท/เม็ด',
            'answer': ''
        },
        {
            'id': '3', 
            'question': 'ข้อใดต่อไปนี้เป็นอาการฉุกเฉินวิกฤตที่เข้าข่ายสิทธิ UCEP?  ก. เจ็บหน้าอกเฉียบพลันรุนแรง ข. ปวดหัวอย่างรุนแรง ค. มีไข้สูง ง. ปวดท้องเรื้อรัง',
            'answer': ''
        },
        {
            'id': '4', 
            'question': 'สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ?  ก. สิทธิหลักประกันสุขภาพแห่งชาติ ข. สิทธิบัตรทอง ค. สิทธิ 30 บาทรักษาทุกโรค ง. ไม่มีข้อใดถูกต้อง',
            'answer': ''
        },
        {
            'id': '5', 
            'question': 'ค่าบริการเคลือบฟลูออไรด์ชนิดเข้มข้นสูงเฉพาะที่มีอัตราเหมาจ่ายเท่าใดต่อครั้ง?  ก. 50 บาท ข. 75 บาท ค. 100 บาท ง. 150 บาท',
            'answer': ''
        }
    ]
    
    filename = "quick_test_sample.csv"
    with open(filename, 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'question', 'answer'])
        writer.writeheader()
        writer.writerows(sample_questions)
    
    return filename


def main():
    """Quick test with sample questions."""
    print("🧪 Quick Test - Processing 5 sample questions")
    print("=" * 50)
    
    try:
        # Create sample CSV
        print("📝 Creating sample questions...")
        sample_file = create_sample_csv()
        print(f"✅ Created: {sample_file}")
        
        # Initialize components
        question_repo = CsvQuestionRepository()
        answer_service = SimpleAnswerService()
        batch_processor = ProcessCsvBatch(question_repo, answer_service)
        
        # Process questions
        result = batch_processor.execute(sample_file, "quick_test_answers.csv", batch_size=5)
        
        # Show results
        print("\n📊 Results:")
        for i, res in enumerate(result.results[:5]):
            print(f"   Q{res['id']}: {res['answer']}")
        
        stats = result.stats
        print(f"✅ Success rate: {stats.success_rate:.1f}%")
        print(f"⏱️  Duration: {stats.duration:.2f} seconds")
        
        # Cleanup
        if os.path.exists(sample_file):
            os.remove(sample_file)
        
        print(f"\n💾 Full results saved to: {result.output_file}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -e .")


if __name__ == "__main__":
    main()