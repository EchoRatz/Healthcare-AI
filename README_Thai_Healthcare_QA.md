# Thai Healthcare Q&A System with ChainLang Reasoning

A specialized ChainLang (Chain of Thought + Agentic Reasoning) system for Thai healthcare multiple-choice question answering based on healthcare policy documents.

## 🎯 Task Overview

**Input Format**: Thai healthcare questions with 4 multiple choice options (ก, ข, ค, ง)
**Output Format**: Submission CSV with predictions in exact format:
```csv
id,answer
1,"ง"
2,"ก"
5,"ข,ง"
6,"ก,ค,ง"
```

## 🏗️ System Architecture

### ChainLang Reasoning Flow:
```
Load Thai Documents → Parse Questions → Retrieve Relevant Content → 
Analyze Choices → Reason → Predict → Format Submission
```

### Key Components:

1. **Thai Text Processing**: Character-level analysis optimized for Thai language
2. **Healthcare Knowledge Base**: 3 comprehensive Thai healthcare policy documents
3. **Choice Scoring**: Evaluates each option against retrieved evidence
4. **Memory System**: Learns from processed questions for consistency
5. **Confidence Assessment**: Provides reliability scores for predictions

## 📁 Files Structure

### Core System:
- **`thai_healthcare_qa_system.py`** - Main Q&A system implementation
- **`test_thai_system.py`** - Testing suite for system validation
- **`run_thai_qa.py`** - Production runner for final submission

### Input Data:
- **`Healthcare-AI-Refactored/src/infrastructure/test.csv`** - Test questions (500+ items)
- **`Healthcare-AI-Refactored/src/infrastructure/results_doc/direct_extraction_corrected.txt`** - Healthcare policy doc 1
- **`Healthcare-AI-Refactored/src/infrastructure/results_doc2/direct_extraction_corrected.txt`** - Healthcare policy doc 2  
- **`Healthcare-AI-Refactored/src/infrastructure/results_doc3/direct_extraction_corrected.txt`** - Healthcare policy doc 3

### Output Files:
- **`submission.csv`** - Final predictions in required format
- **`submission_detailed.json`** - Detailed analysis with reasoning chains
- **`thai_healthcare_memory.json`** - System memory for consistency

## 🚀 Quick Start

### 1. Test the System (Recommended first):
```bash
pip install -r requirements.txt
python test_thai_system.py
```

### 2. Generate Final Submission:
```bash
python run_thai_qa.py
```

### 3. Alternative - Direct Processing:
```bash
python thai_healthcare_qa_system.py
```

## 🧠 Chain of Thought Reasoning

### Step-by-Step Process:

1. **Document Retrieval** (ค้นหาข้อมูลที่เกี่ยวข้อง):
   - Uses TF-IDF with character-level n-grams for Thai text
   - Finds top 10-15 most relevant sentences from healthcare documents
   - Weights by similarity scores

2. **Choice Analysis** (วิเคราะห์ตัวเลือก):
   - Calculates match score for each choice (ก, ข, ค, ง) against evidence
   - Uses character-level intersection weighted by document similarity
   - Considers semantic and lexical overlap

3. **Decision Making** (ตัดสินใจ):
   - Selects choices scoring above threshold (80% of max score)
   - Allows multiple answers when scores are close
   - Provides confidence assessment

4. **Memory Integration** (หน่วยความจำ):
   - Stores processed questions for future reference
   - Uses similarity matching for consistent answers
   - Builds knowledge over processing sessions

## 📊 Expected Performance

### Confidence Levels:
- **High (>0.5)**: Direct evidence found in documents
- **Medium (0.2-0.5)**: Partial evidence or memory-based answers  
- **Low (<0.2)**: Fallback predictions with minimal evidence

### Answer Distribution:
- **Single Answers**: Most common pattern (80-90%)
- **Multiple Answers**: When evidence supports multiple choices (10-20%)
- **Default Fallback**: "ข" (common Thai multiple choice default)

## 🔧 Customization Options

### Adjust Similarity Thresholds:
```python
# In _find_relevant_content method
if similarities[idx] > 0.05:  # Lower = more results

# In _calculate_choice_score method  
threshold = max_score * 0.8  # Lower = more multiple answers
```

### Modify Thai Text Processing:
```python
# Character n-gram range for TF-IDF
ngram_range=(1, 3)  # Adjust for different text patterns

# Minimum sentence length
if len(part.strip()) > 10:  # Adjust threshold
```

### Change Default Answers:
```python
predicted_answers = ["ข"]  # Modify fallback choice
```

## 🧪 Testing Features

### Question Parsing Test:
- Validates extraction of questions and multiple choice options
- Tests Thai text preprocessing
- Verifies choice scoring mechanism

### Small Subset Test:
- Processes first 5 questions as validation
- Checks output format compliance
- Validates reasoning chain functionality

### System Readiness Check:
- Verifies all required files exist
- Shows file sizes and status
- Confirms system is ready for full processing

## 📈 Performance Monitoring

The system provides detailed analytics:
- Processing time per question
- Confidence distribution across predictions
- Answer pattern analysis
- Evidence quality assessment
- Memory utilization statistics

## 🎯 Submission Format

**Exact format required**:
```csv
id,answer
1,"ง"
2,"ก,ข"
3,"ค"
```

**Key Requirements**:
- Header row: `id,answer`
- Quoted answers: `"ง"` not `ง`
- Multiple answers: `"ก,ข,ง"` (comma-separated)
- Complete coverage: All test IDs must have predictions

## 🔍 Troubleshooting

### Common Issues:

1. **Missing Files**: Ensure all healthcare documents are in correct paths
2. **Encoding Errors**: System expects UTF-8 encoded Thai text
3. **Memory Issues**: Large documents may require adjustment of TF-IDF max_features
4. **Confidence Too Low**: Adjust similarity thresholds if predictions seem conservative

### File Path Issues:
```bash
# Check file structure matches:
Healthcare-AI-Refactored/
  src/
    infrastructure/
      test.csv
      results_doc/
        direct_extraction_corrected.txt
      results_doc2/
        direct_extraction_corrected.txt  
      results_doc3/
        direct_extraction_corrected.txt
```

## 📊 Expected Runtime

- **Initialization**: 30-60 seconds (loading documents, creating embeddings)
- **Processing**: 1-3 seconds per question
- **Total Time**: 10-30 minutes for full dataset (500 questions)
- **Memory Usage**: 1-2 GB RAM (depends on document size)

## 🎉 Success Indicators

✅ **System Ready**: All files found, embeddings created  
✅ **Processing**: Questions parsed correctly, evidence found  
✅ **Output**: submission.csv generated with correct format  
✅ **Validation**: Correct number of predictions, proper encoding  

Run the system and check for these success indicators to ensure proper operation!