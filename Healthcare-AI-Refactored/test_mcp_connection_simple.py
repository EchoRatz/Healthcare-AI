#!/usr/bin/env python3
"""
Simple MCP Connection Test
==========================

Test basic MCP connection with correct URL and format
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_simple_connection():
    """Test simple MCP connection"""
    try:
        print("🔧 Testing simple MCP connection...")
        
        from src.infrastructure.connectors.MCPConnector import MCPConnector
        
        # Create connector with correct base URL
        connector = MCPConnector("https://mcp-hackathon.cmkl.ai")
        
        print(f"Server URL: {connector.server_url}")
        
        # Test availability
        available = connector.is_available()
        print(f"MCP server available: {available}")
        
        if available:
            # Test listing resources
            resources = connector.list_resources()
            print(f"Available resources: {resources[:5]}...")
            
            # Test a simple tool call
            test_request = [{
                'endpoint': 'list_all_departments',
                'params': {
                    'name': 'list_all_departments',
                    'arguments': {},
                    'query': 'Test query'
                }
            }]
            
            result = connector.fetch(test_request)
            print(f"Tool call result: {result}")
            
            return True
        else:
            print("❌ MCP server not available")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_request():
    """Test direct request to MCP server"""
    try:
        print("\n🔧 Testing direct request...")
        
        import requests
        
        # Test the exact format from working examples
        url = "https://mcp-hackathon.cmkl.ai/message"
        
        # Initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "clientInfo": {
                    "name": "healthcare-test-client",
                    "version": "1.0.0"
                },
                "capabilities": {
                    "tools": {"listChanged": True}
                }
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        print(f"Sending request to: {url}")
        print(f"Request: {json.dumps(init_request, indent=2)}")
        
        response = requests.post(url, json=init_request, headers=headers, timeout=10)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response text: {response.text[:500]}...")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response JSON: {json.dumps(data, indent=2)}")
                return True
            except json.JSONDecodeError:
                print("Response is not valid JSON")
                return False
        else:
            print(f"HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Direct request error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("SIMPLE MCP CONNECTION TEST")
    print("=" * 60)
    print("Testing basic MCP connection with correct URL")
    print()
    
    # Test simple connection
    print("Testing MCPConnector...")
    success1 = test_simple_connection()
    
    # Test direct request
    print("\nTesting direct request...")
    success2 = test_direct_request()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"MCPConnector: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Direct Request: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("🎉 Both tests passed! MCP connection is working.")
    elif success1 or success2:
        print("⚠️  One test passed. MCP connection partially working.")
    else:
        print("❌ Both tests failed. MCP connection needs attention.")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 