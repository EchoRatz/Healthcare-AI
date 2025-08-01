#!/usr/bin/env python3
"""
Test MCP Session Handling
=========================

Figure out proper session management for CMKL MCP server
"""

import requests
import json
import time

def test_session_formats():
    """Test different session ID formats"""
    print("🔧 Testing MCP Session Formats")
    print("=" * 35)
    
    url = "https://mcp-hackathon.cmkl.ai/mcp"
    session_id = f"healthcare_test_{int(time.time())}"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    # Test 1: Session in URL parameters
    print("📋 Test 1: Session as URL parameter")
    try:
        response = requests.post(
            f"{url}?session_id={session_id}",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list"
            },
            headers=headers,
            timeout=10
        )
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✅ SUCCESS with URL param!")
            data = response.json()
            print(f"  Response: {json.dumps(data, indent=2)[:300]}...")
            return "url_param"
        else:
            print(f"  Response: {response.text[:100]}...")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test 2: Session in headers
    print("\n📋 Test 2: Session in headers")
    try:
        session_headers = {**headers, "X-Session-ID": session_id}
        response = requests.post(
            url,
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            },
            headers=session_headers,
            timeout=10
        )
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✅ SUCCESS with header!")
            data = response.json()
            print(f"  Response: {json.dumps(data, indent=2)[:300]}...")
            return "header"
        else:
            print(f"  Response: {response.text[:100]}...")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test 3: Initialize session first
    print("\n📋 Test 3: Initialize session first")
    try:
        init_response = requests.post(
            url,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "clientInfo": {
                        "name": "healthcare-client",
                        "version": "1.0.0"
                    },
                    "capabilities": {}
                }
            },
            headers=headers,
            timeout=10
        )
        print(f"  Init Status: {init_response.status_code}")
        print(f"  Init Response: {init_response.text[:150]}...")
        
        if init_response.status_code == 200:
            # Try tools/list after initialization
            tools_response = requests.post(
                url,
                json={
                    "jsonrpc": "2.0", 
                    "id": 2,
                    "method": "tools/list"
                },
                headers=headers,
                timeout=10
            )
            print(f"  Tools Status: {tools_response.status_code}")
            if tools_response.status_code == 200:
                print(f"  ✅ SUCCESS after initialization!")
                data = tools_response.json()
                print(f"  Response: {json.dumps(data, indent=2)[:300]}...")
                return "initialize_first"
            else:
                print(f"  Tools Response: {tools_response.text[:100]}...")
                
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test 4: Session with cookies
    print("\n📋 Test 4: Session with cookies")
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        # Set a session cookie
        session.cookies.set('session_id', session_id)
        
        response = session.post(
            url,
            json={
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/list"
            },
            timeout=10
        )
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✅ SUCCESS with cookies!")
            data = response.json()
            print(f"  Response: {json.dumps(data, indent=2)[:300]}...")
            return "cookies"
        else:
            print(f"  Response: {response.text[:100]}...")
            
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test 5: Different session field names
    print("\n📋 Test 5: Different session field names in body")
    session_fields = ["session", "sessionId", "client_session", "connection_id"]
    
    for field in session_fields:
        try:
            response = requests.post(
                url,
                json={
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/list",
                    field: session_id
                },
                headers=headers,
                timeout=10
            )
            print(f"  {field}: Status {response.status_code}")
            if response.status_code == 200:
                print(f"  ✅ SUCCESS with field '{field}'!")
                data = response.json()
                print(f"  Response: {json.dumps(data, indent=2)[:300]}...")
                return f"body_{field}"
            elif response.status_code != 400:
                print(f"    Different error: {response.text[:50]}...")
                
        except Exception as e:
            print(f"    Error: {e}")
    
    return None

def test_real_tool_call(session_method):
    """Test a real tool call with working session method"""
    print(f"\n🧪 Testing Real Tool Call")
    print("-" * 30)
    
    if not session_method:
        print("❌ No working session method found")
        return
    
    url = "https://mcp-hackathon.cmkl.ai/mcp"
    session_id = f"healthcare_test_{int(time.time())}"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    # Test with lookup_patient tool
    request_data = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "lookup_patient",
            "arguments": {
                "patient_id": "สิทธิประกันสุขภาพแห่งชาติ"
            }
        }
    }
    
    # Apply session method
    if session_method == "url_param":
        response = requests.post(f"{url}?session_id={session_id}", json=request_data, headers=headers, timeout=15)
    elif session_method == "header":
        headers["X-Session-ID"] = session_id
        response = requests.post(url, json=request_data, headers=headers, timeout=15)
    elif session_method.startswith("body_"):
        field_name = session_method.split("_", 1)[1]
        request_data[field_name] = session_id
        response = requests.post(url, json=request_data, headers=headers, timeout=15)
    else:
        print(f"❌ Unknown session method: {session_method}")
        return
    
    print(f"Tool call status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✅ HEALTHCARE TOOL CALL SUCCESS!")
        try:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)[:500]}...")
            
            # Look for Thai healthcare content
            response_str = str(data)
            if any(keyword in response_str for keyword in ['สิทธิ', 'ประกัน', 'บัตร', 'ทอง']):
                print(f"🎯 Found Thai healthcare content!")
                
        except Exception as e:
            print(f"Response (non-JSON): {response.text[:200]}...")
    else:
        print(f"❌ Tool call failed: {response.text[:150]}...")

def main():
    print("🌐 MCP Session Management Testing")
    print("=" * 40)
    
    # Find working session method
    working_method = test_session_formats()
    
    if working_method:
        print(f"\n🎯 Working session method: {working_method}")
        
        # Test real tool call
        test_real_tool_call(working_method)
        
        print(f"\n✅ MCP Connection Established!")
        print(f"📋 Use this configuration in comprehensive_mcp_client.py:")
        print(f"  Method: {working_method}")
        print(f"  URL: https://mcp-hackathon.cmkl.ai/mcp")
        print(f"  Headers: Accept: application/json, text/event-stream")
        
    else:
        print(f"\n❌ Could not establish MCP session")
        print(f"💡 May need authentication or special session setup")

if __name__ == "__main__":
    main()