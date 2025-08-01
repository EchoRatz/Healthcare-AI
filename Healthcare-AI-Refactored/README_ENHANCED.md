# Enhanced Chain-of-Thought AI System

A sophisticated AI system using Ollama 40GB model with advanced chain-of-thought reasoning, pre-plan + fetch-all data retrieval, and support for MCP, PDF, and Text data sources.

## 🏗️ System Architecture

The system implements the architecture specified in the technical specification with three main components:

### 1. Query Planner
- Uses Ollama 40GB model to analyze questions
- Creates structured retrieval plans in YAML format
- Implements chain-of-thought reasoning for planning
- Supports MCP, PDF, and Text data sources

### 2. Data Connectors
- **MCP Connector**: Model Context Protocol client for structured data
- **PDF Connector**: PyPDF2-based text extraction from PDF documents
- **Text Connector**: Plain text file reading with line range support

### 3. Chain-of-Thought Reasoning Engine
- Pre-plan + fetch-all strategy for optimal performance
- Batch data retrieval to minimize latency
- Enhanced reasoning with step-by-step analysis
- Support for multiple data sources simultaneously

## 🚀 Quick Start

### Prerequisites

1. **Ollama Installation**
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull the 70B model (40GB quantized)
   ollama pull llama2:70b
   ```

2. **Python Dependencies**
   ```bash
   pip install -r requirements_enhanced.txt
   ```

3. **Hardware Requirements**
   - GPU with ≥40GB VRAM (NVIDIA A100, H100, or AMD MI300)
   - 64GB+ system RAM recommended
   - For CPU-only: 128GB+ RAM

### Basic Setup

1. **Configure the system**
   ```bash
   # Edit configuration
   nano config/enhanced_system.json
   ```

2. **Run the demo**
   ```bash
   python src/scripts/enhanced_system_demo.py --demo
   ```

3. **Interactive mode**
   ```bash
   python src/scripts/enhanced_system_demo.py
   ```

## 📋 Configuration

### Enhanced System Configuration (`config/enhanced_system.json`)

```json
{
  "llm": {
    "provider": "ollama",
    "model_name": "llama2:70b",
    "base_url": "http://localhost:11434",
    "temperature": 0.7,
    "max_tokens": 2000,
    "quantization": "q8_0"
  },
  "connectors": {
    "mcp": {
      "enabled": true,
      "server_url": "http://localhost:3000"
    },
    "pdf": {
      "enabled": true,
      "base_path": "data/documents"
    },
    "text": {
      "enabled": true,
      "base_path": "data/documents"
    }
  }
}
```

### Hardware Optimization

For optimal performance with the 40GB model:

1. **GPU Setup**
   ```bash
   # Check GPU memory
   nvidia-smi
   
   # Set environment variables for Ollama
   export OLLAMA_HOST=0.0.0.0:11434
   export OLLAMA_ORIGINS=*
   ```

2. **Quantization Settings**
   - Use `q8_0` for 40GB GPU
   - Use `q4_0` for 24GB GPU
   - Use `q2_K` for 16GB GPU

## 🔧 Usage Examples

### Single Query Processing

```python
from infrastructure.factories.EnhancedSystemFactory import EnhancedSystemFactory

# Create system
factory = EnhancedSystemFactory("config/enhanced_system.json")
engine = factory.create_chain_of_thought_engine()

# Process query
result = engine.process_query("What are the symptoms of diabetes?")
print(result['answer'])
```

### Batch Processing

```python
queries = [
    "What are the main symptoms of diabetes?",
    "How do I configure the system for optimal performance?",
    "What are the latest treatment guidelines for hypertension?"
]

results = engine.process_batch(queries)
for result in results:
    print(f"Q: {result['query']}")
    print(f"A: {result['answer']}")
```

### System Information

```python
# Get system status
status = factory.get_system_status()
print(json.dumps(status, indent=2))

# Validate system
validation = factory.validate_system()
if validation['valid']:
    print("System is ready!")
else:
    print("System validation failed:", validation['errors'])
