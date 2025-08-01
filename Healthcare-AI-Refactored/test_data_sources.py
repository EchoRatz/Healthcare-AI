"""Test script to verify data source integration."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from infrastructure.database.DataSourceManager import DataSourceManager


def test_data_sources():
    """Test data source integration."""
    print("🧪 Testing Data Source Integration")
    print("=" * 50)
    
    # Initialize data source manager
    data_source_manager = DataSourceManager()
    
    # Get available sources
    available_sources = data_source_manager.get_available_sources()
    print(f"📋 Available data sources: {available_sources}")
    
    # Get source information
    source_info = data_source_manager.get_source_info()
    print("\n📊 Source Information:")
    for source_name, info in source_info.items():
        status = "✅" if info['exists'] else "❌"
        size_mb = info['size'] / (1024 * 1024) if info['size'] > 0 else 0
        print(f"  {status} {source_name}: {size_mb:.2f} MB")
    
    # Test loading hospital_micro_facts specifically
    print("\n🏥 Testing hospital_micro_facts integration:")
    hospital_doc = data_source_manager.load_source('hospital_micro_facts')
    
    if hospital_doc:
        print(f"  ✅ Successfully loaded hospital_micro_facts")
        print(f"  📄 Content length: {len(hospital_doc.content):,} characters")
        print(f"  🏷️  Document ID: {hospital_doc.id}")
        print(f"  📋 Metadata: {hospital_doc.metadata}")
        
        # Show a sample of the content
        sample = hospital_doc.content[:200] + "..." if len(hospital_doc.content) > 200 else hospital_doc.content
        print(f"  📝 Sample content: {sample}")
    else:
        print("  ❌ Failed to load hospital_micro_facts")
    
    # Test loading all sources
    print("\n📚 Testing all data sources:")
    all_documents = data_source_manager.load_all_sources()
    print(f"  ✅ Loaded {len(all_documents)} documents")
    
    for doc in all_documents:
        print(f"    - {doc.id}: {len(doc.content):,} chars")


if __name__ == "__main__":
    test_data_sources() 