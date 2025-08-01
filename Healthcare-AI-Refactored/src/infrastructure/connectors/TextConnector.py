"""Text connector implementation for reading plain text files."""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from core.interfaces.DataConnectorInterface import DataConnectorInterface
from shared.logging.LoggerMixin import LoggerMixin


class TextConnector(DataConnectorInterface, LoggerMixin):
    """Text connector implementation for reading plain text files."""
    
    def __init__(self, base_path: str = "data/documents", text_folders: Optional[List[str]] = None):
        super().__init__()
        self.base_path = Path(base_path)
        self.text_folders = text_folders or []
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
                folder = req.get('folder', None)  # Specific folder to search in
                
                if not file_path:
                    self.logger.warning(f"Skipping request without file path: {req}")
                    continue
                
                # Resolve file path - try multiple folders if specified
                full_path = None
                if folder:
                    # Search in specific folder
                    folder_path = self.base_path / folder
                    full_path = folder_path / file_path
                    if not full_path.exists():
                        self.logger.warning(f"File not found in {folder}: {full_path}")
                        full_path = None
                else:
                    # Search in base path first
                    full_path = self.base_path / file_path
                    if not full_path.exists():
                        # Search in text folders
                        for text_folder in self.text_folders:
                            folder_path = self.base_path / text_folder
                            test_path = folder_path / file_path
                            if test_path.exists():
                                full_path = test_path
                                self.logger.info(f"Found file in {text_folder}: {file_path}")
                                break
                
                if not full_path or not full_path.exists():
                    self.logger.error(f"Text file not found: {file_path}")
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
                        'line_range': line_range if line_range else 'all',
                        'source_folder': str(full_path.parent.name)
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
                raise Exception(f"Failed to read file with any encoding: {e}")
    
    def is_available(self) -> bool:
        """Check if text connector is available."""
        return self.base_path.exists()
    
    def get_connector_info(self) -> Dict[str, Any]:
        """Get connector information."""
        return {
            'type': 'text',
            'base_path': str(self.base_path),
            'text_folders': self.text_folders,
            'available_files': self.list_available_files()
        }
    
    def list_available_files(self, extensions: Optional[List[str]] = None) -> List[str]:
        """List all available text files in the base path and text folders."""
        files = []
        
        # List files in base path
        if self.base_path.exists():
            for file_path in self.base_path.rglob('*'):
                if file_path.is_file():
                    if extensions is None or file_path.suffix.lower() in extensions:
                        files.append(str(file_path.relative_to(self.base_path)))
        
        # List files in text folders
        for folder_name in self.text_folders:
            folder_path = self.base_path / folder_name
            if folder_path.exists():
                for file_path in folder_path.rglob('*'):
                    if file_path.is_file():
                        if extensions is None or file_path.suffix.lower() in extensions:
                            files.append(str(file_path.relative_to(self.base_path)))
        
        return sorted(list(set(files)))  # Remove duplicates
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific file."""
        try:
            # Try to find the file in base path or text folders
            full_path = None
            
            # Check base path first
            test_path = self.base_path / file_path
            if test_path.exists():
                full_path = test_path
            
            # Check text folders if not found
            if not full_path:
                for folder_name in self.text_folders:
                    folder_path = self.base_path / folder_name
                    test_path = folder_path / file_path
                    if test_path.exists():
                        full_path = test_path
                        break
            
            if not full_path or not full_path.exists():
                return None
            
            stat = full_path.stat()
            return {
                'file_path': file_path,
                'full_path': str(full_path),
                'size_bytes': stat.st_size,
                'modified_time': stat.st_mtime,
                'exists': True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get file info for {file_path}: {e}")
            return None
    
    def search_in_file(self, file_path: str, search_term: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """Search for a term in a specific file."""
        try:
            # Find the file
            full_path = None
            
            # Check base path first
            test_path = self.base_path / file_path
            if test_path.exists():
                full_path = test_path
            
            # Check text folders if not found
            if not full_path:
                for folder_name in self.text_folders:
                    folder_path = self.base_path / folder_name
                    test_path = folder_path / file_path
                    if test_path.exists():
                        full_path = test_path
                        break
            
            if not full_path or not full_path.exists():
                return []
            
            # Search in file
            matches = []
            with open(full_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    if not case_sensitive:
                        if search_term.lower() in line.lower():
                            matches.append({
                                'line_number': line_num,
                                'line_content': line.strip(),
                                'file_path': file_path
                            })
                    else:
                        if search_term in line:
                            matches.append({
                                'line_number': line_num,
                                'line_content': line.strip(),
                                'file_path': file_path
                            })
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Failed to search in file {file_path}: {e}")
            return [] 