import os
import sys
import zipfile
import requests
import json
import fitz  # PyMuPDF
from pdf2image import convert_from_path
from PIL import Image
import io
import tempfile
import time

nvai_url = "https://integrate.api.nvidia.com/v1/chat/completions"

headers = {
  "Authorization": "Bearer $API_KEY_REQUIRED_IF_EXECUTING_OUTSIDE_NGC",
  "Accept": "application/json"
}

# Typhoon.ai API configuration
typhoon_url = "https://api.opentyphoon.ai/v1/chat/completions"
typhoon_headers = {
    "Authorization": "Bearer $TYPHOON_API_KEY",
    "Content-Type": "application/json"
}

tools = [
    "markdown_bbox",
    "markdown_no_bbox",
    "detection_only",
]


def _upload_asset(input, description):
    """
    Uploads an asset to the NVCF API.
    :param input: The binary asset to upload
    :param description: A description of the asset

    """

    authorize = requests.post(
        "https://api.nvcf.nvidia.com/v2/nvcf/assets",
        headers={
            "Content-Type": "application/json",
            **headers,
        },
        json={"contentType": "image/jpeg", "description": description},
        timeout=30,
    )
    authorize.raise_for_status()

    response = requests.put(
        authorize.json()["uploadUrl"],
        data=input,
        headers={
            "x-amz-meta-nvcf-asset-description": description,
            "content-type": "image/jpeg",
        },
        timeout=300,
    )

    response.raise_for_status()
    return str(authorize.json()["assetId"])

def _generate_content(task_id, asset_id):
    if task_id < 0 or task_id >= len(tools):
        print(f"task_id should within [0, {len(tools)-1}]")
        exit(1)
    tool = [{
        "type": "function",
        "function": {"name": tools[task_id]},
    }]
    content = [{
        "type": "image_url",
        "image_url": {"url": f"data:image/jpeg;asset_id,{asset_id}" }
    }]
    return content, tool

def extract_text_from_pdf_direct(pdf_path):
    """
    Extract text from PDF line by line in proper reading order (horizontal flow).
    Uses PyMuPDF with layout analysis for better text positioning.
    """
    try:
        doc = fitz.open(pdf_path)
        text = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += f"\n--- Page {page_num + 1} ---\n"
            
            # Extract text with positioning information
            page_text = extract_text_line_by_line(page)
            text += page_text
            
        doc.close()
        return text
    except Exception as e:
        print(f"Error extracting text directly from PDF: {e}")
        return None

def extract_text_line_by_line(page):
    """
    Extract text from a PDF page line by line in proper reading order.
    Groups text by lines and sorts horizontally within each line.
    """
    try:
        # Get text with detailed positioning using text dictionary
        text_dict = page.get_text("dict")
        
        # Extract all text blocks with position information
        text_elements = []
        
        for block in text_dict["blocks"]:
            if "lines" in block:  # Text block (not image)
                for line in block["lines"]:
                    line_text = ""
                    line_bbox = line["bbox"]  # Bounding box: (x0, y0, x1, y1)
                    
                    # Collect all text spans in this line
                    spans_in_line = []
                    for span in line["spans"]:
                        if span["text"].strip():  # Only non-empty text
                            spans_in_line.append({
                                "text": span["text"],
                                "x0": span["bbox"][0],
                                "y0": span["bbox"][1],
                                "x1": span["bbox"][2], 
                                "y1": span["bbox"][3]
                            })
                    
                    # Sort spans in this line by horizontal position (left to right)
                    spans_in_line.sort(key=lambda x: x["x0"])
                    
                    # Combine spans into line text
                    line_text = ""
                    prev_x1 = 0
                    for span in spans_in_line:
                        # Add space if there's a significant gap between spans
                        if prev_x1 > 0 and span["x0"] - prev_x1 > 5:
                            line_text += " "
                        line_text += span["text"]
                        prev_x1 = span["x1"]
                    
                    if line_text.strip():
                        text_elements.append({
                            "text": line_text,
                            "y": line_bbox[1],  # Use top y-coordinate for sorting
                            "x": line_bbox[0],  # Use left x-coordinate for secondary sorting
                            "bbox": line_bbox
                        })
        
        # Sort all text elements by vertical position (top to bottom)
        # Then by horizontal position (left to right) for elements at similar heights
        text_elements.sort(key=lambda x: (round(x["y"], 1), x["x"]))
        
        # Group elements into lines based on similar y-coordinates
        lines = []
        current_line = []
        current_y = -1
        y_threshold = 5  # Pixels tolerance for grouping into same line
        
        for element in text_elements:
            if current_y == -1 or abs(element["y"] - current_y) <= y_threshold:
                # Same line or first element
                current_line.append(element)
                current_y = element["y"]
            else:
                # New line
                if current_line:
                    # Sort current line by x-coordinate (left to right)
                    current_line.sort(key=lambda x: x["x"])
                    lines.append(current_line)
                current_line = [element]
                current_y = element["y"]
        
        # Don't forget the last line
        if current_line:
            current_line.sort(key=lambda x: x["x"])
            lines.append(current_line)
        
        # Build final text with proper line breaks
        page_text = ""
        for line_elements in lines:
            line_text = ""
            prev_x1 = 0
            
            for element in line_elements:
                # Add appropriate spacing between elements in the same line
                if prev_x1 > 0:
                    gap = element["x"] - prev_x1
                    if gap > 10:  # Significant gap - add space
                        line_text += " "
                    elif gap > 30:  # Very large gap - could be table columns
                        line_text += "   "  # Multiple spaces
                
                line_text += element["text"]
                prev_x1 = element["bbox"][2]  # Right edge of current element
            
            if line_text.strip():
                page_text += line_text.rstrip() + "\n"
        
        return page_text
        
    except Exception as e:
        print(f"Error in line-by-line extraction: {e}")
        # Fallback to simple text extraction
        try:
            return page.get_text()
        except:
            return ""

