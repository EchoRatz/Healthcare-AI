# 🇹🇭 Typhoon.ai Thai Grammar Correction Setup Guide

## Overview

Your PDF Extractor now includes **Thai grammar correction** powered by **Typhoon.ai** - Thailand's leading AI language model optimized specifically for Thai language processing.

## ✨ Features

- **Thai-First AI Model**: Typhoon-v2.1-12b-instruct optimized for Thai language
- **Grammar & Spelling Correction**: Fixes common Thai writing errors
- **Smart Chunking**: Handles large documents by processing in chunks
- **Preserves Meaning**: Maintains original context while improving readability
- **Free Tier Available**: Start testing with free API access

## 🚀 Quick Setup

### Step 1: Get Your Free API Key

1. Visit: https://docs.opentyphoon.ai/
2. Sign up for a free account
3. Navigate to API section
4. Generate your API key

### Step 2: Set Environment Variable

**Windows (PowerShell):**
```powershell
$env:TYPHOON_API_KEY = "your_api_key_here"
```

**Windows (Command Prompt):**
```cmd
set TYPHOON_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export TYPHOON_API_KEY="your_api_key_here"
```

### Step 3: Test the Setup

```bash
python test_typhoon_grammar.py
```

## 📋 Usage Examples

### Extract PDF + Grammar Correction
```bash
# Extract text and apply grammar correction
python PDF_Extractor.py doc.pdf results direct --correct-grammar

# Use inline API key (if not set in environment)
python PDF_Extractor.py doc.pdf results direct --correct-grammar --typhoon-key YOUR_KEY
```

### Grammar Correction Only
```bash
# Correct existing extracted text file
python PDF_Extractor.py test_results/direct_extraction.txt corrected grammar-only

# Extract from PDF and correct in one step
python PDF_Extractor.py doc.pdf corrected grammar-only
```

### Multiple Methods + Grammar Correction
```bash
# Extract with both methods + grammar correction
python PDF_Extractor.py doc.pdf results both 1 --correct-grammar
```

## 📁 Output Files

When grammar correction is enabled, you'll get:

- **Original extraction**: `direct_extraction.txt`
- **Grammar-corrected**: `direct_extraction_corrected.txt` or `grammar_corrected.txt`
- **Both files preserve**: Original formatting and page structure

## 🔧 Technical Details

### Model Information
- **Model**: `typhoon-v2.1-12b-instruct`
- **Context Window**: 56K tokens
- **Optimization**: Thai language processing
- **Rate Limits**: 5 requests/second (free tier)

### Processing Features
- **Smart Chunking**: Splits large texts into manageable pieces
- **Rate Limiting**: Built-in delays to respect API limits
- **Error Handling**: Graceful fallback if API fails
- **Encoding**: UTF-8 support for proper Thai display

### What Gets Corrected
- ✅ Thai spelling errors (การสะกด)
- ✅ Grammar mistakes (ไวยากรณ์)
- ✅ Word spacing issues
- ✅ Punctuation improvements
- ❌ Preserves original meaning and structure

## 🐛 Troubleshooting

### Common Issues

**1. "No TYPHOON_API_KEY found"**
```bash
# Check if environment variable is set
echo $TYPHOON_API_KEY  # Linux/Mac
echo %TYPHOON_API_KEY%  # Windows CMD
```

**2. "API request failed with status 401"**
```bash
# Your API key may be invalid or expired
# Generate a new key from: https://docs.opentyphoon.ai/
```

**3. "API request failed with status 429"**
```bash
# Rate limit exceeded - wait a moment and try again
# Consider using smaller text chunks
```

**4. Grammar correction takes too long**
- Large documents are processed in chunks
- Each chunk takes 1-3 seconds
- Total time depends on document size
- Progress is shown during processing

### Performance Tips

1. **For Large Documents**: Use `grammar-only` mode after extraction
2. **For Multiple Files**: Process them one at a time
3. **For Testing**: Use the test script with sample text first

## 📊 Example Results

### Before Grammar Correction:
```
คูรือสดทธิหลักประกันสุขภาพแหรงชาติ ปรงบประมาณ 2566
ตามที ส๚านักบรุการประชาชน มีภารกิจหลัก
```

### After Grammar Correction:
```
คู่มือสิทธิหลักประกันสุขภาพแห่งชาติ ปีงบประมาณ 2566
ตามที่ สำนักบริการประชาชน มีภารกิจหลัก
```

## 🔗 Resources

- **Typhoon.ai Documentation**: https://docs.opentyphoon.ai/
- **API Reference**: https://docs.opentyphoon.ai/en/api/
- **Model Details**: https://arxiv.org/abs/2412.13702
- **Community Discord**: Available on their website

## 💡 Tips for Best Results

1. **Shorter Chunks**: Better accuracy with smaller text sections
2. **Context Preservation**: Keep related paragraphs together
3. **Review Output**: AI corrections may occasionally change meaning
4. **Backup Originals**: Always keep original extracted text
5. **Test First**: Use sample text before processing large documents

## 🆘 Support

If you encounter issues:

1. **Check API Key**: Ensure it's valid and properly set
2. **Test Network**: Verify internet connection
3. **Review Logs**: Check error messages in terminal
4. **Try Sample**: Use `test_typhoon_grammar.py` first
5. **Contact Support**: Typhoon.ai community for API-specific issues

---

**Ready to improve your Thai text quality?** 🚀

Start with: `python test_typhoon_grammar.py`