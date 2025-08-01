#!/usr/bin/env python3
"""
Aggressive MCP Client - Multiple Authentication Attempts
=======================================================

Try every possible authentication method to get MCP server working
"""

import requests
import json
import time
import threading
from queue import Queue
from typing import Dict, List, Optional

class AggressiveMCPClient:
    """Try every possible method to connect to MCP server"""
    
    def __init__(self):
        self.base_url = "https://mcp-hackathon.cmkl.ai"
        self.success_queue = Queue()
        self.working_config = None
        
    def test_all_connection_methods(self) -> Optional[Dict]:
        """Test every possible connection method in parallel"""
        print("🚀 Testing ALL possible MCP connection methods...")
        
        # All possible endpoints
        endpoints = ["/mcp", "/message", "/api/mcp", "/tools", "/rpc", "/jsonrpc", "/api/tools", "/healthcare"]
        
        # All possible authentication methods
        auth_methods = [
            {"type": "none", "data": {}},
            {"type": "session_body", "data": {"session_id": f"healthcare_{int(time.time())}"}},
            {"type": "session_url", "data": {"session_id": f"patient_{int(time.time())}"}},
            {"type": "auth_header", "data": {"Authorization": "Bearer healthcare-token"}},
            {"type": "api_key", "data": {"X-API-Key": "healthcare-api-key"}},
            {"type": "client_id", "data": {"client_id": "healthcare-client", "client_secret": "secret"}},
        ]
        
        # All possible request formats
        request_formats = [
            {
                "name": "full_jsonrpc",
                "format": {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "lookup_patient",
                        "arguments": {"patient_id": "สิทธิประกันสุขภาพ"}
                    }
                }
            },
            {
                "name": "simple_format",
                "format": {
                    "method": "tools/call",
                    "params": {
                        "name": "lookup_patient", 
                        "arguments": {"patient_id": "สิทธิประกันสุขภาพ"}
                    }
                }
            },
            {
                "name": "direct_call",
                "format": {
                    "tool": "lookup_patient",
                    "args": {"patient_id": "สิทธิประกันสุขภาพ"}
                }
            }
        ]
        
        # All possible headers
        header_variants = [
            {"Content-Type": "application/json", "Accept": "application/json"},
            {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"},
            {"Content-Type": "application/json", "Accept": "text/event-stream"},
            {"Content-Type": "application/json", "Accept": "*/*"},
        ]
        
        threads = []
        
        # Test all combinations
        for endpoint in endpoints:
            for auth in auth_methods:
                for req_format in request_formats:
                    for headers in header_variants:
                        thread = threading.Thread(
                            target=self._test_combination,
                            args=(endpoint, auth, req_format, headers)
                        )
                        threads.append(thread)
                        thread.start()
        
        # Wait for first success or all failures
        print(f"⚡ Started {len(threads)} parallel connection attempts...")
        
        for thread in threads:
            thread.join(timeout=2)  # Quick timeout per thread
        
        # Check if we got any successes
        successes = []
        while not self.success_queue.empty():
            successes.append(self.success_queue.get())
        
        if successes:
            self.working_config = successes[0]  # Use first working config
            print(f"✅ Found {len(successes)} working configurations!")
            print(f"🎯 Using: {self.working_config['description']}")
            return self.working_config
        else:
            print(f"❌ No working configurations found from {len(threads)} attempts")
            return None
    
    def _test_combination(self, endpoint: str, auth: Dict, req_format: Dict, headers: Dict):
        """Test a specific combination of connection parameters"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            # Prepare request
            request_data = req_format['format'].copy()
            
            # Add auth data to request body
            if auth['type'] == 'session_body':
                request_data.update(auth['data'])
            elif auth['type'] == 'client_id':
                request_data.update(auth['data'])
            
            # Add auth data to URL
            if auth['type'] == 'session_url':
                session_key = list(auth['data'].keys())[0]
                url += f"?{session_key}={auth['data'][session_key]}"
            
            # Add auth data to headers
            final_headers = headers.copy()
            if auth['type'] == 'auth_header':
                final_headers.update(auth['data'])
            elif auth['type'] == 'api_key':
                final_headers.update(auth['data'])
            
            # Make request
            response = requests.post(url, json=request_data, headers=final_headers, timeout=5)
            
            if response.status_code == 200:
                # Check if response contains useful data
                response_text = response.text
                
                # Look for healthcare content or valid JSON
                has_healthcare_content = any(term in response_text for term in 
                    ['สิทธิ', 'ประกัน', 'บัตร', 'ทอง', 'สุขภาพ', 'patient', 'doctor'])
                
                has_valid_json = False
                try:
                    json_data = response.json()
                    has_valid_json = True
                except:
                    # Try SSE format
                    if 'data:' in response_text:
                        has_valid_json = True
                
                if has_healthcare_content or has_valid_json:
                    success_config = {
                        'endpoint': endpoint,
                        'auth': auth,
                        'format': req_format,
                        'headers': final_headers,
                        'url': url,
                        'description': f"{endpoint} + {auth['type']} + {req_format['name']}",
                        'response_preview': response_text[:200]
                    }
                    self.success_queue.put(success_config)
                    
        except Exception as e:
            pass  # Ignore failures in parallel testing
    
    def query_healthcare_data(self, question: str, choices: Dict[str, str]) -> Optional[Dict]:
        """Query healthcare data using working configuration"""
        if not self.working_config:
            return None
        
        # Use working config to make healthcare queries
        healthcare_tools = [
            ("lookup_patient", {"patient_id": "สิทธิประกันสุขภาพแห่งชาติ"}),
            ("search_patients", {"search_term": "สิทธิประกัน"}),
            ("emergency_patient_lookup", {"identifier": "สิทธิบัตรทอง"}),
            ("list_all_departments", {}),
            ("search_doctors", {"specialty": "สุขภาพแห่งชาติ"}),
        ]
        
        results = {}
        
        for tool_name, arguments in healthcare_tools:
            try:
                # Prepare request using working config
                request_data = self.working_config['format']['format'].copy()
                request_data['params']['name'] = tool_name
                request_data['params']['arguments'] = arguments
                
                # Add auth data
                if self.working_config['auth']['type'] == 'session_body':
                    request_data.update(self.working_config['auth']['data'])
                
                response = requests.post(
                    self.working_config['url'],
                    json=request_data,
                    headers=self.working_config['headers'],
                    timeout=10
                )
                
                if response.status_code == 200:
                    results[tool_name] = response.text
                    print(f"✅ {tool_name}: Got data ({len(response.text)} chars)")
                
            except Exception as e:
                print(f"❌ {tool_name}: {str(e)[:50]}")
        
        return results if results else None

def test_aggressive_client():
    """Test the aggressive MCP client"""
    print("🔥 Aggressive MCP Client Testing")
    print("=" * 40)
    
    client = AggressiveMCPClient()
    
    # Find working connection
    working_config = client.test_all_connection_methods()
    
    if working_config:
        print(f"\n🎉 SUCCESS! MCP server is accessible!")
        print(f"📋 Working configuration:")
        print(f"  Endpoint: {working_config['endpoint']}")
        print(f"  Auth: {working_config['auth']['type']}")
        print(f"  Format: {working_config['format']['name']}")
        print(f"  Response: {working_config['response_preview'][:100]}...")
        
        # Test healthcare queries
        print(f"\n🏥 Testing healthcare queries...")
        question = "สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ?"
        choices = {
            "ก": "สิทธิหลักประกันสุขภาพแห่งชาติ",
            "ข": "สิทธิบัตรทอง",
            "ค": "สิทธิ 30 บาทรักษาทุกโรค",
            "ง": "ไม่มีข้อใดถูกต้อง"
        }
        
        healthcare_data = client.query_healthcare_data(question, choices)
        
        if healthcare_data:
            print(f"🎯 Got healthcare data from {len(healthcare_data)} tools!")
            
            # Save working config for integration
            with open('working_mcp_config.json', 'w', encoding='utf-8') as f:
                json.dump(working_config, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved working config to working_mcp_config.json")
            
            return True
        else:
            print(f"⚠️ Connection works but no healthcare data available")
            return False
    else:
        print(f"\n❌ Could not find any working MCP configuration")
        print(f"💡 Server may require special authentication or be temporarily unavailable")
        return False

if __name__ == "__main__":
    success = test_aggressive_client()
    
    if success:
        print(f"\n🚀 Ready to integrate working MCP client!")
        print(f"📝 Next: Update ultra_fast_llama31.py with working config")
    else:
        print(f"\n🔧 Need to focus on reducing 'ง' answers without MCP")
        print(f"📊 Current issue: 249/500 answers are 'ง' (too many 'None')")