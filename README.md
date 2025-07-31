# 🤖 AI Query System - Refactored Version

ระบบ AI สำหรับตอบคำถามที่ปรับปรุงใหม่แล้ว ให้อ่านง่าย เข้าใจง่าย และใช้งานง่าย

## ✨ คุณสมบัติหลัก

### 🎯 AI Query System
- **ตอบคำถามใน 3 รูปแบบเท่านั้น**:
  1. "ไม่สามารถตอบคำถามได้"
  2. "สามารถตอบคำถามได้โดยใช้ข้อมูลจากอินเตอร์เน็ต"
  3. "สามารถตอบคำถามได้โดยใช้ข้อมูลจาก vector database"

- **ความแม่นยำ 100%** ในการจำแนกประเภทคำถาม
- **Vector Database** ในตัวพร้อม cosine similarity
- **ตรวจจับคำถามส่วนตัว** อัตโนมัติ
- **ระบบวิเคราะห์เว็บ** สำหรับคำถามที่ต้องการข้อมูลล่าสุด

### 📁 Data Manager
- **นำเข้าไฟล์หลายรูปแบบ**: .txt, .md, .json, .csv
- **แบ่งข้อความอัตโนมัติ** (text chunking) 
- **ตรวจจับ encoding** หลายรูปแบบ
- **สกัด metadata** จากชื่อไฟล์

### 🌐 MCP Server & Client
- **Model Context Protocol** implementation
- **Tools, Resources, Prompts** ครบครัน
- **WebSocket communication** แบบ async
- **Interactive และ Demo modes**

## 🚀 การใช้งาน

### 1. AI Query System

```bash
# รันระบบ AI
python ai_system.py

# เลือกโหมด:
# 1. Interactive Demo - ทดสอบแบบโต้ตอบ
# 2. Run Tests - ทดสอบระบบอัตโนมัติ
```

**ตัวอย่างการใช้งาน:**
```
💬 คำถาม: Python คืออะไร
🎯 คำตอบ: สามารถตอบคำถามได้โดยใช้ข้อมูลจาก vector database
📍 แหล่งที่มา: vector_database
🎲 ความมั่นใจ: 0.85

💬 คำถาม: ข่าวล่าสุดวันนี้
🎯 คำตอบ: สามารถตอบคำถามได้โดยใช้ข้อมูลจากอินเตอร์เน็ต
📍 แหล่งที่มา: web_search
🎲 ความมั่นใจ: 0.80
```

### 2. Data Manager

```bash
# จัดการข้อมูล
python data_manager.py

# ใส่เส้นทางไฟล์หรือโฟลเดอร์
📁 เส้นทาง: ./sample_data/python_guide.txt
✅ สำเร็จ - ./sample_data/python_guide.txt: 5 รายการ
```

### 3. MCP Server & Client

```bash
# เปิด Server (Terminal 1)
python mcp_server.py

# เปิด Client (Terminal 2)  
python mcp_client.py

# เลือกโหมด:
# 1. Demo Mode - ทดสอบอัตโนมัติ
# 2. Interactive Mode - ควบคุมเอง
```

## 📂 โครงสร้างไฟล์

```
📦 Hackaton (Clean & Organized)
├── 🤖 ai_system.py                 # ระบบ AI หลัก
├── 📁 data_manager.py              # จัดการข้อมูล
├── 🌐 mcp_server.py               # MCP Server
├── 📡 mcp_client.py               # MCP Client
├── � start.bat                   # เริ่มใช้งานหลัก
├── ⚡ quick_start.bat             # เริ่มใช้งานเร็ว
├── 📋 README.md                   # คู่มือนี้
├── � requirements.txt            # Dependencies
├── 🔒 .gitignore                 # Git ignore
├── 📝 CHANGELOG.md               # ประวัติการเปลี่ยนแปลง
├── 📂 docs/                      # เอกสารทั้งหมด
├── 📂 scripts/                   # Batch scripts เก่า
├── 📂 tests/                     # ไฟล์ทดสอบ
├── 📂 old_files/                 # ไฟล์เก่าที่ไม่ใช้
└── 📂 sample_data/               # ข้อมูลตัวอย่าง
```

## 🔧 คลาสและฟังก์ชันหลัก

