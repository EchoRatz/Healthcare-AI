#!/usr/bin/env python3
"""Test persistent session with cookies"""

import asyncio
import aiohttp
import json

async def test_persistent_session():
    """Test if session uses cookies or persistent connection"""
    
    url = "https://mcp-hackathon.cmkl.ai/mcp"
    
    # Use cookie jar to persist cookies
    jar = aiohttp.CookieJar(unsafe=True)
    
    async with aiohttp.ClientSession(cookie_jar=jar) as session:
        
        # Step 1: Initialize and capture any cookies
        print("🍪 Step 1: Initialize with Cookie Persistence")
        init_request = {
            "jsonrpc": "2.0",
            "id": "init-1",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
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
        
        async with session.post(url, json=init_request, headers=headers) as response:
            print(f"   Status: {response.status}")
            print(f"   Cookies: {[f'{c.key}={c.value}' for c in session.cookie_jar]}")
            
            # Check response headers for session info
            print(f"   Response Headers:")
            for key, value in response.headers.items():
                if 'session' in key.lower() or 'set-cookie' in key.lower():
                    print(f"     {key}: {value}")
            
            text = await response.text()
            print(f"   Response: {text[:150]}...")
        
        print()
        
        # Step 2: Try tool call with cookies
        print("🔧 Step 2: Tool Call with Persistent Cookies")
        tool_request = {
            "jsonrpc": "2.0",
            "id": "tool-1",
            "method": "tools/call",
            "params": {
                "name": "list_all_departments",
                "arguments": {}
            }
        }
        
        async with session.post(url, json=tool_request, headers=headers) as response:
            print(f"   Status: {response.status}")
            text = await response.text()
            print(f"   Response: {text[:150]}...")
            
            if response.status == 200:
                print("   🎉 SUCCESS! Cookies worked!")
                return True
        
        print()
        
        # Step 3: Try WebSocket connection
        print("🔌 Step 3: Check if Server Prefers WebSocket")
        try:
            ws_url = "wss://mcp-hackathon.cmkl.ai/mcp"
            async with session.ws_connect(ws_url) as ws:
                
                # Send init via WebSocket
                await ws.send_str(json.dumps(init_request))
                response = await ws.receive()
                print(f"   WS Response: {response.data[:100]}...")
                
                # Send tool call
                await ws.send_str(json.dumps(tool_request))
                response = await ws.receive()
                print(f"   WS Tool Response: {response.data[:100]}...")
                
                if "error" not in response.data:
                    print("   🎉 SUCCESS! WebSocket worked!")
                    return True
                    
        except Exception as e:
            print(f"   WebSocket failed: {e}")
        
    return False

if __name__ == "__main__":
    asyncio.run(test_persistent_session())