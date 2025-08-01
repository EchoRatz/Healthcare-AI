# Healthcare Q&A System

ระบบ AI สำหรับตอบคำถามด้านสุขภาพที่ใช้ Ollama model และเชื่อมต่อกับ MCP server ของ CMKL

## 🏗️ System Configuration

### Data Sources
- **MCP Server**: `https://mcp-hackathon.cmkl.ai/mcp`
- **Text Files**: จากโฟลเดอร์ `results_doc`, `results_doc2`, `results_doc3`
- **Input**: `src/infrastructure/test.csv`
- **Expected Output**: `test_sample_output.csv`

### Model Configuration
- **Model**: `llama2:13b` (เร็วและประหยัดทรัพยากร)
- **Provider**: Ollama
- **Base URL**: `http://localhost:11434`

## 🚀 Quick Start

### Step 1: Install Dependencies
```bash
cd Healthcare-AI-Refactored
pip install -r requirements_enhanced.txt
```

### Step 2: Install Ollama Model
```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the 13B model (เร็วกว่า 70B)
ollama pull llama2:13b
```

### Step 3: Test the System
```bash
# Test basic functionality
python test_system.py

# Run the demo
python src/scripts/enhanced_system_demo.py
```

### Step 4: Process Healthcare Q&A Dataset
```bash
# Process all questions
python src/scripts/process_healthcare_qa.py

# Process only first 10 questions (for testing)
python src/scripts/process_healthcare_qa.py --max-questions 10

# Process with custom batch size
python src/scripts/process_healthcare_qa.py --batch-size 3
```

## 📊 Expected Output Format

### Input (`test.csv`)
```csv
id,question,answer
1,ผมปวดท้องมาก อ้วกด้วย ตอนนี้ตีสองยังมีแผนกไหนเปิดอยู่ไหมครับ?  ก. Endocrinology ข. Orthopedics ค. Emergency ง. Internal Medicine ,
2,ยา Clopidogrel mg tablet ในปี 2567 จ่ายในอัตราเท่าใดต่อเม็ดในกรณีผู้ป่วยนอก (OP)?  ก. 2 บาท/เม็ด ข. 3 บาท/เม็ด ค. 4 บาท/เม็ด ง. 5 บาท/เม็ด ,
```

### Output (`test_output.csv`)
```csv
id,answer
1,ค
2,ข
3,ก,ค
4,ค
5,ข,ง
```

## 🔧 Configuration Details

### Enhanced System Config (`config/enhanced_system.json`)
```json
{
  "llm": {
    "model_name": "llama2:13b",
    "base_url": "http://localhost:11434"
  },
  "connectors": {
    "mcp": {
      "enabled": true,
      "server_url": "https://mcp-hackathon.cmkl.ai/mcp"
    },
    "text": {
      "enabled": true,
      "base_path": "src/infrastructure",
      "text_folders": ["results_doc", "results_doc2", "results_doc3"]
    }
  }
}
```

## 📁 File Structure

```
Healthcare-AI-Refactored/
├── config/
│   └── enhanced_system.json          # System configuration
├── src/
│   ├── infrastructure/
│   │   ├── results_doc/              # Text files folder 1
│   │   │   └── direct_extraction_corrected.txt
│   │   ├── results_doc2/             # Text files folder 2
│   │   │   └── direct_extraction_corrected.txt
│   │   ├── results_doc3/             # Text files folder 3
│   │   │   └── direct_extraction_corrected.txt
│   │   └── test.csv                  # Input questions
│   └── scripts/
│       └── process_healthcare_qa.py  # Processing script
├── test_system.py                    # System test script
└── test_sample_output.csv            # Expected output format
```

## 🧪 Testing

### Test Individual Components
```bash
# Test text connector
python -c "
from src.infrastructure.connectors.TextConnector import TextConnector
connector = TextConnector('src/infrastructure', ['results_doc', 'results_doc2', 'results_doc3'])
print('Available files:', connector.list_available_files())
"

# Test MCP connector
python -c "
from src.infrastructure.connectors.MCPConnector import MCPConnector
connector = MCPConnector('https://mcp-hackathon.cmkl.ai/mcp')
print('Available:', connector.is_available())
"
```

### Test Full System
```bash
# Run comprehensive test
python test_system.py

# Test with specific query
python -c "
from src.infrastructure.factories.EnhancedSystemFactory import EnhancedSystemFactory
factory = EnhancedSystemFactory()
engine = factory.create_chain_of_thought_engine()
result = engine.process_query('แผนกไหนที่ให้บริการโรคหัวใจ?')
print('Answer:', result.get('answer'))
"
```

## 📈 Performance

### Expected Processing Times
- **Planning Phase**: 100-300ms
- **Data Retrieval**: 0.5-2.0s
- **Reasoning Phase**: 1-5s
- **Total Response**: 2-8 seconds per question

### Resource Requirements
- **GPU**: 8GB+ VRAM (สำหรับ llama2:13b)
- **RAM**: 16GB+ system RAM
- **Storage**: 5GB+ สำหรับ model และ documents

## 🔍 Troubleshooting

### Common Issues

1. **Model not found**
   ```bash
   # Check available models
   ollama list
   
   # Pull the model
   ollama pull llama2:13b
   ```

2. **MCP connection failed**
   ```bash
   # Test MCP server
   curl https://mcp-hackathon.cmkl.ai/mcp
   ```

3. **Text files not found**
   ```bash
   # Check file structure
   ls -la src/infrastructure/results_doc*/
   ```

4. **Memory issues**
   ```bash
   # Use smaller model
   ollama pull llama2:7b
   
   # Update config
   # Change model_name to "llama2:7b" in config/enhanced_system.json
   ```

## 📊 Monitoring

### Check System Status
```python
from src.infrastructure.factories.EnhancedSystemFactory import EnhancedSystemFactory

factory = EnhancedSystemFactory()
status = factory.get_system_status()
print(json.dumps(status, indent=2))
```

### Validate System
```python
validation = factory.validate_system()
if validation['valid']:
    print("✅ System is ready!")
else:
    print("❌ Issues found:", validation['errors'])
```

## 🎯 Usage Examples

### Process Single Question
```python
from src.infrastructure.factories.EnhancedSystemFactory import EnhancedSystemFactory

factory = EnhancedSystemFactory()
engine = factory.create_chain_of_thought_engine()

question = "แผนกไหนที่ให้บริการโรคหัวใจ?"
result = engine.process_query(question)
print(f"Answer: {result['answer']}")
```

### Process Batch Questions
```python
from src.scripts.process_healthcare_qa import HealthcareQAProcessor

processor = HealthcareQAProcessor()
questions = processor.load_test_data('src/infrastructure/test.csv')
results = processor.process_batch(questions[:5])  # Process first 5 questions
```

## 📝 Notes

- ระบบใช้ **pre-plan + fetch-all** strategy เพื่อประสิทธิภาพสูงสุด
- รองรับการอ่านไฟล์จากหลายโฟลเดอร์พร้อมกัน
- เชื่อมต่อกับ MCP server ของ CMKL สำหรับข้อมูลเพิ่มเติม
- ใช้ `llama2:13b` แทน `llama2:70b` เพื่อความเร็วและประหยัดทรัพยากร
- ผลลัพธ์จะถูก extract เป็นรูปแบบ ก,ข,ค,ง ตามที่ต้องการ

---

**Ready to process healthcare Q&A dataset! 🚀** 