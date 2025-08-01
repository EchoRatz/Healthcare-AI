#!/usr/bin/env python3
"""
Find Working MCP Endpoint
========================

Quick test to find the correct endpoint for the CMKL MCP server
"""

import requests
import json

def test_endpoints():
    """Test different endpoint combinations"""
    print("🔍 Finding Working MCP Endpoint")
    print("=" * 35)
    
    base_url = "https://mcp-hackathon.cmkl.ai"
    
    # Test different endpoints
    endpoints = ["/message", "/mcp", "/api/mcp", "/tools", "/rpc", "/jsonrpc", "/", "/api"]
    
    # Simple test request
    test_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    working_endpoints = []
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n📡 Testing: {url}")
        
        try:
            response = requests.post(url, json=test_request, headers=headers, timeout=10)
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ SUCCESS!")
                try:
                    data = response.json()
                    print(f"  Response: {json.dumps(data, indent=2)[:200]}...")
                    working_endpoints.append((endpoint, "200 OK"))
                except:
                    print(f"  Response: {response.text[:100]}...")
                    working_endpoints.append((endpoint, "200 Non-JSON"))
                    
            elif response.status_code == 406:
                print(f"  🔶 Not Acceptable (server responding but needs different format)")
                working_endpoints.append((endpoint, "406 Needs Format"))
                
            elif response.status_code == 404:
                print(f"  ❌ Not Found")
                
            else:
                print(f"  ⚠️  HTTP {response.status_code}")
                try:
                    data = response.json()
                    if "jsonrpc" in data:
                        print(f"  📡 JSON-RPC response detected")
                        working_endpoints.append((endpoint, f"{response.status_code} JSON-RPC"))
                except:
                    pass
                    
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Connection error: {str(e)[:50]}...")
    
    print(f"\n📊 Results Summary:")
    if working_endpoints:
        print(f"  Found {len(working_endpoints)} responsive endpoints:")
        for endpoint, status in working_endpoints:
            print(f"    {endpoint} → {status}")
        
        # Return the best endpoint
        for endpoint, status in working_endpoints:
            if "200" in status:
                return endpoint
        for endpoint, status in working_endpoints:
            if "406" in status:
                return endpoint  # 406 means it responds but needs different format
                
    else:
        print(f"  ❌ No responsive endpoints found")
    
    return None

def test_with_session_id(endpoint):
    """Test the endpoint with session ID"""
    if not endpoint:
        return
        
    print(f"\n🔧 Testing {endpoint} with Session ID")
    print("-" * 40)
    
    url = f"https://mcp-hackathon.cmkl.ai{endpoint}"
    
    # Try with session ID in request body
    request_with_session = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "session_id": "healthcare_test_123"
    }
    
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    
    try:
        response = requests.post(url, json=request_with_session, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS with session ID!")
            print(f"Response: {json.dumps(data, indent=2)[:300]}...")
            return True
        else:
            response_text = response.text[:200]
            print(f"Response: {response_text}")
            
            # Check if it's asking for different session format
            if "session" in response_text.lower():
                print(f"💡 Server mentions session - might need different session format")
                
    except Exception as e:
        print(f"Error: {e}")
    
    return False

def main():
    print("🌐 MCP Endpoint Discovery")
    print("=" * 30)
    
    # Find working endpoint
    working_endpoint = test_endpoints()
    
    if working_endpoint:
        print(f"\n🎯 Best endpoint found: {working_endpoint}")
        
        # Test with session ID
        success = test_with_session_id(working_endpoint)
        
        if success:
            print(f"\n✅ MCP server is accessible!")
            print(f"📋 Use this configuration:")
            print(f"  URL: https://mcp-hackathon.cmkl.ai{working_endpoint}")
            print(f"  Method: POST")
            print(f"  Headers: Content-Type: application/json")
            print(f"  Body: Include session_id in request")
        else:
            print(f"\n🔶 Server responds but needs proper authentication/format")
            
    else:
        print(f"\n❌ Could not find working endpoint")
        print(f"💡 Try manual testing in Postman with different endpoints")

if __name__ == "__main__":
    main()