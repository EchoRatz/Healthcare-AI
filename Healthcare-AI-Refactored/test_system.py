#!/usr/bin/env python3
"""
Simple test script for the enhanced healthcare AI system.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_system():
    """Test the enhanced system with a simple query."""
    try:
        print("Testing enhanced healthcare AI system...")
        
        # Import the factory
        from infrastructure.factories.EnhancedSystemFactory import EnhancedSystemFactory
        
        # Create factory
        factory = EnhancedSystemFactory("config/enhanced_system.json")
        
        # Get system status
        status = factory.get_system_status()
        print("System status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # Create engine
        engine = factory.create_chain_of_thought_engine()
        
        # Test with a simple query
        test_query = "แผนกไหนที่ให้บริการโรคหัวใจ?"
        print(f"\nTesting with query: {test_query}")
        
        result = engine.process_query(test_query)
        
        print(f"\nResult: {result.get('answer', 'No answer')}")
        print(f"Processing time: {result.get('processing_time', 0):.2f} seconds")
        
        return True
        
    except Exception as e:
        print(f"Error testing system: {e}")
        return False

def test_text_connector():
    """Test the text connector with the new folders."""
    try:
        print("\nTesting text connector...")
        
        from infrastructure.connectors.TextConnector import TextConnector
        
        # Create connector with new configuration
        connector = TextConnector(
            base_path="src/infrastructure",
            text_folders=["results_doc", "results_doc2", "results_doc3"]
        )
        
        # List available files
        files = connector.list_available_files()
        print(f"Available files: {files}")
        
        # Test reading a file
        if files:
            test_file = files[0]
            print(f"Testing reading file: {test_file}")
            
            result = connector.fetch([{'file': test_file}])
            print(f"File content length: {len(str(result))}")
            
        return True
        
    except Exception as e:
        print(f"Error testing text connector: {e}")
        return False

def test_mcp_connector():
    """Test the MCP connector."""
    try:
        print("\nTesting MCP connector...")
        
        from infrastructure.connectors.MCPConnector import MCPConnector
        
        # Create connector
        connector = MCPConnector("https://mcp-hackathon.cmkl.ai/mcp")
        
        # Test availability
        available = connector.is_available()
        print(f"MCP connector available: {available}")
        
        if available:
            # Get connector info
            info = connector.get_connector_info()
            print(f"MCP connector info: {info}")
        
        return True
        
    except Exception as e:
        print(f"Error testing MCP connector: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("ENHANCED HEALTHCARE AI SYSTEM TEST")
    print("=" * 60)
    
    # Test text connector
    text_ok = test_text_connector()
    
    # Test MCP connector
    mcp_ok = test_mcp_connector()
    
    # Test full system
    system_ok = test_system()
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Text Connector: {'✅ PASS' if text_ok else '❌ FAIL'}")
    print(f"MCP Connector: {'✅ PASS' if mcp_ok else '❌ FAIL'}")
    print(f"Full System: {'✅ PASS' if system_ok else '❌ FAIL'}")
    print("=" * 60) 