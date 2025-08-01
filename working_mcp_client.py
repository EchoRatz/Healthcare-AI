#!/usr/bin/env python3
"""
WORKING MCP Client - Session ID in Headers!
===========================================

Finally cracked the CMKL MCP server session format!
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional

class WorkingMCPClient:
    """Working CMKL MCP client with proper session handling"""
    
    def __init__(self, server_url: str = "https://mcp-hackathon.cmkl.ai/mcp"):
        self.server_url = server_url
        self.session = None
        self.session_id = None
        self.initialized = False
        
    async def __aenter__(self):
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def initialize(self):
        """Initialize MCP session and extract session ID from headers"""
        self.session = aiohttp.ClientSession()
        
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
        
        async with self.session.post(self.server_url, json=init_request, headers=headers) as response:
            if response.status == 200:
                # Extract session ID from response headers!
                self.session_id = response.headers.get('mcp-session-id')
                if self.session_id:
                    print(f"✅ MCP Session initialized: {self.session_id}")
                    self.initialized = True
                    
                    # Now discover available tools
                    await self._discover_tools()
                    return True
                else:
                    print("❌ No session ID in response headers")
            else:
                text = await response.text()
                print(f"❌ Init failed: {response.status} - {text}")
        
        return False
    
    async def _discover_tools(self):
        """Discover what tools are actually available"""
        request_body = {
            "jsonrpc": "2.0",
            "id": "tools-list",
            "method": "tools/list"
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "mcp-session-id": self.session_id
        }
        
        async with self.session.post(self.server_url, json=request_body, headers=headers) as response:
            print(f"🔍 Tool discovery status: {response.status}")
            
            if response.status == 200:
                content_type = response.headers.get('content-type', '')
                print(f"🔍 Content type: {content_type}")
                
                if 'text/event-stream' in content_type:
                    text = await response.text()
                    print(f"🔍 SSE response: {text[:200]}...")
                    # Parse SSE
                    lines = text.strip().split('\n')
                    for line in lines:
                        if line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])
                                print(f"🔍 Parsed data: {data}")
                                if "result" in data and "tools" in data["result"]:
                                    tools = data["result"]["tools"]
                                    print(f"📋 Available tools ({len(tools)}):")
                                    for tool in tools[:5]:  # Show first 5
                                        print(f"   - {tool.get('name', 'Unknown')}")
                                    return tools
                                elif "result" in data:
                                    print(f"🔍 Result keys: {data['result'].keys()}")
                            except Exception as e:
                                print(f"🔍 Parse error: {e}")
                                continue
                else:
                    data = await response.json()
                    print(f"🔍 JSON data: {data}")
                    if "result" in data and "tools" in data["result"]:
                        tools = data["result"]["tools"]
                        print(f"📋 Available tools ({len(tools)}):")
                        for tool in tools[:5]:  # Show first 5
                            print(f"   - {tool.get('name', 'Unknown')}")
                        return tools
            else:
                text = await response.text()
                print(f"❌ Tool discovery failed: {response.status} - {text}")
        
        return []
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """Call tool with proper session ID in headers"""
        if not self.initialized or not self.session_id:
            raise ValueError("MCP client not initialized")
        
        # Use EXACT format from Raw_Body_MCP.txt
        request_body = {
            "jsonrpc": "2.0",
            "id": f"tool-{tool_name}",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments if arguments else {}  # Ensure arguments is always dict
            }
        }
        
        # Use session ID in headers!
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "mcp-session-id": self.session_id  # This is the key!
        }
        
        async with self.session.post(self.server_url, json=request_body, headers=headers) as response:
            if response.status == 200:
                content_type = response.headers.get('content-type', '')
                
                if 'text/event-stream' in content_type:
                    text = await response.text()
                    # Parse SSE
                    lines = text.strip().split('\n')
                    for line in lines:
                        if line.startswith('data: '):
                            try:
                                return json.loads(line[6:])
                            except:
                                continue
                else:
                    return await response.json()
            else:
                text = await response.text()
                return {"error": f"HTTP {response.status}: {text}"}
        
        return {"error": "No response received"}
    
    # Healthcare tool methods
    async def list_all_departments(self):
        """List all hospital departments"""
        return await self.call_tool("list_all_departments", {})
    
    async def lookup_patient(self, patient_id: str):
        """Lookup patient by ID"""
        return await self.call_tool("lookup_patient", {"patient_id": patient_id})
    
    async def search_doctors(self, specialty: str = None, department: str = None):
        """Search doctors"""
        # Match Raw_Body_MCP.txt format exactly
        args = {}
        if specialty is not None:
            args["specialty"] = specialty
        if department is not None:
            args["department"] = department
        return await self.call_tool("search_doctors", args)
    
    async def emergency_patient_lookup(self, identifier: str):
        """Emergency patient lookup"""
        return await self.call_tool("emergency_patient_lookup", {"identifier": identifier})

async def test_working_mcp():
    """Test the working MCP client"""
    print("🚀 Testing WORKING MCP Client")
    print("=" * 50)
    
    async with WorkingMCPClient() as client:
        if not client.initialized:
            print("❌ Failed to initialize")
            return
        
        # Test 1: List departments
        print("\n📋 Test 1: List all departments")
        result = await client.list_all_departments()
        print(f"Result: {result}")
        
        if "error" not in result:
            print("🎉 SUCCESS! Real MCP is working!")
        
        # Test 2: Search doctors
        print("\n👨‍⚕️ Test 2: Search doctors")
        result = await client.search_doctors(specialty="cardiology")
        print(f"Result: {result}")
        
        # Test 3: Patient lookup
        print("\n👤 Test 3: Patient lookup")  
        result = await client.lookup_patient("test123")
        print(f"Result: {result}")
        
        # Test 4: Emergency lookup
        print("\n🚨 Test 4: Emergency lookup")
        result = await client.emergency_patient_lookup("emergency123")
        print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(test_working_mcp())