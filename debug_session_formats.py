#!/usr/bin/env python3
"""Debug different session ID formats for CMKL MCP server"""

import asyncio
import aiohttp
import json
import uuid

async def test_session_formats():
    """Test different ways to send session ID"""
    
    session_id = str(uuid.uuid4())
    url = "https://mcp-hackathon.cmkl.ai/mcp"
    
    # Test different session ID formats
    test_cases = [
        # 1. Query parameter
        {
            "name": "URL Query Parameter",
            "url": f"{url}?sessionId={session_id}",
            "headers": {"Content-Type": "application/json"},
            "body": {
                "jsonrpc": "2.0",
                "id": "test-1",
                "method": "tools/call",
                "params": {"name": "list_all_departments", "arguments": {}}
            }
        },
        
        # 2. MCP-specific headers
        {
            "name": "MCP Headers",
            "url": url,
            "headers": {
                "Content-Type": "application/json",
                "MCP-Session-ID": session_id,
                "X-MCP-Session": session_id
            },
            "body": {
                "jsonrpc": "2.0",
                "id": "test-2", 
                "method": "tools/call",
                "params": {"name": "list_all_departments", "arguments": {}}
            }
        },
        
        # 3. Authorization Bearer
        {
            "name": "Bearer Token",
            "url": url,
            "headers": {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {session_id}"
            },
            "body": {
                "jsonrpc": "2.0",
                "id": "test-3",
                "method": "tools/call", 
                "params": {"name": "list_all_departments", "arguments": {}}
            }
        },
        
        # 4. Session in outer JSON wrapper
        {
            "name": "JSON Wrapper",
            "url": url,
            "headers": {"Content-Type": "application/json"},
            "body": {
                "sessionId": session_id,
                "request": {
                    "jsonrpc": "2.0",
                    "id": "test-4",
                    "method": "tools/call",
                    "params": {"name": "list_all_departments", "arguments": {}}
                }
            }
        },
        
        # 5. No method - direct params
        {
            "name": "Direct Format",
            "url": url,
            "headers": {"Content-Type": "application/json"},
            "body": {
                "jsonrpc": "2.0",
                "id": "test-5",
                "sessionId": session_id,
                "name": "list_all_departments",
                "arguments": {}
            }
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 Test {i}: {test_case['name']}")
            print(f"   URL: {test_case['url']}")
            print(f"   Headers: {test_case['headers']}")
            print(f"   Body: {json.dumps(test_case['body'], indent=2)}")
            
            try:
                async with session.post(
                    test_case['url'],
                    headers=test_case['headers'],
                    json=test_case['body'],
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    status = response.status
                    text = await response.text()
                    
                    print(f"   ✅ Status: {status}")
                    if status == 200:
                        print(f"   🎉 SUCCESS! Format works!")
                        print(f"   📄 Response: {text[:200]}...")
                        return test_case  # Found working format!
                    else:
                        print(f"   ❌ Response: {text[:100]}...")
                        
            except Exception as e:
                print(f"   💥 Error: {e}")
                
    print(f"\n❌ No working session format found")
    return None

if __name__ == "__main__":
    asyncio.run(test_session_formats())