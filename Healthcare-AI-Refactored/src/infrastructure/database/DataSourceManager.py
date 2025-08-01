"""Data source manager for Healthcare AI."""

import os
from pathlib import Path
from typing import List, Dict, Optional
from shared.logging.LoggerMixin import get_logger
from core.entities.Document import Document


class DataSourceManager:
    """Manages data sources for the Healthcare AI system."""
    
    def __init__(self, data_sources_path: str = "src/infrastructure/data_sources"):
        self.data_sources_path = Path(data_sources_path)
        self.logger = get_logger(__name__)
        self.sources = {
            'results_doc': 'results_doc/direct_extraction_corrected.txt',
            'results_doc2': 'results_doc2/direct_extraction_corrected.txt', 
            'results_doc3': 'results_doc3/direct_extraction_corrected.txt',
            'hospital_micro_facts': 'hospital_micro_facts/hospital_micro_facts.txt'
        }
    
    def get_available_sources(self) -> List[str]:
        """Get list of available data sources."""
        available = []
        for source_name, file_path in self.sources.items():
            full_path = self.data_sources_path / file_path
            if full_path.exists():
                available.append(source_name)
            else:
                self.logger.warning(f"Data source not found: {full_path}")
        return available
    
    def load_source(self, source_name: str) -> Optional[Document]:
        """Load a specific data source."""
        if source_name not in self.sources:
            self.logger.error(f"Unknown data source: {source_name}")
            return None
        
        file_path = self.data_sources_path / self.sources[source_name]
        
        if not file_path.exists():
            self.logger.error(f"Data source file not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            document = Document(
                id=source_name,
                content=content,
                metadata={
                    'source': source_name,
                    'file_path': str(file_path),
                    'size': len(content),
                    'type': 'healthcare_knowledge'
                }
            )
            
            self.logger.info(f"Loaded data source: {source_name} ({len(content):,} chars)")
            return document
            
        except Exception as e:
            self.logger.error(f"Failed to load data source {source_name}: {e}")
            return None
    
    def load_all_sources(self) -> List[Document]:
        """Load all available data sources."""
        documents = []
        available_sources = self.get_available_sources()
        
        for source_name in available_sources:
            document = self.load_source(source_name)
            if document:
                documents.append(document)
        
        self.logger.info(f"Loaded {len(documents)} data sources")
        return documents
    
    def get_source_info(self) -> Dict[str, Dict]:
        """Get information about all data sources."""
        info = {}
        
        for source_name, file_path in self.sources.items():
            full_path = self.data_sources_path / file_path
            source_info = {
                'exists': full_path.exists(),
                'path': str(full_path),
                'size': full_path.stat().st_size if full_path.exists() else 0
            }
            info[source_name] = source_info
        
        return info 