def extract_text_with_blocks(page):
    """
    Alternative extraction method using text blocks for better layout handling.
    Good for documents with complex layouts, tables, or multiple columns.
    """
    try:
        # Get text blocks - these preserve reading order better for complex layouts
        blocks = page.get_text("blocks")
        
        # Sort blocks by position (top to bottom, left to right)
        blocks.sort(key=lambda block: (round(block[1], 1), block[0]))  # y-coordinate first, then x
        
        page_text = ""
        for block in blocks:
            # block format: (x0, y0, x1, y1, "text content", block_num, block_type)
            if len(block) >= 5 and block[4].strip():  # Has text content
                text_content = block[4].strip()
                
                # Clean up the text - remove excessive whitespace but preserve structure
                lines = text_content.split('\n')
                cleaned_lines = []
                
                for line in lines:
                    cleaned_line = ' '.join(line.split())  # Normalize spaces
                    if cleaned_line:
                        cleaned_lines.append(cleaned_line)
                
                if cleaned_lines:
                    page_text += '\n'.join(cleaned_lines) + '\n\n'
        
        return page_text
        
    except Exception as e:
        print(f"Error in block-based extraction: {e}")
        return ""

def extract_text_from_pdf_enhanced(pdf_path, method="line_by_line"):
    """
    Enhanced PDF text extraction with multiple methods.
    
    Args:
        pdf_path: Path to PDF file
        method: "line_by_line" (default), "blocks", or "simple"
    """
    try:
        doc = fitz.open(pdf_path)
        text = ""
        
        print(f"Using extraction method: {method}")
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += f"\n--- Page {page_num + 1} ---\n"
            
            if method == "line_by_line":
                page_text = extract_text_line_by_line(page)
            elif method == "blocks":
                page_text = extract_text_with_blocks(page)
            else:  # simple
                page_text = page.get_text()
            
            text += page_text
            
        doc.close()
        return text
        
    except Exception as e:
        print(f"Error in enhanced PDF extraction: {e}")
        return None

def convert_pdf_to_images(pdf_path, output_dir=None):
    """
    Convert PDF pages to images for processing with NVIDIA API.
    """
    try:
        if output_dir is None:
            output_dir = tempfile.mkdtemp()
        
        # Convert PDF to images
        images = convert_from_path(pdf_path, dpi=200)
        image_paths = []
        
        for i, image in enumerate(images):
            image_path = os.path.join(output_dir, f"page_{i+1}.jpg")
            image.save(image_path, 'JPEG', quality=95)
            image_paths.append(image_path)
        
        return image_paths
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return None

