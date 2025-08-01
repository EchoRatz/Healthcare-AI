# PDF Extractor with Thai Grammar Correction - Quick Usage Guide

## Basic Commands

### 1. Direct Text Extraction (No API Key Required)
```bash
python PDF_Extractor.py doc.pdf results direct
python PDF_Extractor.py doc2.pdf results direct
python PDF_Extractor.py doc3.pdf results direct
```

### 2. NVIDIA API Processing (Requires API Key)
First, set your API key:
```bash
# Replace YOUR_API_KEY with your actual NVIDIA API key
export API_KEY="YOUR_API_KEY"
```

Then run:
```bash
python PDF_Extractor.py doc.pdf results nvidia 0
python PDF_Extractor.py doc.pdf results nvidia 1
python PDF_Extractor.py doc.pdf results nvidia 2
```

### 3. Both Methods
```bash
python PDF_Extractor.py doc.pdf results both 1
```

## ✨ NEW: Thai Grammar Correction with Typhoon.ai

### 4. Grammar Correction Setup
First, get your free Typhoon.ai API key from: https://docs.opentyphoon.ai/

Set your API key:
```bash
export TYPHOON_API_KEY="your_typhoon_api_key_here"
```

### 5. Extract + Grammar Correction
```bash
# Extract text and apply grammar correction
python PDF_Extractor.py doc.pdf results direct --correct-grammar

# Both extraction methods + grammar correction
python PDF_Extractor.py doc.pdf results both 1 --correct-grammar

# Use inline API key
python PDF_Extractor.py doc.pdf results direct --correct-grammar --typhoon-key YOUR_KEY
```

### 6. Grammar Correction Only
```bash
# Correct grammar on existing extracted text
python PDF_Extractor.py test_results/direct_extraction.txt corrected_results grammar-only

# Correct grammar on PDF (extract first, then correct)
python PDF_Extractor.py doc.pdf corrected_results grammar-only --typhoon-key YOUR_KEY
```

## Tool Options (for NVIDIA API)

- **0: markdown_bbox** - Extracts content with bounding box information
- **1: markdown_no_bbox** - Extracts clean content without bounding boxes
- **2: detection_only** - Only detects elements without full extraction

## Output Files

### Direct Method:
- `direct_extraction.txt` - Plain text content from all pages

### NVIDIA API Method:
- `combined_results.json` - Complete results from all pages
- `page_1_result.json`, `page_2_result.json`, etc. - Individual page results

## Examples

```bash
# Extract text from all your PDF files
python PDF_Extractor.py doc.pdf doc_results direct
python PDF_Extractor.py doc2.pdf doc2_results direct  
python PDF_Extractor.py doc3.pdf doc3_results direct

# Use NVIDIA API for advanced processing
python PDF_Extractor.py doc.pdf nvidia_results nvidia 1
```

## Features

✅ **Multi-page PDF support**  
✅ **Thai language support**  
✅ **High-quality image conversion (200 DPI)**  
✅ **Automatic cleanup of temporary files**  
✅ **Detailed error handling**  
✅ **Multiple output formats**  

## Notes

- Direct method works offline and doesn't require API keys
- NVIDIA API method provides better OCR and layout analysis
- Both methods preserve page structure
- Results are saved in UTF-8 encoding for proper Thai text display