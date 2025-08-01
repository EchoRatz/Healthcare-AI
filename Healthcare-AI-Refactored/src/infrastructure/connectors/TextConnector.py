"""Text connector implementation for reading plain text files."""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from core.interfaces.DataConnectorInterface import DataConnectorInterface
from shared.logging.LoggerMixin import LoggerMixin


class TextConnector(DataConnectorInterface, LoggerMixin):
    """Text connector implementation for reading plain text files."""
    
    def __init__(self, base_path: str = "data/documents"):
        super().__init__()
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def fetch(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Fetch text from files based on requests.
        
        Args:
            requests: List of request dictionaries with 'file' and optional 'line_range' keys
            
        Returns:
            Dictionary containing extracted text organized by file
        """
        try:
            results = {}
            
            for req in requests:
                file_path = req.get('file')
                line_range = req.get('line_range', None)  # (start_line, end_line) or None for all
                
                if not file_path:
                    self.logger.warning(f"Skipping request without file path: {req}")
                    continue
                
                # Resolve file path
                full_path = self.base_path / file_path
                
                if not full_path.exists():
                    self.logger.error(f"Text file not found: {full_path}")
                    results[file_path] = {
                        'error': f"File not found: {file_path}",
                        'text': None
                    }
                    continue
                
                try:
                    text = self._read_text(full_path, line_range)
                    results[file_path] = {
                        'text': text,
                        'error': None,
                        'line_range': line_range if line_range else 'all'
                    }
                    
                except Exception as e:
                    self.logger.error(f"Failed to read text from {file_path}: {e}")
                    results[file_path] = {
                        'error': str(e),
                        'text': None
                    }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to fetch text data: {e}")
            return {'error': str(e)}
    
    def _read_text(self, file_path: Path, line_range: Optional[tuple]) -> str:
        """Read text from file with optional line range filtering."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
                if line_range:
                    start_line, end_line = line_range
                    # Convert to 0-based indexing and handle bounds
                    start_idx = max(0, start_line - 1)
                    end_idx = min(len(lines), end_line)
                    lines = lines[start_idx:end_idx]
                
                return ''.join(lines)
                
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    lines = file.readlines()
                    
                    if line_range:
                        start_line, end_line = line_range
                        start_idx = max(0, start_line - 1)
                        end_idx = min(len(lines), end_line)
                        lines = lines[start_idx:end_idx]
                    
                    return ''.join(lines)
            except Exception as e:
                raise Exception(f"Failed to read file with multiple encodings: {e}")
    
    def is_available(self) -> bool:
        """Check if text processing is available."""
        return True  # No external dependencies
    
    def get_connector_info(self) -> Dict[str, Any]:
        """Get information about the text connector."""
        return {
            'type': 'text',
            'base_path': str(self.base_path),
            'available': self.is_available(),
            'supported_extensions': ['.txt', '.md', '.csv', '.json', '.yaml', '.yml']
        }
    
    def list_available_files(self, extensions: Optional[List[str]] = None) -> List[str]:
        """List available text files in the base directory."""
        try:
            if extensions is None:
                extensions = ['.txt', '.md', '.csv', '.json', '.yaml', '.yml']
            
            text_files = []
            for file_path in self.base_path.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in extensions:
                    relative_path = file_path.relative_to(self.base_path)
                    text_files.append(str(relative_path))
            
            return text_files
            
        except Exception as e:
            self.logger.error(f"Failed to list text files: {e}")
            return []
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific text file."""
        try:
            full_path = self.base_path / file_path
            
            if not full_path.exists():
                return None
            
            stat = full_path.stat()
            
            # Count lines
            try:
                with open(full_path, 'r', encoding='utf-8') as file:
                    line_count = sum(1 for _ in file)
            except UnicodeDecodeError:
                with open(full_path, 'r', encoding='latin-1') as file:
                    line_count = sum(1 for _ in file)
            
            return {
                'file_path': file_path,
                'file_size': stat.st_size,
                'line_count': line_count,
                'available': True
            }
                
        except Exception as e:
            self.logger.error(f"Failed to get file info for {file_path}: {e}")
            return None
    
    def search_in_file(self, file_path: str, search_term: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """Search for a term in a specific text file."""
        try:
            full_path = self.base_path / file_path
            
            if not full_path.exists():
                return []
            
            matches = []
            search_term_lower = search_term.lower() if not case_sensitive else search_term
            
            with open(full_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    line_to_search = line.lower() if not case_sensitive else line
                    if search_term_lower in line_to_search:
                        matches.append({
                            'line_number': line_num,
                            'line_content': line.strip(),
                            'match_position': line_to_search.find(search_term_lower)
                        })
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Failed to search in file {file_path}: {e}")
            return [] 