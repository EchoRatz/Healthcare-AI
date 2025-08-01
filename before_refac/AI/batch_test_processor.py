#!/usr/bin/env python3
"""
Batch processor for test.csv questions
Processes all Thai healthcare questions and outputs only choice letters (ก, ข, ค, ง)
"""

from thai_qa_processor import ThaiHealthcareQA
import sys
import os
import csv


def validate_csv_format(csv_file_path):
    """Validate that the CSV file has the correct format"""
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Check if required columns exist
            if 'id' not in reader.fieldnames or 'question' not in reader.fieldnames:
                return False, "CSV must have 'id' and 'question' columns"
            
            # Check first few rows
            row_count = 0
            for row in reader:
                if not row['id'] or not row['question']:
                    return False, f"Empty id or question in row {row_count + 1}"
                row_count += 1
                if row_count >= 3:  # Check first 3 rows
                    break
            
            return True, f"Valid CSV with {row_count}+ questions"
            
    except Exception as e:
        return False, f"Error reading CSV: {str(e)}"


def preview_csv(csv_file_path, num_rows=3):
    """Preview first few rows of CSV"""
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            print(f"📋 Preview of {csv_file_path}:")
            print("-" * 80)
            
            for i, row in enumerate(reader):
                if i >= num_rows:
                    break
                    
                question_preview = row['question'][:100] + "..." if len(row['question']) > 100 else row['question']
                print(f"ID {row['id']}: {question_preview}")
                
            print("-" * 80)
            
    except Exception as e:
        print(f"❌ Error previewing CSV: {e}")


def show_usage():
    """Show usage information"""
    print("\n💡 วิธีใช้:")
    print("   python batch_test_processor.py [input.csv] [output.csv] [batch_size] [flags]")
    print("\n📁 ตัวอย่าง:")
    print("   python batch_test_processor.py                    # ใช้ค่าเริ่มต้น")
    print("   python batch_test_processor.py test.csv          # กำหนดไฟล์ input")
    print("   python batch_test_processor.py test.csv results.csv  # กำหนดไฟล์ input และ output")
    print("   python batch_test_processor.py test.csv results.csv 10  # กำหนด batch size")
    print("   python batch_test_processor.py test.csv results.csv 10 --auto  # โหมดอัตโนมัติ")
    print("\n🏷️  Flags:")
    print("   --auto, -y    : ไม่ถามยืนยัน เริ่มประมวลผลทันที")
    print("   --sample      : ประมวลผลคำถามตัวอย่าง")
    print("   --help, -h    : แสดงความช่วยเหลือ")
    print("\n📋 รูปแบบ CSV ที่ต้องการ:")
    print("   id,question,answer")
    print("   1,คำถาม? ก. ตัวเลือก1 ข. ตัวเลือก2 ค. ตัวเลือก3 ง. ตัวเลือก4,")


def show_help():
    """Show detailed help information"""
    print("🎯 Thai Healthcare Q&A Batch Processor")
    print("=" * 60)
    print("ประมวลผลคำถามสุขภาพภาษาไทยจำนวนมากจากไฟล์ CSV")
    print("ตอบเฉพาะตัวอักษร ก, ข, ค, ง ตามที่ระบบ AI วิเคราะห์")
    show_usage()
    print("\n🔧 ข้อกำหนดระบบ:")
    print("   - Ollama ต้องรันอยู่")
    print("   - Models: llama3.2, mxbai-embed-large")
    print("   - Python packages: langchain-ollama, langchain-chroma, langchain-core")
    print("\n📊 คุณสมบัติ:")
    print("   ✅ ตรวจสอบรูปแบบ CSV อัตโนมัติ")
    print("   ✅ แสดงตัวอย่างคำถามก่อนประมวลผล")
    print("   ✅ ประมวลผลแบบ batch เพื่อประสิทธิภาพ")
    print("   ✅ แสดงสถิติและผลลัพธ์")
    print("   ✅ จัดการข้อผิดพลาดอัตโนมัติ")