```

## 📊 Performance Characteristics

### Expected Latency
- **Planning Phase**: 100-500ms (GPU)
- **Data Retrieval**: 0.1-2.0s (depends on sources)
- **Reasoning Phase**: 2-8s (40GB model)
- **Total Response Time**: 3-10 seconds

### Accuracy Goals
- **Factual Accuracy**: >90% on domain-specific queries
- **Reasoning Quality**: Enhanced with chain-of-thought
- **Source Grounding**: All answers traceable to data sources

### Resource Usage
- **GPU Memory**: 40GB for 70B model
- **System Memory**: 64GB+ recommended
- **Storage**: 10GB+ for documents and vectors

## 🔍 Data Sources

### MCP (Model Context Protocol)
```python
# Example MCP request
mcp_request = {
    "endpoint": "get_user_data",
    "params": {"user_id": 42}
}
```

### PDF Documents
```python
# Example PDF request
pdf_request = {
    "file": "medical_manual.pdf",
    "pages": [1, 2, 3]  # Specific pages
}
```

### Text Files
```python
# Example text request
text_request = {
    "file": "notes.txt",
    "line_range": [10, 50]  # Line range
}
```

## 🛠️ Development

### Project Structure
```
Healthcare-AI-Refactored/
├── config/
│   ├── app.json                 # Original config
│   └── enhanced_system.json     # Enhanced system config
├── src/
│   ├── core/
│   │   ├── interfaces/          # Abstract interfaces
│   │   └── use_cases/          # Business logic
│   ├── infrastructure/
│   │   ├── connectors/          # Data connectors
│   │   ├── planners/           # Query planners
│   │   └── factories/          # System factories
│   └── scripts/
│       └── enhanced_system_demo.py
├── data/
│   └── documents/              # PDF and text files
└── requirements_enhanced.txt
```

### Adding New Connectors

1. **Implement the interface**
   ```python
   from core.interfaces.DataConnectorInterface import DataConnectorInterface
   
   class NewConnector(DataConnectorInterface):
       def fetch(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
           # Implementation
           pass
   ```

2. **Add to factory**
   ```python
   def create_new_connector(self) -> Optional[DataConnectorInterface]:
       # Factory method
       pass
   ```

3. **Update configuration**
   ```json
   {
     "connectors": {
       "new_source": {
         "enabled": true,
         "config": "value"
       }
     }
   }
   ```

## 🧪 Testing

### Unit Tests
```bash
pytest tests/ -v
```

### Integration Tests
```bash
python src/scripts/enhanced_system_demo.py --demo --detailed
```

### Performance Tests
```bash
# Test with different model sizes
python -c "
from infrastructure.factories.EnhancedSystemFactory import EnhancedSystemFactory
factory = EnhancedSystemFactory()
engine = factory.create_chain_of_thought_engine()
import time
start = time.time()
result = engine.process_query('Test query')
print(f'Time: {time.time() - start:.2f}s')
"
```

## 🔧 Troubleshooting

### Common Issues

1. **Ollama not available**
   ```bash
   # Check Ollama service
   curl http://localhost:11434/api/tags
   
   # Start Ollama
   ollama serve
   ```

2. **GPU memory issues**
   ```bash
   # Use smaller model
   ollama pull llama2:13b
   
   # Or use quantization
   ollama pull llama2:70b:q8_0
   ```

3. **PDF processing errors**
   ```bash
   # Install PyPDF2
   pip install PyPDF2
   
   # Or use alternative
   pip install PyMuPDF
   ```

### Performance Optimization

1. **Enable quantization**
   ```json
   {
     "llm": {
       "quantization": "q8_0"
     }
   }
   ```

2. **Adjust batch size**
   ```json
   {
     "processing": {
       "batch_size": 3
     }
   }
   ```

3. **Use caching**
   ```json
   {
     "performance": {
       "enable_caching": true
     }
   }
   ```

## 📈 Monitoring

### System Metrics
- Query processing time
- Data retrieval latency
- GPU utilization
- Memory usage
- Error rates

### Logging
```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Ollama team for the excellent LLM serving framework
- Model Context Protocol (MCP) for standardized data access
- PyPDF2 for PDF text extraction
- The open-source AI community for inspiration and tools

---

**Note**: This enhanced system is designed for high-performance AI reasoning with the Ollama 40GB model. Ensure you have adequate hardware resources before deployment. 