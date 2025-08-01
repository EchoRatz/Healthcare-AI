"""Integration tests for cache operations."""
import pytest
import tempfile
import os
from src.infrastructure.repositories.JsonCache import JsonCacheRepository
from src.core.services.CacheManager import CacheManager
from src.domain.entities.CacheEntry import CacheEntry
from datetime import datetime


class TestCacheOperations:
    """Test cache operations integration."""
    
    def setup_method(self):
        """Setup test components."""
        # Create temporary cache file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.close()
        
        self.cache_repo = JsonCacheRepository(self.temp_file.name)
        self.cache_manager = CacheManager(self.cache_repo)
    
    def teardown_method(self):
        """Cleanup test components."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_cache_lifecycle(self):
        """Test complete cache lifecycle."""
        # Create test entry
        entry = CacheEntry(
            id="test1",
            fact_type="medication",
            key="Test Medicine",
            value="Test Value",
            timestamp=datetime.now(),
            relevance_score=8.0
        )
        
        # Save entry
        self.cache_repo.save_cache_entry(entry)
        
        # Load entries
        entries = self.cache_repo.load_cache_entries()
        assert len(entries) == 1
        assert entries[0].id == "test1"
        assert entries[0].key == "Test Medicine"
        
        # Search cache
        search_results = self.cache_repo.search_cache("medicine", top_k=5)
        assert len(search_results) >= 1
        
        # Get stats
        stats = self.cache_repo.get_cache_stats()
        assert stats["total_entries"] == 1
        
        # Clear cache
        self.cache_repo.clear_cache()
        empty_entries = self.cache_repo.load_cache_entries()
        assert len(empty_entries) == 0
    
    def test_cache_manager_integration(self):
        """Test cache manager with extraction data."""
        extraction_data = {
            "facts": [
                {
                    "type": "medication",
                    "key": "Aspirin",
                    "value": "100 baht per bottle",
                    "context": "For headache treatment"
                }
            ],
            "relevance_score": 7
        }
        
        # Add extracted information
        self.cache_manager.add_extracted_information(extraction_data)
        
        # Search knowledge
        results = self.cache_manager.search_knowledge("aspirin", top_k=3)
        assert len(results) >= 1
        
        # Get summary
        summary = self.cache_manager.get_cache_summary()
        assert summary["total_entries"] >= 1