# Thai Healthcare Q&A System

ระบบตอบคำถามแบบหลายตัวเลือกเกี่ยวกับระบบหลักประกันสุขภาพแห่งชาติของไทย (ปี 2566)

## คุณสมบัติ

- ตอบคำถามแบบหลายตัวเลือกภาษาไทย
- ใช้ข้อมูลจากเอกสาร "direct_extraction_corrected.txt" 
- รองรับคำตอบที่ถูกต้องหลายข้อ
- แสดงเหตุผลสำหรับแต่ละตัวเลือก
- ใช้ Vector Database เพื่อค้นหาข้อมูลที่เกี่ยวข้อง

## การติดตั้ง

### 1. ติดตั้ง Ollama และโมเดล

```bash
# ติดตั้ง Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# ดาวน์โหลดโมเดลที่จำเป็น
ollama pull llama3.2
ollama pull mxbai-embed-large
```

### 2. ติดตั้ง Python dependencies

```bash
pip install langchain-ollama langchain-chroma langchain-core
```

### 3. ตรวจสอบไฟล์ข้อมูล

ตรวจสอบว่ามีไฟล์ต่อไปนี้อยู่:
- `results_doc/direct_extraction_corrected.txt`
- `results_doc2/direct_extraction_corrected.txt` 
- `results_doc3/direct_extraction_corrected.txt`

## การใช้งาน

### 1. ทดสอบระบบ

```bash
cd AI
python test_thai_qa.py
```

### 2. ใช้งานแบบ Interactive

```bash
cd AI
python thai_qa_processor.py
```

### 3. ใช้งานใน Python Code

```python
from thai_qa_processor import ThaiHealthcareQA

# สร้าง instance ของระบบ
qa_system = ThaiHealthcareQA()

# เตรียมคำถาม
question = """ผมปวดท้องมาก อ้วกด้วย ตอนนี้ตีสองยังมีแผนกไหนเปิดอยู่ไหมครับ?
ก. Endocrinology
ข. Orthopedics
ค. Emergency
ง. Internal Medicine"""

# ตอบคำถาม
answer = qa_system.answer_question(question)
print(answer)
```

## รูปแบบคำถาม

คำถามต้องมีรูปแบบดังนี้:

```
<คำถาม>
ก. <ตัวเลือกที่ 1>
ข. <ตัวเลือกที่ 2>
ค. <ตัวเลือกที่ 3>
ง. <ตัวเลือกที่ 4>
```

## รูปแบบคำตอบ

ระบบจะตอบเฉพาะตัวอักษรที่ถูกต้อง:

```
ก           (คำตอบเดียว)
ก, ค        (หลายคำตอบ)
ไม่มีคำตอบที่ถูกต้อง  (ไม่มีคำตอบใดถูก)
```

## ตัวอย่าง

### Input:
```
ผมปวดท้องมาก อ้วกด้วย ตอนนี้ตีสองยังมีแผนกไหนเปิดอยู่ไหมครับ?
ก. Endocrinology
ข. Orthopedics
ค. Emergency
ง. Internal Medicine
```

### Expected Output:
```
ค
```

## 📊 Batch Processing (ประมวลผล CSV)

ระบบสามารถประมวลผลคำถามจำนวนมากจากไฟล์ CSV ได้:

### 1. ประมวลผลไฟล์ test.csv ทั้งหมด (500 คำถาม)

```bash
cd AI
python batch_test_processor.py
```

หรือกำหนดไฟล์และขนาด batch:

```bash
python batch_test_processor.py test.csv results.csv 10
```

### 2. ทดสอบด่วนกับ 5 คำถามแรก

```bash
python quick_batch_test.py
```

### 3. ใช้งานใน Python Script

```python
from thai_qa_processor import ThaiHealthcareQA

# เริ่มต้นระบบ
qa_system = ThaiHealthcareQA()

# ประมวลผลทั้งไฟล์
qa_system.process_csv_questions("test.csv", "answers.csv")

# หรือประมวลผลแบบ batch (แนะนำสำหรับไฟล์ใหญ่)
qa_system.process_csv_batch("test.csv", batch_size=10, output_file_path="answers.csv")
```