def main():
    """Main function to process test.csv in batch mode"""
    
    # Default paths - look for test.csv in current directory or parent directory
    possible_paths = ["test.csv", "../test.csv", "AI/test.csv"]
    input_csv = None
    
    # Find test.csv file
    for path in possible_paths:
        if os.path.exists(path):
            input_csv = path
            break
    
    if input_csv is None:
        input_csv = "test.csv"  # Default fallback
    
    output_csv = "test_answers.csv"
    batch_size = 5  # Smaller batch size for better monitoring
    
    # Check if custom paths provided
    if len(sys.argv) > 1:
        input_csv = sys.argv[1]
    if len(sys.argv) > 2:  
        output_csv = sys.argv[2]
    if len(sys.argv) > 3:
        batch_size = int(sys.argv[3])
    
    # Check if input file exists
    if not os.path.exists(input_csv):
        print(f"❌ ไม่พบไฟล์: {input_csv}")
        print(f"🔍 กำลังมองหาไฟล์ในตำแหน่ง: {os.path.abspath(input_csv)}")
        show_usage()
        return
    
    print("🎯 Thai Healthcare Q&A Batch Processor")
    print("=" * 60)
    print(f"📝 Input file: {input_csv}")
    print(f"💾 Output file: {output_csv}")
    print(f"📦 Batch size: {batch_size}")
    print("=" * 60)
    
    # Validate CSV format
    print("🔍 กำลังตรวจสอบรูปแบบ CSV...")
    is_valid, message = validate_csv_format(input_csv)
    
    if not is_valid:
        print(f"❌ {message}")
        print("\n📋 รูปแบบ CSV ที่ถูกต้อง:")
        print("id,question,answer")
        print("1,คำถาม? ก. ตัวเลือก1 ข. ตัวเลือก2 ค. ตัวเลือก3 ง. ตัวเลือก4,")
        return
    
    print(f"✅ {message}")
    
    # Preview CSV content
    preview_csv(input_csv)
    
    # Count total questions
    try:
        with open(input_csv, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            total_questions = sum(1 for row in reader)
        print(f"📊 จำนวนคำถามทั้งหมด: {total_questions} ข้อ")
    except Exception as e:
        print(f"⚠️  ไม่สามารถนับจำนวนคำถามได้: {e}")
        total_questions = "ไม่ทราบ"
    
    print("=" * 60)
    
    # Confirm before processing (unless --auto flag is used)
    auto_mode = '--auto' in sys.argv or '-y' in sys.argv
    
    if not auto_mode:
        response = input("🤔 ต้องการเริ่มประมวลผลหรือไม่? (y/n): ").lower().strip()
        if response not in ['y', 'yes', 'ใช่']:
            print("❌ ยกเลิกการประมวลผล")
            return
    else:
        print("🤖 โหมดอัตโนมัติ - เริ่มประมวลผลทันที")
    
    print("=" * 60)
    
    try:
        # Initialize the Q&A system
        print("🚀 กำลังเริ่มต้นระบบ...")
        qa_system = ThaiHealthcareQA()
        print("✅ ระบบพร้อมใช้งาน!")
        print()
        
        # Process the CSV file
        if batch_size > 1:
            qa_system.process_csv_batch(input_csv, batch_size, output_csv)
        else:
            qa_system.process_csv_questions(input_csv, output_csv)
        
        # Show completion summary
        print("\n" + "=" * 60)
        print("🎉 การประมวลผลเสร็จสิ้น!")
        
        # Show output file info
        if os.path.exists(output_csv):
            file_size = os.path.getsize(output_csv)
            print(f"📁 ไฟล์ผลลัพธ์: {output_csv}")
            print(f"📊 ขนาดไฟล์: {file_size:,} bytes")
            
            # Preview results
            print("\n📋 ตัวอย่างผลลัพธ์:")
            try:
                with open(output_csv, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for i, row in enumerate(reader):
                        if i >= 5:  # Show first 5 results
                            break
                        print(f"   Q{row['id']}: {row['answer']}")
                print("   ...")
            except Exception as e:
                print(f"   ไม่สามารถแสดงตัวอย่างได้: {e}")
        
        print("=" * 60)
            
    except KeyboardInterrupt:
        print("\n⚠️  การประมวลผลถูกยกเลิกโดยผู้ใช้")
        print("📁 ผลลัพธ์บางส่วนอาจถูกบันทึกแล้ว")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {str(e)}")
        print("💡 แนะนำ:")
        print("   - ตรวจสอบว่า Ollama กำลังรันอยู่")
        print("   - ตรวจสอบว่าได้ติดตั้ง models แล้ว: llama3.2, mxbai-embed-large")
        print("   - ตรวจสอบรูปแบบของไฟล์ CSV")


def process_sample_questions():
    """Process just a few sample questions for testing"""
    
    sample_csv = "sample_test.csv"
    
    # Create a small sample CSV for testing
    import csv
    
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
        }
    ]
    
    # Write sample CSV
    with open(sample_csv, 'w', encoding='utf-8', newline='') as file:
        fieldnames = ['id', 'question', 'answer']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sample_questions)
    
    print("🧪 ประมวลผลคำถามตัวอย่าง")
    print("=" * 60)
    
    try:
        qa_system = ThaiHealthcareQA()
        qa_system.process_csv_questions(sample_csv, "sample_answers.csv")
        
        # Clean up
        os.remove(sample_csv)
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {str(e)}")


if __name__ == "__main__":
    # Check for help flags
    if '--help' in sys.argv or '-h' in sys.argv:
        show_help()
    elif '--sample' in sys.argv:
        process_sample_questions()
    else:
        main()