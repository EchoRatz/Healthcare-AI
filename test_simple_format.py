#!/usr/bin/env python3
"""
Test Simple MCP Format
======================

Use the exact format the user provided - no jsonrpc, no id, no session
"""

import requests
import json

def test_simple_format():
    """Test with the exact simple format"""
    print("🧪 Testing Simple MCP Format")
    print("=" * 35)
    print("Using exact format from user's example")
    
    url = "https://mcp-hackathon.cmkl.ai/mcp"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    # Test cases using EXACT format from user
    test_cases = [
        {
            "name": "lookup_patient (empty)",
            "request": {
                "method": "tools/call",
                "params": {
                    "name": "lookup_patient",
                    "arguments": {
                        "patient_id": ""
                    }
                }
            }
        },
        {
            "name": "lookup_patient (healthcare)",
            "request": {
                "method": "tools/call",
                "params": {
                    "name": "lookup_patient",
                    "arguments": {
                        "patient_id": "สิทธิประกันสุขภาพแห่งชาติ"
                    }
                }
            }
        },
        {
            "name": "list_all_departments",
            "request": {
                "method": "tools/call",
                "params": {
                    "name": "list_all_departments",
                    "arguments": {}
                }
            }
        },
        {
            "name": "emergency_patient_lookup",
            "request": {
                "method": "tools/call", 
                "params": {
                    "name": "emergency_patient_lookup",
                    "arguments": {
                        "identifier": "สิทธิบัตรทอง"
                    }
                }
            }
        },
        {
            "name": "search_patients",
            "request": {
                "method": "tools/call",
                "params": {
                    "name": "search_patients",
                    "arguments": {
                        "search_term": "สิทธิประกัน"
                    }
                }
            }
        }
    ]
    
    successful_calls = []
    healthcare_content = []
    
    for test_case in test_cases:
        print(f"\n📋 Testing: {test_case['name']}")
        
        try:
            response = requests.post(url, json=test_case['request'], headers=headers, timeout=15)
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ SUCCESS!")
                
                # Try to parse response
                response_text = response.text.strip()
                
                # Handle SSE format
                if response_text.startswith('event:') or 'data:' in response_text:
                    print(f"  📡 SSE Response detected")
                    
                    # Extract data line
                    lines = response_text.split('\n')
                    data_line = None
                    for line in lines:
                        if line.startswith('data: '):
                            data_line = line[6:]
                            break
                    
                    if data_line:
                        try:
                            data = json.loads(data_line)
                            print(f"  📄 Data: {json.dumps(data, indent=2)[:300]}...")
                            
                            # Check for healthcare content
                            data_str = str(data)
                            thai_keywords = ['สิทธิ', 'ประกัน', 'บัตร', 'ทอง', 'สุขภาพ']
                            choice_keywords = ['ก', 'ข', 'ค', 'ง']
                            
                            found_thai = [kw for kw in thai_keywords if kw in data_str]
                            found_choices = [kw for kw in choice_keywords if kw in data_str]
                            
                            if found_thai or found_choices:
                                print(f"  🎯 Healthcare content found!")
                                if found_thai:
                                    print(f"    Thai terms: {found_thai}")
                                if found_choices:
                                    print(f"    Choices: {found_choices}")
                                healthcare_content.append({
                                    "tool": test_case['name'],
                                    "thai_terms": found_thai,
                                    "choices": found_choices,
                                    "data": data
                                })
                            
                            successful_calls.append(test_case['name'])
                            
                        except json.JSONDecodeError:
                            print(f"  📄 Data (non-JSON): {data_line[:100]}...")
                            successful_calls.append(test_case['name'])
                    else:
                        print(f"  📄 SSE without data line: {response_text[:100]}...")
                        successful_calls.append(test_case['name'])
                
                else:
                    # Try direct JSON
                    try:
                        data = response.json()
                        print(f"  📄 JSON: {json.dumps(data, indent=2)[:300]}...")
                        successful_calls.append(test_case['name'])
                    except:
                        print(f"  📄 Text: {response_text[:150]}...")
                        successful_calls.append(test_case['name'])
                        
            else:
                error_text = response.text[:150]
                print(f"  ❌ HTTP {response.status_code}: {error_text}...")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:50]}...")
    
    print(f"\n📊 Test Results:")
    print(f"  Successful calls: {len(successful_calls)}/{len(test_cases)}")
    print(f"  Working tools: {successful_calls}")
    print(f"  Healthcare content found: {len(healthcare_content)} tools")
    
    if healthcare_content:
        print(f"\n🎯 Healthcare Content Summary:")
        for content in healthcare_content:
            print(f"  {content['tool']}:")
            if content['thai_terms']:
                print(f"    Thai: {content['thai_terms']}")
            if content['choices']:
                print(f"    Choices: {content['choices']}")
    
    return successful_calls, healthcare_content

def create_working_client_template(successful_tools, healthcare_data):
    """Create template for working MCP client"""
    print(f"\n🔧 Creating Working Client Template")
    print("-" * 40)
    
    if not successful_tools:
        print("❌ No working tools found")
        return
    
    template = f'''# Working MCP Client Configuration
# Based on successful tests

URL = "https://mcp-hackathon.cmkl.ai/mcp"
HEADERS = {{
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
}}

# Request Format (NO jsonrpc, NO id, NO session)
REQUEST_TEMPLATE = {{
    "method": "tools/call",
    "params": {{
        "name": "TOOL_NAME",
        "arguments": {{
            # Tool-specific arguments
        }}
    }}
}}

# Working Tools ({len(successful_tools)} confirmed):
WORKING_TOOLS = {successful_tools}

# Healthcare-relevant tools:
HEALTHCARE_TOOLS = {[hc['tool'] for hc in healthcare_data]}
'''
    
    print(template)
    
    # Save to file
    with open('working_mcp_config.py', 'w', encoding='utf-8') as f:
        f.write(template)
    
    print(f"✅ Saved to working_mcp_config.py")

def main():
    print("🌐 Simple MCP Format Testing")
    print("=" * 35)
    print("Using exact format from user's example (no jsonrpc/id/session)")
    
    successful_tools, healthcare_data = test_simple_format()
    
    if successful_tools:
        print(f"\n🎉 SUCCESS! Found working MCP format")
        create_working_client_template(successful_tools, healthcare_data)
        
        print(f"\n🚀 Next Steps:")
        print(f"  1. Update comprehensive_mcp_client.py with simple format")
        print(f"  2. Integrate working tools into ultra_fast_llama31.py")
        print(f"  3. Test healthcare question validation")
        print(f"  4. Fix logical contradictions in answers")
        
    else:
        print(f"\n❌ Still no working format found")
        print(f"💡 May need authentication or server-specific setup")

if __name__ == "__main__":
    main()