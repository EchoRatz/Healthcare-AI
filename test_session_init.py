#!/usr/bin/env python3
"""Test session initialization with CMKL MCP server"""

import asyncio
import aiohttp
import json
import uuid

async def test_session_initialization():
    """Test if we need to initialize session first"""
    
    url = "https://mcp-hackathon.cmkl.ai/mcp"
    session_id = str(uuid.uuid4())
    
    async with aiohttp.ClientSession() as session:
        
        # Step 1: Try to initialize session
        print("🔄 Step 1: Initialize Session")
        init_request = {
            "jsonrpc": "2.0",
            "id": "init-1",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "sessionId": session_id,
                "clientInfo": {
                    "name": "healthcare-ai-client",
                    "version": "1.0.0"
                },
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                }
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        try:
            async with session.post(url, json=init_request, headers=headers, timeout=10) as response:
                status = response.status
                content_type = response.headers.get('content-type', '')
                
                print(f"   Status: {status}")
                print(f"   Content-Type: {content_type}")
                
                if 'text/event-stream' in content_type:
                    text = await response.text()
                    print(f"   SSE Response: {text[:200]}...")
                    
                    # Parse SSE for session info
                    lines = text.strip().split('\n')
                    for line in lines:
                        if line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])
                                print(f"   Parsed Data: {data}")
                                
                                if "result" in data:
                                    print("   ✅ Initialization successful!")
                                    extracted_session = data.get("result", {}).get("sessionId")
                                    if extracted_session:
                                        session_id = extracted_session
                                        print(f"   📋 Server provided session ID: {session_id}")
                                    break
                            except:
                                continue
                else:
                    text = await response.text()
                    print(f"   JSON Response: {text}")
                    
        except Exception as e:
            print(f"   Error: {e}")
        
        print()
        
        # Step 2: Use the session ID for tool call
        print("🔧 Step 2: Call Tool with Session")
        tool_request = {
            "jsonrpc": "2.0",
            "id": "tool-1",
            "method": "tools/call",
            "params": {
                "name": "list_all_departments",
                "arguments": {},
                "sessionId": session_id  # Use session from init
            }
        }
        
        try:
            async with session.post(url, json=tool_request, headers=headers, timeout=10) as response:
                status = response.status
                content_type = response.headers.get('content-type', '')
                
                print(f"   Status: {status}")
                if status == 200:
                    print("   🎉 SUCCESS! Tool call worked!")
                
                if 'text/event-stream' in content_type:
                    text = await response.text()
                    print(f"   SSE Response: {text[:200]}...")
                else:
                    text = await response.text()
                    print(f"   Response: {text[:200]}...")
                    
        except Exception as e:
            print(f"   Error: {e}")
            
        print()
        
        # Step 3: Try alternative - session in headers after init
        print("🔧 Step 3: Try Session in Headers")
        headers_with_session = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "X-Session-ID": session_id,
            "MCP-Session-ID": session_id
        }
        
        tool_request_simple = {
            "jsonrpc": "2.0",
            "id": "tool-2",
            "method": "tools/call",
            "params": {
                "name": "list_all_departments",
                "arguments": {}
            }
        }
        
        try:
            async with session.post(url, json=tool_request_simple, headers=headers_with_session, timeout=10) as response:
                status = response.status
                print(f"   Status: {status}")
                
                if status == 200:
                    print("   🎉 SUCCESS! Header session worked!")
                
                text = await response.text()
                print(f"   Response: {text[:100]}...")
                    
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_session_initialization())