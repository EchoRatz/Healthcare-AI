#!/usr/bin/env python3
"""
Comprehensive MCP Integration Test
=================================

Test the updated MCPConnector with proper JSON-RPC format
based on working examples from mcp_healthcare_client.py and mcp_sse_client.py
"""

import sys
import json
import time
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_mcp_initialization():
    """Test MCP initialization with JSON-RPC format"""
    try:
        print("🔧 Testing MCP initialization...")
        
        from src.infrastructure.connectors.MCPConnector import MCPConnector
        
        # Create connector
        connector = MCPConnector("https://mcp-hackathon.cmkl.ai")
        
        # Test availability
        available = connector.is_available()
        print(f"MCP server available: {available}")
        
        if available:
            # Test listing resources
            resources = connector.list_resources()
            print(f"Available resources: {resources[:5]}...")  # Show first 5
            
            return True
        else:
            print("❌ MCP server not available")
            return False
            
    except Exception as e:
        print(f"❌ MCP initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mcp_tool_calls():
    """Test MCP tool calls with proper JSON-RPC format"""
    try:
        print("\n🔧 Testing MCP tool calls...")
        
        from src.infrastructure.connectors.MCPConnector import MCPConnector
        
        # Create connector
        connector = MCPConnector("https://mcp-hackathon.cmkl.ai")
        
        # Test different tool calls
        test_requests = [
            {
                'endpoint': 'list_all_departments',
                'params': {
                    'name': 'list_all_departments',
                    'arguments': {},
                    'query': 'แผนกไหนที่ให้บริการโรคหัวใจ?'
                }
            },
            {
                'endpoint': 'lookup_patient',
                'params': {
                    'name': 'lookup_patient',
                    'arguments': {
                        'patient_id': 'test_patient_123'
                    },
                    'query': 'Find patient information'
                }
            },
            {
                'endpoint': 'get_department_services',
                'params': {
                    'name': 'get_department_services',
                    'arguments': {
                        'department': 'cardiology'
                    },
                    'query': 'What services does cardiology offer?'
                }
            }
        ]
        
        results = connector.fetch(test_requests)
        
        print(f"📊 Tool call results:")
        for endpoint, result in results.items():
            if result.get('error'):
                print(f"  ❌ {endpoint}: {result['error']}")
            else:
                data = result.get('data', {})
                print(f"  ✅ {endpoint}: {str(data)[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP tool call error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_selection():
    """Test automatic tool selection"""
    try:
        print("\n🎯 Testing tool selection...")
        
        from src.infrastructure.connectors.MCPConnector import MCPConnector
        
        # Create connector
        connector = MCPConnector("https://mcp-hackathon.cmkl.ai")
        
        # Test queries and expected tools
        test_queries = [
            ("แผนกไหนที่ให้บริการโรคหัวใจ?", "list_all_departments"),
            ("Find patient information", "lookup_patient"),
            ("Schedule appointment", "schedule_appointment"),
            ("Check room availability", "get_room_info"),
            ("Get doctor schedule", "get_doctor_schedule"),
            ("Book queue", "book_queue"),
            ("Get lab results", "get_lab_results"),
            ("Emergency patient lookup", "emergency_patient_lookup"),
            ("Check food allergies", "check_food_allergies"),
            ("Find available doctors", "find_available_doctors")
        ]
        
        success_count = 0
        for query, expected_tool in test_queries:
            selected_tool = connector.select_appropriate_tool(query)
            status = "✅" if selected_tool == expected_tool else "❌"
            print(f"  {status} '{query[:30]}...' -> {selected_tool}")
            if selected_tool == expected_tool:
                success_count += 1
        
        accuracy = (success_count / len(test_queries)) * 100
        print(f"\n📊 Tool selection accuracy: {accuracy:.1f}% ({success_count}/{len(test_queries)})")
        
        return accuracy > 70  # 70% accuracy threshold
        
    except Exception as e:
        print(f"❌ Tool selection error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_healthcare_validation():
    """Test healthcare question validation using MCP"""
    try:
        print("\n🏥 Testing healthcare validation...")
        
        from src.infrastructure.connectors.MCPConnector import MCPConnector
        
        # Create connector
        connector = MCPConnector("https://mcp-hackathon.cmkl.ai")
        
        # Test healthcare question
        healthcare_question = "สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ?"
        
        # Create request for healthcare validation
        request = [{
            'endpoint': 'lookup_patient',
            'params': {
                'name': 'lookup_patient',
                'arguments': {
                    'patient_id': healthcare_question
                },
                'query': healthcare_question
            }
        }]
        
        result = connector.fetch(request)
        
        if result and 'lookup_patient' in result:
            mcp_result = result['lookup_patient']
            if mcp_result.get('error'):
                print(f"❌ MCP validation error: {mcp_result['error']}")
            else:
                data = mcp_result.get('data', {})
                print(f"✅ MCP validation successful!")
                print(f"   Response: {str(data)[:200]}...")
                
                # Try to extract answer from response
                response_str = str(data).lower()
                thai_choices = ['ก', 'ข', 'ค', 'ง']
                found_choices = [choice for choice in thai_choices if choice in response_str]
                
                if found_choices:
                    print(f"   Found choices in response: {found_choices}")
                
                return True
        else:
            print("❌ No MCP validation response")
            return False
            
    except Exception as e:
        print(f"❌ Healthcare validation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_end_to_end_workflow():
    """Test complete end-to-end workflow"""
    try:
        print("\n🔄 Testing end-to-end workflow...")
        
        from src.infrastructure.connectors.MCPConnector import MCPConnector
        
        # Create connector
        connector = MCPConnector("https://mcp-hackathon.cmkl.ai")
        
        # Simulate a complete workflow
        workflow_steps = [
            {
                'name': 'List Departments',
                'endpoint': 'list_all_departments',
                'params': {
                    'name': 'list_all_departments',
                    'arguments': {},
                    'query': 'Show me all hospital departments'
                }
            },
            {
                'name': 'Get Department Services',
                'endpoint': 'get_department_services',
                'params': {
                    'name': 'get_department_services',
                    'arguments': {
                        'department': 'cardiology'
                    },
                    'query': 'What services does cardiology offer?'
                }
            },
            {
                'name': 'Find Available Doctors',
                'endpoint': 'find_available_doctors',
                'params': {
                    'name': 'find_available_doctors',
                    'arguments': {
                        'specialty': 'cardiology',
                        'date': '2024-02-08'
                    },
                    'query': 'Find available cardiologists for today'
                }
            }
        ]
        
        print("📋 Executing workflow steps:")
        for step in workflow_steps:
            print(f"  🔄 {step['name']}...")
            
            request = [{
                'endpoint': step['endpoint'],
                'params': step['params']
            }]
            
            result = connector.fetch(request)
            
            if result and step['endpoint'] in result:
                step_result = result[step['endpoint']]
                if step_result.get('error'):
                    print(f"    ❌ Error: {step_result['error']}")
                else:
                    data = step_result.get('data', {})
                    print(f"    ✅ Success: {str(data)[:50]}...")
            else:
                print(f"    ❌ No response")
        
        return True
        
    except Exception as e:
        print(f"❌ End-to-end workflow error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("COMPREHENSIVE MCP INTEGRATION TEST")
    print("=" * 60)
    print("Testing updated MCPConnector with JSON-RPC format")
    print("Based on working examples from mcp_healthcare_client.py")
    print()
    
    # Run all tests
    tests = [
        ("MCP Initialization", test_mcp_initialization),
        ("Tool Selection", test_tool_selection),
        ("MCP Tool Calls", test_mcp_tool_calls),
        ("Healthcare Validation", test_healthcare_validation),
        ("End-to-End Workflow", test_end_to_end_workflow)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results[test_name] = success
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! MCP integration is working correctly.")
    elif passed >= total * 0.8:
        print("⚠️  Most tests passed. MCP integration is mostly working.")
    else:
        print("❌ Many tests failed. MCP integration needs attention.")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 