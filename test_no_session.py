#!/usr/bin/env python3
"""
Test JSON-RPC Without Session
=============================

Use proper JSON-RPC format but skip session management entirely
"""

import requests
import json
import time

def test_jsonrpc_no_session():
    """Test JSON-RPC format without any session management"""
    print("🧪 Testing JSON-RPC Without Session")
    print("=" * 40)
    
    url = "https://mcp-hackathon.cmkl.ai/mcp"
    headers = {
        "Content-Type": "application/json", 
        "Accept": "application/json, text/event-stream"
    }
    
    # Test with proper JSON-RPC but no session
    test_tools = [
        {
            "name": "lookup_patient",
            "arguments": {"patient_id": ""}
        },
        {
            "name": "lookup_patient", 
            "arguments": {"patient_id": "สิทธิประกันสุขภาพ"}
        },
        {
            "name": "search_patients",
            "arguments": {"search_term": "สิทธิ"}
        },
        {
            "name": "list_all_departments",
            "arguments": {}
        },
        {
            "name": "emergency_patient_lookup",
            "arguments": {"identifier": "healthcare_policy"}
        },
        {
            "name": "get_department_services", 
            "arguments": {"dept_name": "สิทธิประกัน"}
        }
    ]
    
    successful_calls = []
    healthcare_responses = []
    
    for i, tool in enumerate(test_tools):
        print(f"\n📋 Testing: {tool['name']}")
        print(f"   Args: {tool['arguments']}")
        
        # Proper JSON-RPC 2.0 format
        request_data = {
            "jsonrpc": "2.0",
            "id": i + 1,
            "method": "tools/call",
            "params": {
                "name": tool['name'],
                "arguments": tool['arguments']
            }
        }
        
        try:
            response = requests.post(url, json=request_data, headers=headers, timeout=15)
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ SUCCESS!")
                successful_calls.append(tool['name'])
                
                # Parse response
                try:
                    # Handle SSE format
                    response_text = response.text.strip()
                    
                    if 'data:' in response_text:
                        # Extract SSE data
                        for line in response_text.split('\n'):
                            if line.startswith('data: '):
                                data_json = line[6:]
                                data = json.loads(data_json)
                                print(f"  📡 SSE Data: {json.dumps(data, indent=2)[:200]}...")
                                
                                # Check for healthcare content
                                if _contains_healthcare_content(str(data)):
                                    print(f"  🎯 Contains healthcare data!")
                                    healthcare_responses.append({
                                        'tool': tool['name'],
                                        'response': data
                                    })
                                break
                    else:
                        # Direct JSON
                        data = response.json()
                        print(f"  📄 JSON: {json.dumps(data, indent=2)[:200]}...")
                        
                        if _contains_healthcare_content(str(data)):
                            print(f"  🎯 Contains healthcare data!")
                            healthcare_responses.append({
                                'tool': tool['name'], 
                                'response': data
                            })
                
                except Exception as parse_error:
                    print(f"  📄 Raw response: {response.text[:150]}...")
                    print(f"  ⚠️  Parse error: {parse_error}")
                    
            elif response.status_code == 400:
                # Check what specific error
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', '')
                    print(f"  ❌ Error: {error_msg[:100]}...")
                    
                    # If it's NOT a session error, this tool might just not work
                    if 'session' not in error_msg.lower():
                        print(f"  💡 Not a session error - tool might not be available")
                    
                except:
                    print(f"  ❌ HTTP 400: {response.text[:100]}...")
                    
            else:
                print(f"  ❌ HTTP {response.status_code}: {response.text[:100]}...")
                
        except Exception as e:
            print(f"  ❌ Request error: {str(e)[:50]}...")
    
    print(f"\n📊 Results Summary:")
    print(f"  Successful calls: {len(successful_calls)}/{len(test_tools)}")
    print(f"  Healthcare responses: {len(healthcare_responses)}")
    
    if successful_calls:
        print(f"  ✅ Working tools: {successful_calls}")
    
    if healthcare_responses:
        print(f"\n🎯 Healthcare Data Found:")
        for resp in healthcare_responses:
            print(f"  📋 {resp['tool']}: Contains Thai healthcare content")
    
    return successful_calls, healthcare_responses

def _contains_healthcare_content(text):
    """Check if text contains Thai healthcare content"""
    healthcare_keywords = [
        'สิทธิ', 'ประกัน', 'สุขภาพ', 'บัตร', 'ทอง', 
        '30', 'บาท', 'รักษา', 'โรค', 'แพทย์', 'หมอ',
        'ก', 'ข', 'ค', 'ง'  # Thai choices
    ]
    
    text_lower = text.lower()
    return any(keyword in text for keyword in healthcare_keywords)

def test_specific_question():
    """Test with the specific problematic question"""
    print(f"\n🏥 Testing Specific Healthcare Question")
    print("-" * 45)
    
    url = "https://mcp-hackathon.cmkl.ai/mcp"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    question = "สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ?"
    
    # Try different ways to ask the question
    approaches = [
        {
            "tool": "emergency_patient_lookup",
            "args": {"identifier": question}
        },
        {
            "tool": "lookup_patient", 
            "args": {"patient_id": question}
        },
        { 
            "tool": "search_patients",
            "args": {"search_term": "สิทธิประกันสุखภาพแห่งชาติ"}
        },
        {
            "tool": "list_all_departments",
            "args": {}
        }
    ]
    
    print(f"🔍 Question: {question[:50]}...")
    
    for i, approach in enumerate(approaches):
        print(f"\n📋 Approach {i+1}: {approach['tool']}")
        
        request_data = {
            "jsonrpc": "2.0",
            "id": 100 + i,
            "method": "tools/call", 
            "params": {
                "name": approach['tool'],
                "arguments": approach['args']
            }
        }
        
        try:
            response = requests.post(url, json=request_data, headers=headers, timeout=15)
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ Got response!")
                
                # Look for Thai choices in response
                response_text = response.text
                thai_choices = []
                for choice in ['ก', 'ข', 'ค', 'ง']:
                    if choice in response_text:
                        thai_choices.append(choice)
                
                if thai_choices:
                    print(f"  🎯 Found Thai choices: {thai_choices}")
                    print(f"  📄 Response preview: {response_text[:200]}...")
                    
                    return {
                        'tool': approach['tool'],
                        'choices': thai_choices,
                        'response': response_text
                    }
                else:
                    print(f"  📄 No choices found: {response_text[:100]}...")
            else:
                print(f"  ❌ Error: {response.text[:100]}...")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    return None

def main():
    print("🌐 JSON-RPC Without Session Testing")
    print("=" * 45)
    
    # Test basic tools
    working_tools, healthcare_data = test_jsonrpc_no_session() 
    
    if working_tools:
        print(f"\n🎉 SUCCESS! Found working tools without session")
        
        # Test specific healthcare question
        question_result = test_specific_question()
        
        if question_result:
            print(f"\n✅ Successfully got data for healthcare question!")
            print(f"Best approach: {question_result['tool']}")
            print(f"Found choices: {question_result['choices']}")
        
        print(f"\n🚀 Ready to integrate into comprehensive MCP client!")
        
    else:
        print(f"\n❌ No tools working yet")
        print(f"💡 May need authentication or different server setup")

if __name__ == "__main__":
    main()