### รูปแบบไฟล์ CSV Input

```csv
id,question,answer
1,ผมปวดท้องมาก อ้วกด้วย ตอนนี้ตีสองยังมีแผนกไหนเปิดอยู่ไหมครับ? ก. Endocrinology ข. Orthopedics ค. Emergency ง. Internal Medicine,
2,ยา Clopidogrel mg tablet ในปี 2567 จ่ายในอัตราเท่าใดต่อเม็ด? ก. 2 บาท/เม็ด ข. 3 บาท/เม็ด ค. 4 บาท/เม็ด ง. 5 บาท/เม็ด,
```

### รูปแบบไฟล์ CSV Output

```csv
id,question,answer
1,ผมปวดท้องมาก อ้วกด้วย ตอนนี้ตีสองยังมีแผนกไหนเปิดอยู่ไหมครับ? ก. Endocrinology ข. Orthopedics ค. Emergency ง. Internal Medicine,ค
2,ยา Clopidogrel mg tablet ในปี 2567 จ่ายในอัตราเท่าใดต่อเม็ด? ก. 2 บาท/เม็ด ข. 3 บาท/เม็ด ค. 4 บาท/เม็ด ง. 5 บาท/เม็ด,ข
```

### คุณสมบัติ Batch Processing

- ✅ **ประมวลผลอัตโนมัติ**: อ่าน CSV และประมวลผลทุกคำถาม
- ✅ **ตอบเฉพาะตัวอักษร**: เอาต์พุตเฉพาะ ก, ข, ค, ง 
- ✅ **สถิติการทำงาน**: แสดงจำนวนข้อที่สำเร็จและผิดพลาด
- ✅ **Batch Processing**: แบ่งเป็นกลุ่มย่อยเพื่อประสิทธิภาพ
- ✅ **Error Handling**: จัดการข้อผิดพลาดและบันทึกสถานะ

## การแก้ไขปัญหา

### 1. ข้อผิดพลาด "Ollama not running"
```bash
# เริ่ม Ollama service
ollama serve
```

### 2. ข้อผิดพลาด "Model not found"
```bash
# ตรวจสอบโมเดลที่ติดตั้งแล้ว
ollama list

# ติดตั้งโมเดลที่จำเป็น
ollama pull llama3.2
ollama pull mxbai-embed-large
```

### 3. Vector Database ล้มเหลว
- ลบโฟลเดอร์ `thai_healthcare_db` และรันใหม่
- ตรวจสอบว่าไฟล์ `.txt` มีข้อมูลและ encoding ถูกต้อง

### 4. คำตอบไม่ถูกต้อง
- ตรวจสอบว่าคำถามมีรูปแบบถูกต้อง
- ตรวจสอบว่าข้อมูลในไฟล์ต้นฉบับมีคำตอบ
- เพิ่มข้อมูลเพิ่มเติมในไฟล์ต้นฉบับ

## โครงสร้างไฟล์

```
AI/
├── thai_qa_processor.py      # ระบบหลัก
├── test_thai_qa.py          # สคริปต์ทดสอบ
├── README_THAI_QA.md        # เอกสารนี้
├── thai_healthcare_db/      # Vector database (สร้างอัตโนมัติ)
└── main.py                  # ระบบเก่า (pizza Q&A)
```

## ข้อจำกัด

- ต้องใช้ Ollama และโมเดลที่ระบุ
- ข้อมูลจำกัดอยู่ในไฟล์ที่ให้มา
- ความแม่นยำขึ้นกับคุณภาพของข้อมูลต้นฉบับ
- การตอบภาษาไทยอาจไม่สมบูรณ์ 100%

## การพัฒนาต่อ

- เพิ่มข้อมูลจากแหล่งอื่น
- ปรับปรung prompt สำหรับความแม่นยำมากขึ้น
- เพิ่มการจัดการ edge cases
- สร้าง web interface
- เพิ่มการ logging และ monitoring