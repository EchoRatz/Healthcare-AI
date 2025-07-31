# 🏥 Healthcare-AI PDF Content Extractor

> **Advanced PDF content extraction with Thai language support and AI-powered grammar correction**

Extract, process, and improve Thai healthcare documents using cutting-edge AI technology.

## ✨ Features

- **📄 Multi-Method PDF Extraction**
  - Direct text extraction (PyMuPDF)
  - NVIDIA NIM API (advanced OCR + layout analysis)
  - Multi-page document support

- **🇹🇭 Thai Language Optimized**
  - Native Thai text extraction
  - Unicode UTF-8 encoding
  - Preserves Thai formatting and structure

- **🤖 AI-Powered Grammar Correction**
  - Typhoon.ai integration (Thai-first LLM)
  - Grammar and spelling correction
  - Smart text chunking for large documents

- **🚀 Flexible Processing Options**
  - Extract only, correct only, or both
  - Multiple output formats (TXT, JSON)
  - Command-line interface

## 🚀 Quick Start

### 1. Basic PDF Extraction
```bash
# Extract text from PDF (no API keys required)
python PDF_Extractor.py doc.pdf results direct
```

### 2. Advanced Processing with NVIDIA API
```bash
# Set your NVIDIA API key
export API_KEY="your_nvidia_api_key"

# Extract with advanced OCR
python PDF_Extractor.py doc.pdf results nvidia 1
```

### 3. Thai Grammar Correction
```bash
# Set your Typhoon.ai API key
export TYPHOON_API_KEY="your_typhoon_api_key"

# Extract + grammar correction
python PDF_Extractor.py doc.pdf results direct --correct-grammar
```

## 📦 Installation

### Requirements
- Python 3.8+
- Virtual environment (recommended)

### Setup
```bash
# Clone repository
git clone https://github.com/your-username/Healthcare-AI.git
cd Healthcare-AI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Dependencies
- `PyMuPDF` (fitz) - PDF text extraction
- `pdf2image` - PDF to image conversion  
- `Pillow` - Image processing
- `requests` - API communication

## 📚 Documentation

- **[Quick Usage Guide](QUICK_USAGE.md)** - Get started in 5 minutes
- **[Typhoon.ai Setup](TYPHOON_SETUP_GUIDE.md)** - Thai grammar correction setup
- **[Complete Usage Guide](USAGE_GUIDE.md)** - Detailed documentation

## 🎯 Use Cases

### Healthcare Document Processing
- **Patient Records**: Extract and improve Thai medical records
- **Research Papers**: Process Thai healthcare research documents
- **Policy Documents**: Extract content from healthcare policy PDFs
- **Insurance Claims**: Process Thai insurance documents

### Text Quality Improvement  
- **Grammar Correction**: Fix Thai spelling and grammar errors
- **Standardization**: Consistent terminology across documents
- **Readability**: Improve document clarity and professionalism

## 📊 Examples

### Input (Original Thai Text):
```
คูรือสดทธิหลักประกันสุขภาพแหรงชาติ ปรงบประมาณ 2566
ตามที ส๚านักบรุการประชาชน มีภารกิจหลัก
```

### Output (Grammar Corrected):
```
คู่มือสิทธิหลักประกันสุขภาพแห่งชาติ ปีงบประมาณ 2566
ตามที่ สำนักบริการประชาชน มีภารกิจหลัก
```

## 🛠️ Command Options

```bash
python PDF_Extractor.py <file> <output_dir> [options]

Methods:
  direct        - Direct text extraction (offline)
  nvidia        - NVIDIA API processing
  both          - Both methods
  grammar-only  - Grammar correction only

Options:
  --correct-grammar     - Apply Thai grammar correction
  --typhoon-key KEY    - Typhoon.ai API key
  
Task IDs (NVIDIA API):
  0 - markdown_bbox     - With bounding boxes
  1 - markdown_no_bbox  - Clean markdown
  2 - detection_only    - Element detection
```

## 🔑 API Keys

### Free Tier Options Available:

1. **Typhoon.ai** (Thai grammar correction)
   - Get key: https://docs.opentyphoon.ai/
   - Free tier: 200 requests/month

2. **NVIDIA NIM** (Advanced OCR)
   - Get key: https://build.nvidia.com/
   - Free tier available

## 📁 Project Structure

```
Healthcare-AI/
├── PDF_Extractor.py          # Main extraction script
├── test_typhoon_grammar.py   # Grammar correction test
├── requirements.txt          # Python dependencies
├── QUICK_USAGE.md           # Quick start guide
├── TYPHOON_SETUP_GUIDE.md   # Typhoon.ai setup
├── USAGE_GUIDE.md           # Complete documentation
├── doc.pdf                  # Sample Thai healthcare PDF
├── doc2.pdf                 # Sample document 2
├── doc3.pdf                 # Sample document 3
└── results/                 # Output directory
    ├── direct_extraction.txt
    ├── direct_extraction_corrected.txt
    └── combined_results.json
```

## 🧪 Testing

```bash
# Test grammar correction setup
python test_typhoon_grammar.py

# Test with sample documents
python PDF_Extractor.py doc.pdf test_results direct --correct-grammar
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Create a GitHub issue
- **Documentation**: Check the guides in this repository
- **API Support**: Contact respective API providers

## 🎉 Acknowledgments

- **Typhoon.ai** - Thai language AI models
- **NVIDIA** - Advanced OCR capabilities  
- **PyMuPDF** - PDF processing library
- **Healthcare Community** - Inspiration and use case validation

---

**Transform your Thai healthcare documents with AI-powered extraction and correction!** 🚀
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
