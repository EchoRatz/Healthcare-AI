#!/usr/bin/env python3
"""
Quick MCP Test with Exact Format
=================================

Test the exact API format the user provided
"""

import requests
import json

def test_exact_format():
    """Test with the exact format provided by user"""
    print("🔍 Testing Exact MCP Format")
    print("=" * 30)
    
    # The exact format the user provided
    request_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "lookup_patient",
            "arguments": {
                "patient_id": ""
            }
        }
    }
    
    # Test with different patient_id values
    test_values = [
        "",  # Empty as in example
        "test_patient",
        "healthcare_policy_question",
        "สิทธิประกันสุขภาพแห่งชาติ",
        "สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ?"
    ]
    
    server_url = "https://mcp-hackathon.cmkl.ai"
    endpoints = ["/message", "/mcp", "/api/mcp"]
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    for endpoint in endpoints:
        url = f"{server_url}{endpoint}"
        print(f"\n🌐 Testing: {url}")
        
        for i, patient_id in enumerate(test_values):
            # Update the patient_id
            request_data["params"]["arguments"]["patient_id"] = patient_id
            request_data["id"] = i + 1
            
            print(f"  📋 Test {i+1}: patient_id = '{patient_id[:30]}{'...' if len(patient_id) > 30 else ''}'")
            
            try:
                response = requests.post(url, json=request_data, headers=headers, timeout=10)
                
                print(f"    Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        if "result" in data:
                            result = data["result"]
                            print(f"    ✅ Success! Type: {type(result).__name__}")
                            print(f"    📄 Preview: {str(result)[:100]}...")
                            
                            # Check for Thai healthcare content
                            if any(keyword in str(result) for keyword in ['สิทธิ', 'ประกัน', 'สุขภาพ']):
                                print(f"    🎯 Contains Thai healthcare content!")
                                
                        elif "error" in data:
                            error = data["error"]
                            print(f"    ❌ Error: {error.get('message', 'Unknown')}")
                            print(f"    Code: {error.get('code', 'N/A')}")
                        
                        return True  # Found working endpoint
                        
                    except json.JSONDecodeError:
                        print(f"    📄 Non-JSON response: {response.text[:100]}...")
                        
                elif response.status_code == 404:
                    print(f"    ❌ Not Found")
                    break  # Try next endpoint
                    
                else:
                    print(f"    ❌ HTTP {response.status_code}: {response.text[:50]}...")
                    
            except requests.exceptions.Timeout:
                print(f"    ⏰ Timeout")
            except requests.exceptions.RequestException as e:
                print(f"    ❌ Request error: {str(e)[:50]}...")
    
    return False

def test_postman_format():
    """Show the exact format for Postman testing"""
    print("\n📮 Postman Test Format")
    print("-" * 25)
    
    print("URL: https://mcp-hackathon.cmkl.ai/message")
    print("Method: POST")
    print("Headers:")
    print("  Content-Type: application/json")
    print("  Accept: application/json")
    print()
    print("Body (JSON):")
    
    postman_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "lookup_patient",
            "arguments": {
                "patient_id": "สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ?"
            }
        }
    }
    
    print(json.dumps(postman_request, indent=2, ensure_ascii=False))
    
    print("\n💡 Try these patient_id variations:")
    variations = [
        '""',  # Empty
        '"test_patient"',
        '"healthcare_policy"',
        '"สิทธิประกันสุขภาพ"',
        '"ก. สิทธิหลักประกันสุขภาพแห่งชาติ ข. สิทธิบัตรทอง ค. สิทธิ 30 บาทรักษาทุกโรค ง. ไม่มีข้อใดถูกต้อง"'
    ]
    
    for var in variations:
        print(f"  - {var}")

def main():
    """Main test function"""
    print("🧪 Quick MCP API Test")
    print("=" * 25)
    
    # Test with the exact format
    success = test_exact_format()
    
    if success:
        print(f"\n✅ MCP API is accessible!")
        print(f"🔧 Update mcp_healthcare_client.py with working endpoint")
    else:
        print(f"\n❌ Could not connect to MCP API")
        print(f"💡 Try manually with Postman:")
        
    # Show Postman format regardless
    test_postman_format()
    
    print(f"\n🎯 Next Steps:")
    print(f"  1. Test manually in Postman with the format above")
    print(f"  2. Note which patient_id values return useful data")
    print(f"  3. Update MCP client with successful patterns")
    print(f"  4. Run full integration test")

if __name__ == "__main__":
    main()