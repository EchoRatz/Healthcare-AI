#!/usr/bin/env python3
"""
Simple test script to verify MCP connection works.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_mcp_connection():
    """Test MCP connection with the corrected format."""
    try:
        print("Testing MCP connection...")
        
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
            
            # List resources
            resources = connector.list_resources()
            print(f"Available resources: {resources}")
            
            # Test a specific call
            test_request = [{
                'endpoint': 'tools/call',
                'params': {
                    'name': 'list_all_departments',
                    'arguments': {}
                }
            }]
            
            result = connector.fetch(test_request)
            print(f"Test call result: {result}")
            
        return True
        
    except Exception as e:
        print(f"Error testing MCP connection: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("MCP CONNECTION TEST")
    print("=" * 60)
    
    success = test_mcp_connection()
    
    print("\n" + "=" * 60)
    print("TEST RESULT")
    print("=" * 60)
    print(f"MCP Connection: {'✅ PASS' if success else '❌ FAIL'}")
    print("=" * 60) 