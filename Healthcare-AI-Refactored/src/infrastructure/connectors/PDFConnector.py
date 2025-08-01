"""PDF connector implementation using PyPDF2."""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

from core.interfaces.DataConnectorInterface import DataConnectorInterface
from shared.logging.LoggerMixin import LoggerMixin


class PDFConnector(DataConnectorInterface, LoggerMixin):
    """PDF connector implementation using PyPDF2."""
    
    def __init__(self, base_path: str = "data/documents"):
        super().__init__()
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        if PdfReader is None:
            self.logger.warning("PyPDF2 not available. Install with: pip install PyPDF2")
    
    def fetch(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Fetch text from PDF files based on requests.
        
        Args:
            requests: List of request dictionaries with 'file' and optional 'pages' keys
            
        Returns:
            Dictionary containing extracted text organized by file
        """
        try:
            results = {}
            
            for req in requests:
                file_path = req.get('file')
                pages = req.get('pages', [])  # Empty list means all pages
                
                if not file_path:
                    self.logger.warning(f"Skipping request without file path: {req}")
                    continue
                
                # Resolve file path
                full_path = self.base_path / file_path
                
                if not full_path.exists():
                    self.logger.error(f"PDF file not found: {full_path}")
                    results[file_path] = {
                        'error': f"File not found: {file_path}",
                        'text': None
                    }
                    continue
                
                try:
                    text = self._extract_text(full_path, pages)
                    results[file_path] = {
                        'text': text,
                        'error': None,
                        'pages_extracted': len(pages) if pages else 'all'
                    }
                    
                except Exception as e:
                    self.logger.error(f"Failed to extract text from {file_path}: {e}")
                    results[file_path] = {
                        'error': str(e),
                        'text': None
                    }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to fetch PDF data: {e}")
            return {'error': str(e)}
    
    def _extract_text(self, file_path: Path, pages: List[int]) -> str:
        """Extract text from specific pages of a PDF file."""
        if PdfReader is None:
            raise ImportError("PyPDF2 is required for PDF processing")
        
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            
            if not pages:
                # Extract all pages
                text_parts = []
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text_parts.append(page.extract_text())
                return "\n\n".join(text_parts)
            else:
                # Extract specific pages
                text_parts = []
                for page_num in pages:
                    if 0 <= page_num < len(reader.pages):
                        page = reader.pages[page_num]
                        text_parts.append(page.extract_text())
                    else:
                        self.logger.warning(f"Page {page_num} not found in {file_path}")
                
                return "\n\n".join(text_parts)
    
    def is_available(self) -> bool:
        """Check if PDF processing is available."""
        return PdfReader is not None
    
    def get_connector_info(self) -> Dict[str, Any]:
        """Get information about the PDF connector."""
        return {
            'type': 'pdf',
            'base_path': str(self.base_path),
            'available': self.is_available(),
            'library': 'PyPDF2' if PdfReader else None
        }
    
    def list_available_files(self) -> List[str]:
        """List available PDF files in the base directory."""
        try:
            pdf_files = []
            for file_path in self.base_path.rglob("*.pdf"):
                relative_path = file_path.relative_to(self.base_path)
                pdf_files.append(str(relative_path))
            
            return pdf_files
            
        except Exception as e:
            self.logger.error(f"Failed to list PDF files: {e}")
            return []
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific PDF file."""
        try:
            full_path = self.base_path / file_path
            
            if not full_path.exists():
                return None
            
            if PdfReader is None:
                return {'error': 'PyPDF2 not available'}
            
            with open(full_path, 'rb') as file:
                reader = PdfReader(file)
                
                return {
                    'file_path': file_path,
                    'total_pages': len(reader.pages),
                    'file_size': full_path.stat().st_size,
                    'available': True
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get file info for {file_path}: {e}")
            return None 