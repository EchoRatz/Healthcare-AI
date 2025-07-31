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