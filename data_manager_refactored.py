#!/usr/bin/env python3
"""
Data Manager - Advanced Data Import and Processing System

This module provides comprehensive data import capabilities with support for
multiple file formats, encoding detection, and intelligent text processing.

Author: Healthcare-AI Team
Date: 2025-08-01
Version: 3.0.0
"""

import csv
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Union, Iterator, Tuple
from dataclasses import dataclass, field
from enum import Enum
import chardet
import re

# Configure logging
logger = logging.getLogger(__name__)


class FileType(Enum):
    """Supported file types."""
    TEXT = "text"
    MARKDOWN = "markdown"
    JSON = "json"
    CSV = "csv"
    XML = "xml"
    UNKNOWN = "unknown"


class ImportStatus(Enum):
    """Import operation status."""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    SKIPPED = "skipped"


@dataclass
class ImportResult:
    """Result of an import operation."""
    
    status: ImportStatus
    file_path: str
    items_imported: int = 0
    items_skipped: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, any] = field(default_factory=dict)
    processing_time: float = 0.0
    
    @property
    def success(self) -> bool:
        """Check if import was successful."""
        return self.status == ImportStatus.SUCCESS
    
    @property
    def total_items(self) -> int:
        """Total items processed."""
        return self.items_imported + self.items_skipped
    
    def __str__(self) -> str:
        """String representation of the result."""
        status_emoji = {
            ImportStatus.SUCCESS: "✅",
            ImportStatus.FAILED: "❌", 
            ImportStatus.PARTIAL: "⚠️",
            ImportStatus.SKIPPED: "⏭️"
        }
        
        emoji = status_emoji.get(self.status, "❓")
        return f"{emoji} {Path(self.file_path).name}: {self.items_imported} imported, {self.items_skipped} skipped"


@dataclass
class ProcessedText:
    """Processed text with metadata."""
    
    text: str
    original_text: str
    metadata: Dict[str, any] = field(default_factory=dict)
    chunk_index: int = 0
    total_chunks: int = 1
    
    def __post_init__(self):
        """Validate processed text."""
        if not self.text:
            raise ValueError("Processed text cannot be empty")


class TextProcessor:
    """Advanced text processing with Thai language support."""
    
    # Thai-specific patterns
    THAI_VOWELS = "เแโใไ"
    THAI_CONSONANTS = "กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ"
    
    # Cleaning patterns
    UNWANTED_CHARS = ['\r', '\t', '\x00', '\ufffd', '\u200b', '\u200c', '\u200d']
    MULTIPLE_SPACES_PATTERN = re.compile(r'\s+')
    MULTIPLE_NEWLINES_PATTERN = re.compile(r'\n\s*\n\s*\n+')
    
    def __init__(self):
        """Initialize text processor."""
        logger.debug("Text processor initialized")
    
    def clean_text(self, text: str, aggressive: bool = False) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Input text to clean
            aggressive: Whether to apply aggressive cleaning
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove unwanted characters
        for char in self.UNWANTED_CHARS:
            text = text.replace(char, '')
        
        # Normalize whitespace
        text = self.MULTIPLE_SPACES_PATTERN.sub(' ', text)
        text = self.MULTIPLE_NEWLINES_PATTERN.sub('\n\n', text)
        
        if aggressive:
            # More aggressive cleaning
            text = re.sub(r'[^\w\s\u0E00-\u0E7F]', '', text)  # Keep only Thai, alphanumeric, and spaces
        
        return text.strip()
    
    def split_into_chunks(
        self, 
        text: str, 
        chunk_size: int = 500, 
        overlap: int = 50,
        respect_sentences: bool = True
    ) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to split
            chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks
            respect_sentences: Whether to try to break at sentence boundaries
            
        Returns:
            List of text chunks
        """
        if not text or len(text) <= chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            
            # Try to find a good breaking point
            if respect_sentences and end < len(text):
                # Look for sentence endings
                sentence_endings = '.!?。'
                for i in range(end, max(start + chunk_size - 100, start), -1):
                    if text[i] in sentence_endings:
                        end = i + 1
                        break
                else:
                    # Look for word boundaries
                    for i in range(end, max(start + chunk_size - 50, start), -1):
                        if text[i].isspace():
                            end = i
                            break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = max(start + chunk_size - overlap, end)
        
        return chunks
    
    def extract_metadata_from_filename(self, file_path: Union[str, Path]) -> Dict[str, any]:
        """
        Extract metadata from filename and path.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary of extracted metadata
        """
        path = Path(file_path)
        filename_lower = path.stem.lower()
        
        # Category mapping
        categories = {
            'healthcare': ['health', 'medical', 'hospital', 'doctor', 'medicine', 'patient'],
            'programming': ['python', 'javascript', 'java', 'code', 'programming', 'software'],
            'ai': ['ai', 'machine_learning', 'ml', 'deep_learning', 'neural', 'model'],
            'data': ['data', 'database', 'sql', 'analytics', 'statistics'],
            'web': ['web', 'html', 'css', 'frontend', 'backend', 'api'],
            'thai': ['thai', 'ไทย', 'กทม', 'ภาษาไทย']
        }
        
        # Determine category
        category = 'general'
        for cat, keywords in categories.items():
            if any(keyword in filename_lower for keyword in keywords):
                category = cat
                break
        
        # Language detection (simple)
        language = 'thai' if any(char in self.THAI_CONSONANTS + self.THAI_VOWELS for char in path.name) else 'english'
        
        return {
            'filename': path.name,
            'stem': path.stem,
            'extension': path.suffix,
            'category': category,
            'language': language,
            'file_size': path.stat().st_size if path.exists() else 0,
            'parent_directory': path.parent.name
        }
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected language ('thai', 'english', 'mixed', 'unknown')
        """
        if not text:
            return 'unknown'
        
        thai_chars = sum(1 for char in text if char in self.THAI_CONSONANTS + self.THAI_VOWELS)
        total_chars = len(re.sub(r'\s+', '', text))
        
        if total_chars == 0:
            return 'unknown'
        
        thai_ratio = thai_chars / total_chars
        
        if thai_ratio > 0.5:
            return 'thai'
        elif thai_ratio > 0.1:
            return 'mixed'
        else:
            return 'english'


