#!/usr/bin/env python3
"""
MCP SSE Session Handler
======================

Handle MCP server's SSE responses and session management
"""

import requests
import json
import time
import threading
import queue
from typing import Dict, Optional, Any

class MCPSSESession:
    """Handle MCP server with SSE responses"""
    
    def __init__(self, server_url: str = "https://mcp-hackathon.cmkl.ai"):
        self.server_url = server_url
        self.session_id = None
        self.response_queue = queue.Queue()
        self.connected = False
        
    def _parse_sse_response(self, response_text: str) -> Optional[Dict]:
        """Parse SSE response format"""
        try:
            lines = response_text.strip().split('\n')
            data_line = None
            
            for line in lines:
                if line.startswith('data: '):
                    data_line = line[6:]  # Remove 'data: ' prefix
                    break
            
            if data_line:
                return json.loads(data_line)
            
        except Exception as e:
            print(f"❌ SSE parse error: {e}")
            print(f"Raw response: {response_text[:200]}...")
        
        return None
    
    def initialize_session(self) -> bool:
        """Initialize MCP session with proper parameters"""
        print("🔧 Initializing MCP session...")
        
        url = f"{self.server_url}/mcp"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        # Try different initialization parameter combinations
        init_variants = [
            {
                "clientInfo": {
                    "name": "healthcare-client",
                    "version": "1.0.0"
                },
                "capabilities": {
                    "tools": {"listChanged": True}
                }
            },
            {
                "clientInfo": {
                    "name": "healthcare-client",
                    "version": "1.0.0"
                }
            },
            {
                "name": "healthcare-client",
                "version": "1.0.0",
                "capabilities": {}
            },
            {}  # Empty params
        ]
        
        for i, params in enumerate(init_variants):
            print(f"\n📋 Trying init variant {i+1}...")
            
            request_data = {
                "jsonrpc": "2.0",
                "id": i + 1,
                "method": "initialize"
            }
            
            if params:
                request_data["params"] = params
            
            try:
                response = requests.post(url, json=request_data, headers=headers, timeout=15)
                
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    # Parse SSE response
                    sse_data = self._parse_sse_response(response.text)
                    
                    if sse_data:
                        print(f"  📡 SSE Response: {json.dumps(sse_data, indent=2)[:200]}...")
                        
                        # Check if initialization was successful
                        if "result" in sse_data:
                            print(f"  ✅ Initialization successful!")
                            
                            # Extract session info if available
                            result = sse_data["result"]
                            if isinstance(result, dict):
                                self.session_id = result.get("sessionId") or result.get("session_id") or f"session_{int(time.time())}"
                            else:
                                self.session_id = f"session_{int(time.time())}"
                                
                            self.connected = True
                            return True
                            
                        elif "error" not in sse_data:
                            # No error, might still be valid
                            print(f"  🔶 Initialization response without error")
                            self.session_id = f"session_{int(time.time())}"
                            self.connected = True
                            return True
                        else:
                            error = sse_data["error"]
                            print(f"  ❌ Init error: {error.get('message', 'Unknown')}")
                            
                else:
                    print(f"  ❌ HTTP {response.status_code}: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"  ❌ Request error: {e}")
        
        return False
    
    def call_tool(self, tool_name: str, arguments: Dict = None) -> Optional[Dict]:
        """Call MCP tool with session"""
        if not self.connected:
            print("❌ Not connected - call initialize_session() first")
            return None
        
        url = f"{self.server_url}/mcp"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        # Try different session formats
        session_formats = [
            {"session_id": self.session_id},  # In body
            {},  # No session (maybe not needed after init)
        ]
        
        for session_format in session_formats:
            request_data = {
                "jsonrpc": "2.0",
                "id": int(time.time() * 1000),
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments or {}
                }
            }
            
            # Add session data
            request_data.update(session_format)
            
            try:
                # Try URL param as well
                url_with_session = f"{url}?session_id={self.session_id}" if session_format else url
                
                response = requests.post(url_with_session, json=request_data, headers=headers, timeout=15)
                
                print(f"📤 Tool call: {tool_name} (session: {bool(session_format)})")
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    # Parse SSE response
                    sse_data = self._parse_sse_response(response.text)
                    
                    if sse_data:
                        print(f"  ✅ Tool call successful!")
                        return sse_data
                    else:
                        # Try direct JSON parse
                        try:
                            direct_data = response.json()
                            print(f"  ✅ Tool call successful (direct JSON)!")
                            return direct_data
                        except:
                            print(f"  📄 Raw response: {response.text[:200]}...")
                            return {"raw_response": response.text}
                            
                else:
                    print(f"  ❌ HTTP {response.status_code}: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"  ❌ Tool call error: {e}")
        
        return None
    
    def test_healthcare_tools(self):
        """Test various healthcare tools"""
        print("\n🏥 Testing Healthcare Tools")
        print("-" * 30)
        
        if not self.connected:
            print("❌ Not connected")
            return
        
        # Test tools in order of importance
        test_tools = [
            ("lookup_patient", {"patient_id": "สิทธิประกันสุขภาพ"}),
            ("list_all_departments", {}),
            ("emergency_patient_lookup", {"identifier": "สิทธิบัตรทอง"}),
            ("search_patients", {"search_term": "สิทธิประกัน"}),
            ("get_department_services", {"dept_name": "สิทธิประกันสุขภาพ"}),
            ("search_doctors", {"specialty": "ประกันสุขภาพ"}),
        ]
        
        successful_tools = []
        
        for tool_name, arguments in test_tools:
            print(f"\n🔧 Testing: {tool_name}")
            
            result = self.call_tool(tool_name, arguments)
            
            if result and "error" not in result:
                successful_tools.append(tool_name)
                
                # Look for Thai healthcare content
                result_str = str(result)
                healthcare_keywords = ['สิทธิ', 'ประกัน', 'บัตร', 'ทอง', 'ก', 'ข', 'ค', 'ง']
                found_keywords = [kw for kw in healthcare_keywords if kw in result_str]
                
                if found_keywords:
                    print(f"  🎯 Healthcare content found: {found_keywords}")
                    print(f"  📄 Preview: {result_str[:150]}...")
                else:
                    print(f"  📄 Result: {result_str[:100]}...")
        
        print(f"\n📊 Test Results:")
        print(f"  Successful tools: {len(successful_tools)}/{len(test_tools)}")
        if successful_tools:
            print(f"  Working tools: {successful_tools}")
        
        return successful_tools

def main():
    """Test MCP SSE session"""
    print("🌐 MCP SSE Session Testing")
    print("=" * 35)
    
    session = MCPSSESession()
    
    # Initialize session
    if session.initialize_session():
        print(f"\n✅ Session established!")
        print(f"Session ID: {session.session_id}")
        
        # Test healthcare tools
        working_tools = session.test_healthcare_tools()
        
        if working_tools:
            print(f"\n🎉 MCP server is accessible for healthcare validation!")
            print(f"💡 Update comprehensive_mcp_client.py to use SSE parsing")
        else:
            print(f"\n🔶 Session works but tools need debugging")
    else:
        print(f"\n❌ Could not establish session")
        print(f"💡 MCP server may require authentication or different approach")

if __name__ == "__main__":
    main()