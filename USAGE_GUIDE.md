# PDF Extractor Usage Guide

This tool extracts structured information from PDF documents using NVIDIA's NeMo Parse API.

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get NVIDIA API Key
1. Visit [NVIDIA Build](https://build.nvidia.com/)
2. Sign up/login and get your API key
3. Replace `$API_KEY_REQUIRED_IF_EXECUTING_OUTSIDE_NGC` in `PDF_Extractor.py` with your actual API key

### 3. Update API Key
Edit line 11 in `PDF_Extractor.py`:
```python
"Authorization": "Bearer YOUR_ACTUAL_API_KEY_HERE",
```

## Usage

### Command Line Interface

#### Basic Usage
```bash
python PDF_Extractor.py document.pdf
```

#### Save Results to Directory
```bash
python PDF_Extractor.py document.pdf results/
```

#### Choose Extraction Mode
```bash
python PDF_Extractor.py document.pdf results/ 0
```

#### Get Help
```bash
python PDF_Extractor.py --help
```

### Extraction Modes

| Task ID | Mode | Description |
|---------|------|-------------|
| 0 | `markdown_bbox` | Extract content with bounding box coordinates |
| 1 | `markdown_no_bbox` | Extract content without bounding boxes |
| 2 | `detection_only` | Detect document elements only |

### Programmatic Usage

```python
from PDF_Extractor import extract_pdf_info

# Extract PDF information
result = extract_pdf_info(
    file_path="document.pdf",
    output_dir="results",
    task_id=0  # markdown_bbox
)

if result:
    print("Extraction successful!")
    # Process result...
else:
    print("Extraction failed!")
```

## Output

The extractor will:
1. Upload your PDF to NVIDIA's API
2. Process it using NeMo Parse
3. Return structured JSON results
4. Save results to a JSON file (if output directory specified)

### Sample Output Structure
```json
{
  "choices": [
    {
      "message": {
        "tool_calls": [
          {
            "function": {
              "name": "markdown_bbox",
              "arguments": "{\"markdown\": \"# Document Title\\n\\nContent here...\"}"
            }
          }
        ]
      }
    }
  ]
}
```

## Supported File Types

- PDF files (`.pdf`)
- Image files (`.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.tif`)

## Troubleshooting

### Common Issues

#### 1. **401 Authentication Error** 
```
Error uploading asset: 401 Client Error: for url: https://api.nvcf.nvidia.com/v2/nvcf/assets
```

**Solution:**
- Make sure you've replaced `YOUR_API_KEY_HERE` with your actual API key from build.nvidia.com
- Your API key should start with `nvapi-` and be quite long
- Test your connection: `python test_api_connection.py`

#### 2. **Getting Your API Key**
1. Go to [build.nvidia.com](https://build.nvidia.com)
2. Sign up with your email (get 5,000 free credits!)
3. Click on any model
4. In the code example, click "Get API Key" → "Generate Key"
5. Copy the full key (starts with `nvapi-`)

#### 3. **Testing Your Setup**
```bash
# First, test your API connection
python test_api_connection.py

# If that works, try extracting a PDF
python PDF_Extractor.py document.pdf
```

#### 4. **Other Common Issues**
- **File Not Found**: Check that your PDF file path is correct
- **Network Issues**: Ensure you have internet connectivity
- **Large Files**: Very large PDFs may take longer to process
- **Rate Limits**: If you hit API limits, wait a few minutes or check your credit balance

### Getting Help

Run with `--help` flag for detailed usage information:
```bash
python PDF_Extractor.py --help
```

## Examples

See `example_usage.py` for programmatic usage examples.

## API Limits

Be aware of NVIDIA API rate limits and usage quotas. Check your NVIDIA Build dashboard for current usage.