class EncodingDetector:
    """Encoding detection utility."""
    
    # Common encodings to try
    COMMON_ENCODINGS = ['utf-8', 'utf-16', 'cp874', 'latin1', 'ascii']
    
    @staticmethod
    def detect_encoding(file_path: Path) -> Tuple[str, float]:
        """
        Detect file encoding.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (encoding, confidence)
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB
            
            result = chardet.detect(raw_data)
            encoding = result.get('encoding', 'utf-8')
            confidence = result.get('confidence', 0.0)
            
            logger.debug(f"Detected encoding: {encoding} (confidence: {confidence:.2f})")
            return encoding, confidence
            
        except Exception as e:
            logger.warning(f"Encoding detection failed: {e}")
            return 'utf-8', 0.0
    
    @classmethod
    def read_file_with_fallback(cls, file_path: Path) -> Tuple[str, str]:
        """
        Read file with encoding fallback.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (content, encoding_used)
        """
        # Try detected encoding first
        detected_encoding, confidence = cls.detect_encoding(file_path)
        
        encodings_to_try = [detected_encoding] + cls.COMMON_ENCODINGS
        
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                logger.debug(f"Successfully read file with encoding: {encoding}")
                return content, encoding
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        # Last resort: read as bytes and replace errors
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            logger.warning("Used UTF-8 with error replacement")
            return content, 'utf-8-replace'
        except Exception as e:
            raise IOError(f"Unable to read file {file_path}: {e}")


class DataImporter:
    """Advanced data importer with multiple format support."""
    
    FILE_TYPE_MAPPING = {
        '.txt': FileType.TEXT,
        '.md': FileType.MARKDOWN,
        '.markdown': FileType.MARKDOWN,
        '.json': FileType.JSON,
        '.csv': FileType.CSV,
        '.xml': FileType.XML
    }
    
    def __init__(self, text_processor: Optional[TextProcessor] = None):
        """
        Initialize data importer.
        
        Args:
            text_processor: Optional text processor instance
        """
        self.text_processor = text_processor or TextProcessor()
        self.encoding_detector = EncodingDetector()
        logger.info("Data importer initialized")
    
    def get_file_type(self, file_path: Path) -> FileType:
        """
        Determine file type from extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            FileType enum value
        """
        extension = file_path.suffix.lower()
        return self.FILE_TYPE_MAPPING.get(extension, FileType.UNKNOWN)
    
    def import_file(
        self, 
        file_path: Union[str, Path], 
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        clean_text: bool = True
    ) -> ImportResult:
        """
        Import data from a single file.
        
        Args:
            file_path: Path to the file
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            clean_text: Whether to clean the text
            
        Returns:
            ImportResult object
        """
        path = Path(file_path)
        
        if not path.exists():
            return ImportResult(
                status=ImportStatus.FAILED,
                file_path=str(path),
                errors=[f"File not found: {path}"]
            )
        
        file_type = self.get_file_type(path)
        
        if file_type == FileType.UNKNOWN:
            return ImportResult(
                status=ImportStatus.SKIPPED,
                file_path=str(path),
                warnings=[f"Unsupported file type: {path.suffix}"]
            )
        
        try:
            logger.info(f"Importing {file_type.value} file: {path}")
            
            if file_type in [FileType.TEXT, FileType.MARKDOWN]:
                return self._import_text_file(path, chunk_size, chunk_overlap, clean_text)
            elif file_type == FileType.JSON:
                return self._import_json_file(path, clean_text)
            elif file_type == FileType.CSV:
                return self._import_csv_file(path, clean_text)
            else:
                return ImportResult(
                    status=ImportStatus.FAILED,
                    file_path=str(path),
                    errors=[f"Import method not implemented for {file_type.value}"]
                )
                
        except Exception as e:
            logger.error(f"Import failed for {path}: {e}")
            return ImportResult(
                status=ImportStatus.FAILED,
                file_path=str(path),
                errors=[str(e)]
            )
    
    def _import_text_file(
        self, 
        path: Path, 
        chunk_size: int, 
        chunk_overlap: int, 
        clean_text: bool
    ) -> ImportResult:
        """Import text or markdown file."""
        try:
            # Read file with encoding detection
            content, encoding = self.encoding_detector.read_file_with_fallback(path)
            
            if clean_text:
                content = self.text_processor.clean_text(content)
            
            # Split into chunks
            chunks = self.text_processor.split_into_chunks(
                content, chunk_size, chunk_overlap
            )
            
            # Extract metadata
            base_metadata = self.text_processor.extract_metadata_from_filename(path)
            base_metadata.update({
                'encoding': encoding,
                'language': self.text_processor.detect_language(content),
                'original_length': len(content),
                'chunk_count': len(chunks)
            })
            
            # Create processed text objects
            processed_texts = []
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    chunk_metadata = base_metadata.copy()
                    chunk_metadata.update({
                        'chunk_index': i,
                        'chunk_length': len(chunk)
                    })
                    
                    processed_text = ProcessedText(
                        text=chunk,
                        original_text=content,
                        metadata=chunk_metadata,
                        chunk_index=i,
                        total_chunks=len(chunks)
                    )
                    processed_texts.append(processed_text)
            
            return ImportResult(
                status=ImportStatus.SUCCESS,
                file_path=str(path),
                items_imported=len(processed_texts),
                metadata={
                    'encoding': encoding,
                    'file_type': 'text',
                    'chunk_count': len(chunks),
                    'processed_texts': processed_texts
                }
            )
            
        except Exception as e:
            return ImportResult(
                status=ImportStatus.FAILED,
                file_path=str(path),
                errors=[f"Text import error: {e}"]
            )
    
    def _import_json_file(self, path: Path, clean_text: bool) -> ImportResult:
        """Import JSON file."""
        try:
            content, encoding = self.encoding_detector.read_file_with_fallback(path)
            data = json.loads(content)
            
            processed_texts = []
            
            def process_json_item(item, prefix=""):
                """Recursively process JSON items."""
                if isinstance(item, dict):
                    text_fields = ['text', 'content', 'description', 'body', 'message', 'title']
                    for field in text_fields:
                        if field in item and isinstance(item[field], str):
                            text = item[field]
                            if clean_text:
                                text = self.text_processor.clean_text(text)
                            
                            if text.strip():
                                metadata = self.text_processor.extract_metadata_from_filename(path)
                                metadata.update({
                                    'json_field': field,
                                    'json_path': prefix,
                                    'additional_fields': {k: v for k, v in item.items() if k != field}
                                })
                                
                                processed_texts.append(ProcessedText(
                                    text=text,
                                    original_text=text,
                                    metadata=metadata
                                ))
                            break
                
                elif isinstance(item, list):
                    for i, sub_item in enumerate(item):
                        process_json_item(sub_item, f"{prefix}[{i}]")
                
                elif isinstance(item, str) and item.strip():
                    text = item
                    if clean_text:
                        text = self.text_processor.clean_text(text)
                    
                    if text.strip():
                        metadata = self.text_processor.extract_metadata_from_filename(path)
                        metadata.update({'json_path': prefix})
                        
                        processed_texts.append(ProcessedText(
                            text=text,
                            original_text=text,
                            metadata=metadata
                        ))
            
            process_json_item(data)
            
            return ImportResult(
                status=ImportStatus.SUCCESS,
                file_path=str(path),
                items_imported=len(processed_texts),
                metadata={
                    'encoding': encoding,
                    'file_type': 'json',
                    'processed_texts': processed_texts
                }
            )
            
        except json.JSONDecodeError as e:
            return ImportResult(
                status=ImportStatus.FAILED,
                file_path=str(path),
                errors=[f"Invalid JSON: {e}"]
            )
        except Exception as e:
            return ImportResult(
                status=ImportStatus.FAILED,
                file_path=str(path),
                errors=[f"JSON import error: {e}"]
            )
    
    def _import_csv_file(self, path: Path, clean_text: bool) -> ImportResult:
        """Import CSV file."""
        try:
            content, encoding = self.encoding_detector.read_file_with_fallback(path)
            
            # Auto-detect delimiter
            sample = content[:1024]
            delimiter = ','
            if ';' in sample and sample.count(';') > sample.count(','):
                delimiter = ';'
            elif '\t' in sample:
                delimiter = '\t'
            
            processed_texts = []
            
            # Use StringIO to handle the content
            from io import StringIO
            csv_reader = csv.DictReader(StringIO(content), delimiter=delimiter)
            
            for row_num, row in enumerate(csv_reader, 1):
                # Find text columns
                text_columns = ['text', 'content', 'description', 'body', 'message', 'question', 'answer']
                
                text_found = False
                for col in text_columns:
                    if col in row and row[col] and row[col].strip():
                        text = row[col].strip()
                        if clean_text:
                            text = self.text_processor.clean_text(text)
                        
                        if text:
                            metadata = self.text_processor.extract_metadata_from_filename(path)
                            metadata.update({
                                'csv_row': row_num,
                                'csv_column': col,
                                'additional_columns': {k: v for k, v in row.items() if k != col}
                            })
                            
                            processed_texts.append(ProcessedText(
                                text=text,
                                original_text=row[col],
                                metadata=metadata
                            ))
                            text_found = True
                            break
                
                # If no standard text column found, use first non-empty column
                if not text_found:
                    for col, value in row.items():
                        if value and len(str(value).strip()) > 10:  # Meaningful text
                            text = str(value).strip()
                            if clean_text:
                                text = self.text_processor.clean_text(text)
                            
                            if text:
                                metadata = self.text_processor.extract_metadata_from_filename(path)
                                metadata.update({
                                    'csv_row': row_num,
                                    'csv_column': col,
                                    'additional_columns': {k: v for k, v in row.items() if k != col}
                                })
                                
                                processed_texts.append(ProcessedText(
                                    text=text,
                                    original_text=value,
                                    metadata=metadata
                                ))
                                break
            
            return ImportResult(
                status=ImportStatus.SUCCESS,
                file_path=str(path),
                items_imported=len(processed_texts),
                metadata={
                    'encoding': encoding,
                    'file_type': 'csv',
                    'delimiter': delimiter,
                    'processed_texts': processed_texts
                }
            )
            
        except Exception as e:
            return ImportResult(
                status=ImportStatus.FAILED,
                file_path=str(path),
                errors=[f"CSV import error: {e}"]
            )
    
    def import_directory(
        self, 
        directory_path: Union[str, Path], 
        recursive: bool = True,
        file_pattern: str = "*",
        **import_kwargs
    ) -> List[ImportResult]:
        """
        Import all supported files from a directory.
        
        Args:
            directory_path: Path to directory
            recursive: Whether to search recursively
            file_pattern: File pattern to match
            **import_kwargs: Arguments passed to import_file
            
        Returns:
            List of ImportResult objects
        """
        path = Path(directory_path)
        
        if not path.exists() or not path.is_dir():
            return [ImportResult(
                status=ImportStatus.FAILED,
                file_path=str(path),
                errors=[f"Directory not found: {path}"]
            )]
        
        results = []
        pattern = "**/" + file_pattern if recursive else file_pattern
        
        for file_path in path.glob(pattern):
            if file_path.is_file() and self.get_file_type(file_path) != FileType.UNKNOWN:
                result = self.import_file(file_path, **import_kwargs)
                results.append(result)
        
        logger.info(f"Imported {len(results)} files from {path}")
        return results
    
    def get_supported_formats(self) -> Dict[str, str]:
        """Get supported file formats."""
        return {
            '.txt': 'Plain text files',
            '.md': 'Markdown files',
            '.json': 'JSON data files',
            '.csv': 'Comma-separated values'
        }


def create_data_importer(text_processor: Optional[TextProcessor] = None) -> DataImporter:
    """Factory function to create a data importer."""
    return DataImporter(text_processor)


# Example usage and testing
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(level=logging.INFO)
    
    # Create data importer
    importer = create_data_importer()
    
    print("📁 Data Manager - Advanced Import System")
    print("=" * 50)
    
    # Show supported formats
    print("\nSupported file formats:")
    for ext, desc in importer.get_supported_formats().items():
        print(f"  {ext} - {desc}")
    
    # Test with sample files if they exist
    test_files = ["thai_text.txt", "test.csv"]
    
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"\n🔄 Testing with {test_file}...")
            result = importer.import_file(test_file)
            print(f"Result: {result}")
            
            if result.success:
                processed_texts = result.metadata.get('processed_texts', [])
                print(f"Imported {len(processed_texts)} text items")
                
                if processed_texts:
                    sample = processed_texts[0]
                    print(f"Sample: {sample.text[:100]}...")
    
    print("\n✅ Data Manager testing completed")
