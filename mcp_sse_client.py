#!/usr/bin/env python3
"""
MCP SSE Client for CMKL Healthcare Server
=========================================

Proper SSE-based MCP client for the CMKL hackathon server
"""

import requests
import json
import time
import asyncio
import aiohttp
import threading
from typing import Dict, List, Optional, Any
from queue import Queue, Empty

class MCPSSEClient:
    """SSE-based MCP client for CMKL server"""
    
    def __init__(self, server_url: str = "https://mcp-hackathon.cmkl.ai"):
        self.server_url = server_url
        self.session_id = None
        self.response_queue = Queue()
        self.sse_thread = None
        self.connected = False
        
    def connect(self) -> bool:
        """Connect to MCP SSE server"""
        try:
            # Start SSE listener in background
            self.session_id = f"healthcare_client_{int(time.time())}"
            self.sse_thread = threading.Thread(target=self._sse_listener, daemon=True)
            self.sse_thread.start()
            
            # Give it a moment to connect
            time.sleep(2)
            
            return self.connected
            
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def _sse_listener(self):
        """Listen for SSE events"""
        try:
            sse_url = f"{self.server_url}/mcp"
            headers = {
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
            
            # Add session ID if needed
            params = {"session_id": self.session_id} if self.session_id else {}
            
            print(f"🔗 Connecting to SSE: {sse_url}")
            
            response = requests.get(sse_url, headers=headers, params=params, stream=True, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ SSE connected!")
                self.connected = True
                
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        if line.startswith("data: "):
                            data = line[6:]  # Remove "data: " prefix
                            try:
                                json_data = json.loads(data)
                                self.response_queue.put(json_data)
                            except json.JSONDecodeError:
                                print(f"Non-JSON SSE data: {data}")
                        elif line.startswith("event: "):
                            event_type = line[7:]  # Remove "event: " prefix
                            print(f"SSE Event: {event_type}")
            else:
                print(f"❌ SSE connection failed: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ SSE listener error: {e}")
        finally:
            self.connected = False
    
    def send_message(self, message: Dict) -> Optional[Dict]:
        """Send message via POST and wait for SSE response"""
        try:
            # Send via POST
            post_url = f"{self.server_url}/message"
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Add session ID to message
            if self.session_id:
                message = {**message, "session_id": self.session_id}
            
            response = requests.post(post_url, json=message, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Message sent successfully")
                
                # Wait for response via SSE
                try:
                    response_data = self.response_queue.get(timeout=15)
                    return response_data
                except Empty:
                    print("⏰ No response received via SSE")
                    return None
            else:
                print(f"❌ POST failed: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"❌ Send message error: {e}")
            return None
    
    def test_healthcare_validation(self, question: str, choices: Dict[str, str]) -> Optional[Dict]:
        """Test healthcare question validation"""
        if not self.connected:
            print("❌ Not connected to MCP server")
            return None
        
        # Try the lookup_patient tool with healthcare question
        test_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "lookup_patient",
                "arguments": {
                    "patient_id": question
                }
            }
        }
        
        print(f"📤 Sending healthcare validation request...")
        response = self.send_message(test_message)
        
        if response:
            print(f"📥 Received response!")
            return response
        else:
            print(f"❌ No response received")
            return None
    
    def initialize(self) -> Optional[Dict]:
        """Initialize MCP connection"""
        init_message = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "clientInfo": {
                    "name": "healthcare-sse-client",
                    "version": "1.0.0"
                },
                "capabilities": {
                    "tools": {"listChanged": True}
                }
            }
        }
        
        return self.send_message(init_message)
    
    def list_tools(self) -> Optional[Dict]:
        """List available tools"""
        tools_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
        
        return self.send_message(tools_message)
    
    def close(self):
        """Close connection"""
        self.connected = False
        if self.sse_thread and self.sse_thread.is_alive():
            # SSE thread will close when connected becomes False
            self.sse_thread.join(timeout=2)

def test_sse_client():
    """Test the SSE MCP client"""
    print("🧪 Testing MCP SSE Client")
    print("=" * 30)
    
    client = MCPSSEClient()
    
    try:
        # Connect
        print("🔗 Connecting to MCP server...")
        if not client.connect():
            print("❌ Failed to connect")
            return
        
        # Initialize
        print("\n📋 Initializing MCP session...")
        init_response = client.initialize()
        if init_response:
            print(f"✅ Initialization successful!")
            print(f"Response: {json.dumps(init_response, indent=2)[:300]}...")
        else:
            print("❌ Initialization failed")
        
        # List tools
        print("\n📋 Listing available tools...")
        tools_response = client.list_tools()
        if tools_response:
            print(f"✅ Tools list received!")
            print(f"Response: {json.dumps(tools_response, indent=2)[:300]}...")
        else:
            print("❌ Tools list failed")
        
        # Test healthcare question
        print("\n📋 Testing healthcare validation...")
        question = "สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ?"
        choices = {
            "ก": "สิทธิหลักประกันสุขภาพแห่งชาติ",
            "ข": "สิทธิบัตรทอง", 
            "ค": "สิทธิ 30 บาทรักษาทุกโรค",
            "ง": "ไม่มีข้อใดถูกต้อง"
        }
        
        validation_response = client.test_healthcare_validation(question, choices)
        if validation_response:
            print(f"✅ Healthcare validation successful!")
            print(f"Response: {json.dumps(validation_response, indent=2)[:500]}...")
            
            # Try to extract answer
            if "result" in validation_response:
                result = validation_response["result"]
                print(f"\n🎯 MCP Answer Analysis:")
                print(f"  Type: {type(result)}")
                
                # Look for Thai choices
                result_str = str(result)
                thai_choices = [c for c in ['ก', 'ข', 'ค', 'ง'] if c in result_str]
                if thai_choices:
                    print(f"  Found choices: {thai_choices}")
                
                # Look for healthcare terms
                healthcare_terms = ['สิทธิ', 'ประกัน', 'สุขภาพ', 'บัตร', 'ทอง']
                found_terms = [term for term in healthcare_terms if term in result_str]
                if found_terms:
                    print(f"  Healthcare terms: {found_terms}")
                    
        else:
            print("❌ Healthcare validation failed")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted")
    except Exception as e:
        print(f"❌ Test error: {e}")
    finally:
        print("\n🔌 Closing connection...")
        client.close()

def main():
    """Main function"""
    print("🌐 MCP SSE Healthcare Client")
    print("=" * 35)
    print("Testing CMKL MCP server with proper SSE connection")
    print()
    
    test_sse_client()
    
    print(f"\n💡 Key Learnings:")
    print(f"  - MCP server uses SSE (Server-Sent Events)")
    print(f"  - Messages sent via POST, responses via SSE")
    print(f"  - Session management may be required")
    print(f"  - Tool 'lookup_patient' is available")
    
    print(f"\n🎯 Next Steps:")
    print(f"  1. If successful, integrate SSE client into main system")
    print(f"  2. Update mcp_healthcare_client.py with SSE support")
    print(f"  3. Test with your contradictory question examples")
    print(f"  4. Deploy in production with ultra_fast_llama31.py")

if __name__ == "__main__":
    main()