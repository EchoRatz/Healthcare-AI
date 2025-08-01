# ChainLang Q&A System

A Chain of Thought + Agentic reasoning system that processes questions from CSV files, consults text files as a knowledge base, and maintains memory of previous Q&A pairs for improved performance over time.

## 🏗️ Architecture

The system follows a **ChainLang** approach with this reasoning flow:
```
Load → Parse → Retrieve → Reason → Answer → Store
```

### Key Components

1. **Knowledge Base**: Static information from 3 text files
2. **Memory System**: Dynamic storage of previous Q&A pairs
3. **Chain of Thought Reasoning**: Step-by-step logical processing
4. **Similarity Search**: TF-IDF based document and memory retrieval
5. **Confidence Scoring**: Quality assessment of generated answers

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Prepare Your Data
- **questions.csv**: One question per row
- **file1.txt, file2.txt, file3.txt**: Your knowledge base documents

### 3. Run the System
```python
# For full CSV processing
python chainlang_qa_system.py

# For testing individual components
python test_qa_system.py
```

## 📁 File Structure

```
.
├── chainlang_qa_system.py    # Main Q&A system implementation
├── test_qa_system.py         # Test script and examples
├── questions.csv             # Input questions
├── file1.txt                 # Knowledge base file 1
├── file2.txt                 # Knowledge base file 2  
├── file3.txt                 # Knowledge base file 3
├── requirements.txt          # Python dependencies
├── qa_memory.json           # Persistent Q&A memory (auto-generated)
└── answers.csv              # Output results (auto-generated)
```

## 🧠 How It Works

### Chain of Thought Reasoning Process

1. **Document Retrieval**: Search knowledge base using TF-IDF similarity
2. **Direct Extraction**: Attempt to find direct answers in documents
3. **Memory Search**: Look for similar questions in previous Q&A pairs
4. **Inference**: Generate plausible answers from available context
5. **Fallback**: Return "not found" if no sufficient information exists

### Memory System

- **Storage**: JSON persistence of all Q&A pairs with metadata
- **Retrieval**: Keyword-based similarity matching for related questions
- **Learning**: System improves over time by referencing past answers

### Confidence Scoring

- **High (0.8)**: Direct answer found in knowledge base
- **Medium (0.6)**: Answer adapted from similar memory entry
- **Low (0.4)**: Inferred answer from partial context
- **None (0.0)**: No answer could be generated

## 📊 Output Format

The system generates answers in this format:
```csv
Question,Answer,Source,Confidence,Timestamp
"What is AI?","Artificial intelligence is...","docs",0.8,"2024-01-15T10:30:00"
```

**Source Types:**
- `docs`: Answer from knowledge base documents
- `memory`: Answer from previous Q&A memory
- `not_found`: No sufficient information available

## 🔧 Customization

### Adding More Knowledge Files
```python
knowledge_files = ['file1.txt', 'file2.txt', 'file3.txt', 'file4.txt']
qa_system = ChainLangQASystem(knowledge_files)
```

### Adjusting Similarity Thresholds
```python
# In _search_memory_for_answer method
memory_match = self._search_memory_for_answer(question, threshold=0.4)

# In _find_relevant_documents method  
if similarities[idx] > 0.2:  # Lower threshold for more results
```

### Custom Preprocessing
Override the `_preprocess_text` method to add domain-specific text cleaning.

## 🎯 Example Usage

```python
from chainlang_qa_system import ChainLangQASystem

# Initialize system
qa_system = ChainLangQASystem(['knowledge1.txt', 'knowledge2.txt', 'knowledge3.txt'])

# Process single question
result = qa_system.answer_question("What is machine learning?")
print(f"Answer: {result.answer}")
print(f"Confidence: {result.confidence}")

# Process CSV batch
results = qa_system.process_csv_questions('input_questions.csv', 'output_answers.csv')
```

## 🧪 Testing

Run the test suite to verify everything works:

```bash
python test_qa_system.py
```

This will:
- Test individual question processing
- Verify memory functionality
- Process the sample CSV file
- Generate test results and summaries

## 📈 Performance Tips

1. **Quality Data**: Ensure knowledge base files contain relevant, well-structured information
2. **Clear Questions**: More specific questions yield better results
3. **Iterative Improvement**: The system learns from each session, improving over time
4. **Memory Management**: Periodically review and clean the qa_memory.json file

## 🤝 Contributing

Feel free to enhance the system by:
- Adding more sophisticated similarity algorithms
- Implementing advanced NLP preprocessing
- Adding support for additional file formats
- Improving the reasoning chain logic

## 📄 License

This project is open source and available under the MIT License.