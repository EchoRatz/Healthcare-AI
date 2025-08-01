#!/usr/bin/env python3
"""
Test MCP API with Actual Format
===============================

Test the CMKL MCP server using the exact API format provided
"""

import asyncio
import aiohttp
import json
import sys

async def test_mcp_api():
    """Test MCP server with actual API format"""
    print("🔍 Testing CMKL MCP Server API")
    print("=" * 35)
    
    server_url = "https://mcp-hackathon.cmkl.ai"
    
    # Test requests based on the example format
    test_requests = [
        {
            "name": "Initialize Connection",
            "request": {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "clientInfo": {
                        "name": "healthcare-test-client",
                        "version": "1.0.0"
                    },
                    "capabilities": {
                        "tools": {"listChanged": True}
                    }
                }
            }
        },
        {
            "name": "List Available Tools",
            "request": {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
        },
        {
            "name": "Test lookup_patient Tool",
            "request": {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "lookup_patient",
                    "arguments": {
                        "patient_id": "healthcare_policy_test"
                    }
                }
            }
        },
        {
            "name": "Test Healthcare Question",
            "request": {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "lookup_patient",
                    "arguments": {
                        "patient_id": "สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ?"
                    }
                }
            }
        }
    ]
    
    # Try different endpoints
    endpoints = ["/message", "/mcp", "/api/mcp", "/"]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            url = f"{server_url}{endpoint}"
            print(f"\n🌐 Testing endpoint: {url}")
            
            success_count = 0
            
            for test in test_requests:
                print(f"\n📋 {test['name']}:")
                
                try:
                    headers = {
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    }
                    
                    async with session.post(
                        url, 
                        json=test['request'], 
                        headers=headers, 
                        timeout=10
                    ) as response:
                        
                        print(f"  Status: {response.status}")
                        
                        if response.status == 200:
                            try:
                                data = await response.json()
                                print(f"  ✅ Success!")
                                
                                # Pretty print key parts of response
                                if "result" in data:
                                    result = data["result"]
                                    if isinstance(result, dict):
                                        for key, value in result.items():
                                            if isinstance(value, (str, int, float, bool)):
                                                print(f"    {key}: {value}")
                                            elif isinstance(value, list) and len(value) <= 3:
                                                print(f"    {key}: {value}")
                                            else:
                                                print(f"    {key}: {type(value).__name__} ({len(str(value))} chars)")
                                    else:
                                        print(f"    Result: {str(result)[:100]}...")
                                
                                elif "error" in data:
                                    error = data["error"]
                                    print(f"  ❌ Error: {error.get('message', 'Unknown error')}")
                                    if "code" in error:
                                        print(f"    Code: {error['code']}")
                                
                                success_count += 1
                                
                            except json.JSONDecodeError:
                                text = await response.text()
                                print(f"  📄 Response: {text[:200]}...")
                                
                        elif response.status == 404:
                            print(f"  ❌ Not Found - trying next endpoint")
                            break
                        
                        else:
                            text = await response.text()
                            print(f"  ❌ HTTP {response.status}: {text[:100]}...")
                            
                except asyncio.TimeoutError:
                    print(f"  ⏰ Timeout")
                except Exception as e:
                    print(f"  ❌ Error: {str(e)[:100]}")
            
            if success_count > 0:
                print(f"\n🎉 Found working endpoint: {url}")
                print(f"📊 Successful requests: {success_count}/{len(test_requests)}")
                return url
            
    print(f"\n❌ No working endpoints found")
    return None

async def test_specific_healthcare_question():
    """Test with your specific problematic question"""
    print("\n🏥 Testing Specific Healthcare Question")
    print("-" * 40)
    
    question = "สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ?"
    choices = "ก. สิทธิหลักประกันสุขภาพแห่งชาติ ข. สิทธิบัตรทอง ค. สิทธิ 30 บาทรักษาทุกโรค ง. ไม่มีข้อใดถูกต้อง"
    
    # Different ways to format the healthcare question
    test_formats = [
        {"patient_id": question},
        {"patient_id": f"Q: {question} Choices: {choices}"},
        {"patient_id": f"healthcare_policy: {question[:50]}"},
        {"patient_id": "thai_healthcare_rights_question"}
    ]
    
    server_url = "https://mcp-hackathon.cmkl.ai"
    endpoints = ["/message", "/mcp"]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            url = f"{server_url}{endpoint}"
            
            for i, arguments in enumerate(test_formats):
                print(f"\n📋 Format {i+1}: {list(arguments.keys())[0]} = {str(list(arguments.values())[0])[:50]}...")
                
                request = {
                    "jsonrpc": "2.0",
                    "id": 100 + i,
                    "method": "tools/call",
                    "params": {
                        "name": "lookup_patient",
                        "arguments": arguments
                    }
                }
                
                try:
                    async with session.post(url, json=request, timeout=15) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            if "result" in data:
                                print(f"  ✅ Success! Response type: {type(data['result'])}")
                                result = data['result']
                                
                                # Look for Thai healthcare-related content
                                result_str = str(result).lower()
                                healthcare_keywords = ['สิทธิ', 'ประกัน', 'สุขภาพ', 'บัตร', 'ทอง', 'ก', 'ข', 'ค', 'ง']
                                found_keywords = [kw for kw in healthcare_keywords if kw in result_str]
                                
                                if found_keywords:
                                    print(f"  🎯 Healthcare content detected: {found_keywords}")
                                
                                print(f"  📄 Response preview: {str(result)[:150]}...")
                                
                            elif "error" in data:
                                print(f"  ❌ Error: {data['error'].get('message', 'Unknown')}")
                            
                        else:
                            print(f"  ❌ HTTP {response.status}")
                            
                except Exception as e:
                    print(f"  ❌ Request failed: {str(e)[:50]}")

def main():
    """Main test function"""
    print("🧪 MCP API Testing Suite")
    print("=" * 30)
    print("Testing CMKL MCP server with actual API format")
    print()
    
    try:
        # Test basic API connectivity
        working_url = asyncio.run(test_mcp_api())
        
        if working_url:
            # Test healthcare-specific queries
            asyncio.run(test_specific_healthcare_question())
        else:
            print("❌ Could not establish basic connectivity")
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
    
    print(f"\n💡 Next Steps:")
    print(f"  1. Use working endpoint in mcp_healthcare_client.py")
    print(f"  2. Adapt arguments based on successful formats")
    print(f"  3. Update validation logic for response parsing")
    print(f"  4. Test full integration with ultra_fast_llama31.py")

if __name__ == "__main__":
    main()