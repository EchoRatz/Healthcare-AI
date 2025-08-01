#!/usr/bin/env python3
"""
Debug MCP Connection
===================

Debug the HTTP 406 error and find the correct connection method
"""

import requests
import json

def test_different_headers():
    """Test with different header combinations"""
    print("🔍 Testing Different Header Combinations")
    print("=" * 45)
    
    base_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "lookup_patient",
            "arguments": {
                "patient_id": "test"
            }
        }
    }
    
    # Different header combinations to try
    header_sets = [
        {
            "name": "Standard JSON",
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        },
        {
            "name": "MCP Specific",
            "headers": {
                "Content-Type": "application/json",
                "Accept": "text/event-stream"
            }
        },
        {
            "name": "With User-Agent",
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "MCP-Healthcare-Client/1.0"
            }
        },
        {
            "name": "SSE Headers",
            "headers": {
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        },
        {
            "name": "Minimal Headers",
            "headers": {
                "Content-Type": "application/json"
            }
        },
        {
            "name": "Different Accept",
            "headers": {
                "Content-Type": "application/json",
                "Accept": "*/*"
            }
        }
    ]
    
    url = "https://mcp-hackathon.cmkl.ai/mcp"
    
    for header_set in header_sets:
        print(f"\n📋 Testing: {header_set['name']}")
        
        try:
            response = requests.post(url, json=base_request, headers=header_set['headers'], timeout=10)
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ SUCCESS!")
                try:
                    data = response.json()
                    print(f"  Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"  Response: {response.text[:200]}...")
                return header_set['headers']
                
            elif response.status_code == 406:
                print(f"  ❌ Not Acceptable - server wants different format")
                
            else:
                print(f"  ❌ HTTP {response.status_code}")
                print(f"  Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:50]}...")
    
    return None

def test_initialization_first():
    """Test if we need to initialize first"""
    print("\n🔧 Testing MCP Initialization Sequence")
    print("=" * 40)
    
    url = "https://mcp-hackathon.cmkl.ai/mcp"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    
    # Step 1: Try to initialize
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "clientInfo": {
                "name": "healthcare-test-client",
                "version": "1.0.0"
            },
            "capabilities": {}
        }
    }
    
    print("📋 Step 1: Initialize connection")
    try:
        response = requests.post(url, json=init_request, headers=headers, timeout=10)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            print("  ✅ Initialization successful!")
            data = response.json()
            print(f"  Response: {json.dumps(data, indent=2)[:300]}...")
            
            # Step 2: Try tools/list
            print("\n📋 Step 2: List tools")
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
            
            response2 = requests.post(url, json=tools_request, headers=headers, timeout=10)
            print(f"  Status: {response2.status_code}")
            
            if response2.status_code == 200:
                data2 = response2.json()
                print(f"  ✅ Tools list successful!")
                print(f"  Response: {json.dumps(data2, indent=2)[:300]}...")
                
                # Step 3: Try tool call
                print("\n📋 Step 3: Call lookup_patient")
                call_request = {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "lookup_patient",
                        "arguments": {
                            "patient_id": "test_patient"
                        }
                    }
                }
                
                response3 = requests.post(url, json=call_request, headers=headers, timeout=10)
                print(f"  Status: {response3.status_code}")
                
                if response3.status_code == 200:
                    data3 = response3.json()
                    print(f"  ✅ Tool call successful!")
                    print(f"  Response: {json.dumps(data3, indent=2)[:300]}...")
                else:
                    print(f"  ❌ Tool call failed: {response3.text[:100]}...")
            else:
                print(f"  ❌ Tools list failed: {response2.text[:100]}...")
        else:
            print(f"  ❌ Initialization failed: {response.text[:100]}...")
            
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:50]}...")

def test_session_based():
    """Test if we need session-based requests"""
    print("\n🔗 Testing Session-Based Requests")
    print("=" * 35)
    
    url = "https://mcp-hackathon.cmkl.ai/mcp"
    
    # Try with a session to maintain cookies/state
    with requests.Session() as session:
        session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        print("📋 Using persistent session")
        
        # Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
                "capabilities": {}
            }
        }
        
        try:
            response = session.post(url, json=init_request, timeout=10)
            print(f"  Init Status: {response.status_code}")
            
            if response.status_code == 200:
                # Try tool call with same session
                call_request = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "lookup_patient",
                        "arguments": {"patient_id": "test"}
                    }
                }
                
                response2 = session.post(url, json=call_request, timeout=10)
                print(f"  Call Status: {response2.status_code}")
                
                if response2.status_code == 200:
                    print("  ✅ Session-based requests work!")
                    return True
                else:
                    print(f"  ❌ Call failed: {response2.text[:100]}...")
            else:
                print(f"  ❌ Init failed: {response.text[:100]}...")
                
        except Exception as e:
            print(f"  ❌ Session error: {str(e)[:50]}...")
    
    return False

def main():
    """Main debug function"""
    print("🐛 MCP Connection Debug Suite")
    print("=" * 35)
    print("Debugging HTTP 406 errors from CMKL MCP server")
    print()
    
    # Test 1: Different headers
    working_headers = test_different_headers()
    
    if working_headers:
        print(f"\n✅ Found working headers: {working_headers}")
    else:
        print(f"\n❌ No working headers found")
    
    # Test 2: Initialization sequence
    test_initialization_first()
    
    # Test 3: Session-based
    session_works = test_session_based()
    
    print(f"\n📊 Debug Summary:")
    print(f"  Working headers: {'Yes' if working_headers else 'No'}")
    print(f"  Session required: {'Yes' if session_works else 'Unknown'}")
    
    print(f"\n💡 Recommendations:")
    print(f"  1. Test these findings in Postman")
    print(f"  2. Check if authentication/API key is required")
    print(f"  3. Try GET request to server root for docs")
    print(f"  4. Contact CMKL team for API documentation")
    
    print(f"\n🔧 For Postman Testing:")
    print(f"  URL: https://mcp-hackathon.cmkl.ai/mcp")
    print(f"  Method: POST") 
    if working_headers:
        print(f"  Headers: {json.dumps(working_headers, indent=4)}")
    else:
        print(f"  Headers: Try text/event-stream for Accept")

if __name__ == "__main__":
    main()