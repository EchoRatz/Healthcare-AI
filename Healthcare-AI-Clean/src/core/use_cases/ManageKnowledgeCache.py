"""Use case for managing knowledge cache."""
from typing import Dict, Any, List
from ..services.CacheManager import CacheManager
from ...domain.services.ExtractionService import ExtractionService


class ManageKnowledgeCache:
    """Use case for cache management operations."""
    
    def __init__(self, cache_manager: CacheManager, extraction_service: ExtractionService):
        self.cache_manager = cache_manager
        self.extraction_service = extraction_service
    
    def extract_and_cache(self, question: str, answer: str) -> bool:
        """Extract knowledge from Q&A and cache it."""
        try:
            extraction_data = self.extraction_service.extract_information(question, answer)
            
            if extraction_data:
                self.cache_manager.add_extracted_information(extraction_data)
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error in knowledge extraction: {e}")
            return False
    
    def search_cache(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search cached knowledge."""
        entries = self.cache_manager.search_knowledge(query, top_k)
        return [entry.to_dict() for entry in entries]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache_manager.get_cache_summary()
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self.cache_manager.clear_all_cache()
        print("🗑️ Cache cleared successfully")
    
    def export_cache(self, filename: str) -> bool:
        """Export cache to text file."""
        try:
            entries = self.cache_manager.cache_repository.load_cache_entries()
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("📚 Healthcare AI Knowledge Cache Export\n")
                f.write("=" * 50 + "\n\n")
                
                for entry in entries:
                    f.write(f"🏷️ Type: {entry.fact_type}\n")
                    f.write(f"🔑 Key: {entry.key}\n")
                    f.write(f"💡 Value: {entry.value}\n")
                    if entry.context:
                        f.write(f"📝 Context: {entry.context}\n")
                    f.write(f"📅 Timestamp: {entry.timestamp}\n")
                    f.write("-" * 30 + "\n\n")
            
            print(f"📄 Cache exported to: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting cache: {e}")
            return False