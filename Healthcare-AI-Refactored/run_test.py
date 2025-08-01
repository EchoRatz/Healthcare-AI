#!/usr/bin/env python3
"""
Simple test script to run from the root directory.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_mcp():
    """Test MCP connection."""
    try:
        print("Testing MCP connection...")
        
        from src.infrastructure.connectors.MCPConnector import MCPConnector
        
        # Create connector
        connector = MCPConnector("https://mcp-hackathon.cmkl.ai/mcp")
        
        # Test availability
        available = connector.is_available()
        print(f"MCP connector available: {available}")
        
        if available:
            # Get connector info
            info = connector.get_connector_info()
            print(f"MCP connector info: {info}")
            
            # List resources
            resources = connector.list_resources()
            print(f"Available resources: {resources}")
            
        return True
        
    except Exception as e:
        print(f"Error testing MCP connection: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_healthcare_qa():
    """Test healthcare Q&A processing."""
    try:
        print("\nTesting healthcare Q&A processing...")
        
        from src.scripts.process_healthcare_qa import HealthcareQAProcessor
        
        # Create processor
        processor = HealthcareQAProcessor()
        
        # Test with just 2 questions
        processor.run(
            input_file="src/infrastructure/test.csv",
            output_file="test_output_small.csv",
            batch_size=1,
            max_questions=2
        )
        
        return True
        
    except Exception as e:
        print(f"Error testing healthcare Q&A: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("SIMPLE TEST SCRIPT")
    print("=" * 60)
    
    # Test MCP
    mcp_success = test_mcp()
    
    # Test healthcare Q&A
    qa_success = test_healthcare_qa()
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"MCP Connection: {'✅ PASS' if mcp_success else '❌ FAIL'}")
    print(f"Healthcare Q&A: {'✅ PASS' if qa_success else '❌ FAIL'}")
    print("=" * 60) 