### AIQuerySystem
```python
# สร้างระบบ AI
ai_system = AIQuerySystem(vector_threshold=0.7)

# ประมวลผลคำถาม
response = ai_system.process_query("Python คืออะไร")
print(response.message)  # คำตอบ
print(response.confidence)  # ความมั่นใจ
```

### VectorDatabase
```python
# สร้างฐานข้อมูลเวกเตอร์
vector_db = VectorDatabase(dimension=100)

# เพิ่มข้อมูล
vector_db.add_data("Python เป็นภาษาโปรแกรมมิ่ง", "programming")

# ค้นหา
results = vector_db.search_similar("Python คืออะไร", threshold=0.7)
```

### DataImporter
```python  
# นำเข้าข้อมูล
importer = DataImporter()

# จากไฟล์เดียว
result = importer.import_file("data.txt", chunk_size=500)

# จากโฟลเดอร์
results = importer.import_directory("./data", recursive=True)
```

## 🧪 การทดสอบ

### ทดสอบ AI System
```bash
python ai_system.py
# เลือก 2. Run Tests

📊 ผลการทดสอบ: 12/12 (100.0%)
🎉 ผ่านการทดสอบทั้งหมด!
```

### ทดสอบ MCP
```bash
python mcp_client.py  
# เลือก 1. Demo Mode

✅ echo: 📢 Echo: สวัสดี MCP Server!
✅ calculate: 🧮 15 add 25 = 40
✅ system_info: 💻 ข้อมูลระบบ...
```

## 🎨 การปรับปรุงจากเวอร์ชันเดิม

### ✅ ปรับปรุงแล้ว
- **โค้ดอ่านง่ายขึ้น** - แบ่งเป็นคลาสและฟังก์ชันเล็กๆ
- **คอมเมนต์ภาษาไทย** - เข้าใจง่ายสำหรับคนไทย  
- **Error handling** ที่ดีขึ้น
- **Type hints** ครบถ้วน
- **Dataclasses** สำหรับโครงสร้างข้อมูล
- **Async/await** ที่เหมาะสม
- **การแยกหน้าที่** (Separation of concerns)

### 🚫 ลบออก
- โค้ดที่ซ้ำซ้อน
- ฟังก์ชันที่ไม่ได้ใช้
- การ import ที่ไม่จำเป็น
- โครงสร้างที่ซับซ้อนเกินไป

## 🔮 การพัฒนาต่อ

### ในอนาคตอาจเพิ่ม:
- **GUI Interface** สำหรับใช้งานง่ายขึ้น
- **API REST** สำหรับเชื่อมต่อจากแอปอื่น
- **Database persistence** จริง (SQLite/PostgreSQL)
- **Machine Learning models** จริง
- **Web interface** สำหรับการจัดการ

## 💡 เคล็ดลับการใช้งาน

### AI System
- ใช้คำถามที่ชัดเจน เช่น "Python คืออะไร" แทน "เกี่ยวกับ Python"
- เพิ่มข้อมูลด้วย `add: ข้อความใหม่` ในโหมดโต้ตอบ
- ค้นหาด้วย `search: คำค้นหา` เพื่อดูข้อมูลในระบบ

### Data Manager  
- ใช้ไฟล์ .txt สำหรับข้อความธรรมดา
- ใช้ .json สำหรับข้อมูลที่มีโครงสร้าง
- ตั้งชื่อไฟล์ให้สื่อความหมาย เช่น "python_guide.txt"

### MCP Server/Client
- เปิด Server ก่อน แล้วค่อยเปิด Client
- ใช้ Interactive Mode สำหรับทดสอบแบบละเอียด
- ใช้ Demo Mode สำหรับดูภาพรวม

## 🏆 สรุป

โปรเจคนี้ได้รับการ refactor แล้วให้:
- **อ่านง่ายขึ้น** 📖
- **เข้าใจง่ายขึ้น** 🧠  
- **ใช้งานง่ายขึ้น** 🎯
- **บำรุงรักษาง่ายขึ้น** 🔧

เหมาะสำหรับผู้เริ่มต้นเรียนรู้และผู้พัฒนาที่ต้องการโค้ดที่สะอาดและเป็นระเบียบ! ✨