def process_pdf_with_nvidia_api(pdf_path, task_id=0, output_dir="results"):
    """
    Process PDF by converting to images and using NVIDIA API for content extraction.
    """
    print(f"Processing PDF: {pdf_path}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert PDF to images
    temp_dir = tempfile.mkdtemp()
    image_paths = convert_pdf_to_images(pdf_path, temp_dir)
    
    if not image_paths:
        print("Failed to convert PDF to images")
        return None
    
    all_results = []
    
    for i, image_path in enumerate(image_paths):
        print(f"Processing page {i+1}/{len(image_paths)}")
        
        try:
            # Upload image to NVIDIA API
            with open(image_path, "rb") as img_file:
                asset_id = _upload_asset(img_file, f"PDF Page {i+1}")
            
            # Generate content and tools
            content, tool = _generate_content(task_id, asset_id)
            
            # Prepare API request
            inputs = {
                "tools": tool,
                "model": "nvidia/nemoretriever-parse",
                "messages": [{
                    "role": "user",
                    "content": content
                }]
            }
            
            post_headers = {
                "Content-Type": "application/json",
                "NVCF-INPUT-ASSET-REFERENCES": asset_id,
                "NVCF-FUNCTION-ASSET-IDS": asset_id,
                **headers
            }
            
            # Send request to NVIDIA API
            response = requests.post(nvai_url, headers=post_headers, json=inputs)
            
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    page_result = {
                        "page": i+1,
                        "response": response_json
                    }
                    all_results.append(page_result)
                    
                    # Save individual page result
                    page_output_path = os.path.join(output_dir, f"page_{i+1}_result.json")
                    with open(page_output_path, 'w', encoding='utf-8') as f:
                        json.dump(page_result, f, indent=2, ensure_ascii=False)
                    
                except ValueError:
                    print(f"Page {i+1}: Response is not in JSON format")
            else:
                print(f"Page {i+1}: API request failed with status {response.status_code}")
        
        except Exception as e:
            print(f"Error processing page {i+1}: {e}")
    
    # Clean up temporary files
    try:
        for image_path in image_paths:
            os.remove(image_path)
        os.rmdir(temp_dir)
    except:
        pass
    
    # Save combined results
    if all_results:
        combined_output_path = os.path.join(output_dir, "combined_results.json")
        with open(combined_output_path, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        print(f"Results saved to: {output_dir}")
        return all_results
    
    return None

def correct_thai_grammar_typhoon(text, api_key=None):
    """
    Correct Thai grammar using Typhoon.ai API.
    """
    if api_key:
        auth_headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    else:
        # Try to get API key from environment
        api_key = os.getenv('TYPHOON_API_KEY')
        if not api_key:
            print("Warning: No Typhoon API key provided. Grammar correction skipped.")
            return text
        auth_headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    try:
        # Prepare the prompt for Thai grammar correction
        prompt = f"""กรุณาแก้ไขไวยากรณ์และการสะกดภาษาไทยในข้อความต่อไปนี้ โดยคงความหมายเดิมไว้ให้มากที่สุด และแสดงเฉพาะข้อความที่แก้ไขแล้วเท่านั้น:

{text}

ข้อความที่แก้ไขแล้ว:"""

        payload = {
            "model": "typhoon-v2.1-12b-instruct",
            "messages": [
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": len(text.split()) + 500,  # Allow some extra tokens
            "temperature": 0.1,
            "top_p": 0.9
        }

        response = requests.post(typhoon_url, headers=auth_headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            corrected_text = result['choices'][0]['message']['content'].strip()
            
            # Clean up the response to get only the corrected text
            if "ข้อความที่แก้ไขแล้ว:" in corrected_text:
                corrected_text = corrected_text.split("ข้อความที่แก้ไขแล้ว:")[-1].strip()
            
            return corrected_text
        else:
            print(f"Typhoon API error: {response.status_code} - {response.text}")
            return text
            
    except Exception as e:
        print(f"Error correcting Thai grammar: {e}")
        return text

def process_text_in_chunks(text, chunk_size=2000, api_key=None):
    """
    Process large text in chunks for grammar correction to handle API token limits.
    """
    if not text or len(text.strip()) == 0:
        return text
    
    # Split text into paragraphs first
    paragraphs = text.split('\n\n')
    corrected_paragraphs = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        # If adding this paragraph would exceed chunk size, process current chunk
        if len(current_chunk) + len(paragraph) > chunk_size and current_chunk:
            corrected_chunk = correct_thai_grammar_typhoon(current_chunk, api_key)
            corrected_paragraphs.append(corrected_chunk)
            current_chunk = paragraph
            time.sleep(1)  # Rate limiting
        else:
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
    
    # Process the last chunk
    if current_chunk:
        corrected_chunk = correct_thai_grammar_typhoon(current_chunk, api_key)
        corrected_paragraphs.append(corrected_chunk)
    
    return "\n\n".join(corrected_paragraphs)

def correct_extracted_text_grammar(input_file, output_file, api_key=None):
    """
    Read extracted text file and apply Thai grammar correction.
    """
    try:
        print(f"Reading text from: {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        if not text.strip():
            print("No text to correct.")
            return False
        
        print("Applying Thai grammar correction...")
        print("This may take a few minutes for large documents...")
        
        corrected_text = process_text_in_chunks(text, chunk_size=1500, api_key=api_key)
        
        # Save corrected text
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(corrected_text)
        
        print(f"Grammar-corrected text saved to: {output_file}")
        return True
        
    except Exception as e:
        print(f"Error in grammar correction: {e}")
        return False

if __name__ == "__main__":
    """
    PDF Content Extractor with Thai Grammar Correction
    
    This program can extract content from PDF files using multiple methods:
    1. NVIDIA API (advanced OCR and layout analysis)
    2. Direct text extraction (fallback method)
    3. Typhoon.ai Thai grammar correction
    
    Usage:
    python PDF_Extractor.py <pdf_file> <output_dir> [method] [task_id] [--correct-grammar] [--typhoon-key KEY]
    
    Arguments:
    - pdf_file: Path to the PDF file to process
    - output_dir: Directory to save results
    - method: 'nvidia' (default) or 'direct' or 'both' or 'grammar-only'
    - task_id: Tool to use (0=markdown_bbox, 1=markdown_no_bbox, 2=detection_only)
    - --correct-grammar: Apply Thai grammar correction using Typhoon.ai
    - --typhoon-key: Typhoon.ai API key (or set TYPHOON_API_KEY environment variable)
    
    Examples:
    python PDF_Extractor.py doc.pdf results
    python PDF_Extractor.py doc.pdf results direct --correct-grammar
    python PDF_Extractor.py doc.pdf results both 1 --correct-grammar --typhoon-key YOUR_KEY
    python PDF_Extractor.py existing_text.txt results grammar-only --typhoon-key YOUR_KEY
    """

    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    # Parse arguments
    pdf_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Handle additional arguments
    args = sys.argv[3:]
    method = 'nvidia'
    task_id = 0
    correct_grammar = False
    typhoon_key = None
    
    i = 0
    while i < len(args):
        if args[i] == '--correct-grammar':
            correct_grammar = True
        elif args[i] == '--typhoon-key':
            i += 1
            if i < len(args):
                typhoon_key = args[i]
        elif args[i].startswith('--'):
            # Skip unknown flags
            pass
        elif args[i] in ['nvidia', 'direct', 'both', 'grammar-only']:
            method = args[i]
        elif args[i].isdigit():
            task_id = int(args[i])
        i += 1

    # Validate inputs
    if method == 'grammar-only':
        # For grammar-only mode, the first argument can be a text file
        if not os.path.exists(pdf_file):
            print(f"Error: File '{pdf_file}' not found.")
            sys.exit(1)
        if not (pdf_file.lower().endswith('.pdf') or pdf_file.lower().endswith('.txt')):
            print(f"Error: '{pdf_file}' must be a PDF or TXT file.")
            sys.exit(1)
    else:
        if not os.path.exists(pdf_file):
            print(f"Error: PDF file '{pdf_file}' not found.")
            sys.exit(1)
        if not pdf_file.lower().endswith('.pdf'):
            print(f"Error: '{pdf_file}' is not a PDF file.")
            sys.exit(1)

    if method not in ['nvidia', 'direct', 'both', 'grammar-only']:
        print(f"Error: Invalid method '{method}'. Use 'nvidia', 'direct', 'both', or 'grammar-only'.")
        sys.exit(1)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    print(f"Processing file: {pdf_file}")
    print(f"Output directory: {output_dir}")
    print(f"Method: {method}")
    
    if method in ['nvidia', 'both'] and task_id < len(tools):
        print(f"Task ID: {task_id} ({tools[task_id]})")
    
    if correct_grammar or method == 'grammar-only':
        if typhoon_key:
            print("Grammar correction: Enabled (Typhoon.ai API)")
        elif os.getenv('TYPHOON_API_KEY'):
            print("Grammar correction: Enabled (Typhoon.ai API from environment)")
        else:
            print("Warning: Grammar correction requested but no API key provided")

    results = {}

    # Handle grammar-only mode
    if method == 'grammar-only':
        print("\n=== Grammar Correction Only ===")
        if pdf_file.lower().endswith('.txt'):
            # Process existing text file
            output_file = os.path.join(output_dir, "grammar_corrected.txt")
            success = correct_extracted_text_grammar(pdf_file, output_file, typhoon_key)
            if success:
                results['grammar'] = "completed"
        else:
            # Extract text from PDF first, then correct grammar
            direct_text = extract_text_from_pdf_direct(pdf_file)
            if direct_text:
                temp_file = os.path.join(output_dir, "temp_extraction.txt")
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(direct_text)
                
                output_file = os.path.join(output_dir, "grammar_corrected.txt")
                success = correct_extracted_text_grammar(temp_file, output_file, typhoon_key)
                
                # Clean up temp file
                try:
                    os.remove(temp_file)
                except:
                    pass
                
                if success:
                    results['grammar'] = "completed"
            else:
                print("Failed to extract text from PDF.")
    else:
        # Method 1: Direct text extraction
        if method in ['direct', 'both']:
            print("\n=== Direct Text Extraction ===")
            direct_text = extract_text_from_pdf_direct(pdf_file)
            if direct_text:
                direct_output_path = os.path.join(output_dir, "direct_extraction.txt")
                with open(direct_output_path, 'w', encoding='utf-8') as f:
                    f.write(direct_text)
                print(f"Direct extraction saved to: {direct_output_path}")
                results['direct'] = direct_text
                
                # Apply grammar correction if requested
                if correct_grammar:
                    corrected_output_path = os.path.join(output_dir, "direct_extraction_corrected.txt")
                    print("\n=== Applying Grammar Correction ===")
                    success = correct_extracted_text_grammar(direct_output_path, corrected_output_path, typhoon_key)
                    if success:
                        results['direct_corrected'] = "completed"
            else:
                print("Direct text extraction failed.")

        # Method 2: NVIDIA API processing
        if method in ['nvidia', 'both']:
            print("\n=== NVIDIA API Processing ===")
            nvidia_results = process_pdf_with_nvidia_api(pdf_file, task_id, output_dir)
            if nvidia_results:
                print("NVIDIA API processing completed successfully.")
                results['nvidia'] = nvidia_results
            else:
                print("NVIDIA API processing failed.")

    # Summary
    print(f"\n=== Processing Complete ===")
    if results:
        print(f"Results saved to: {output_dir}")
        if 'direct' in results:
            print("- Direct text extraction: direct_extraction.txt")
        if 'direct_corrected' in results:
            print("- Grammar-corrected text: direct_extraction_corrected.txt")
        if 'nvidia' in results:
            print("- NVIDIA API results: combined_results.json and individual page files")
        if 'grammar' in results:
            print("- Grammar-corrected text: grammar_corrected.txt")
    else:
        print("No results were generated. Please check your inputs and try again.")

    # Display available tools for reference
    if method in ['nvidia', 'both']:
        print(f"\nAvailable tools for NVIDIA API:")
        for i, tool in enumerate(tools):
            print(f"  {i}: {tool}")
    
    if correct_grammar or method == 'grammar-only':
        print(f"\nTyphoon.ai Grammar Correction:")
        print(f"  - Model: typhoon-v2.1-12b-instruct")
        print(f"  - Optimized for Thai language")
        print(f"  - Processes text in chunks for large documents")
