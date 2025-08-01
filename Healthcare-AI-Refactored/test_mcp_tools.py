#!/usr/bin/env python3
"""
Test script to verify MCP tool selection works correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_mcp_tool_selection():
    """Test MCP tool selection based on query content."""
    try:
        print("Testing MCP tool selection...")
        
        from src.infrastructure.connectors.MCPConnector import MCPConnector
        
        # Create connector
        connector = MCPConnector("https://mcp-hackathon.cmkl.ai/mcp")
        
        # Test queries and expected tools
        test_queries = [
            # Department queries
            ("แผนกไหนที่ให้บริการโรคหัวใจ?", "list_all_departments"),
            ("What services does cardiology offer?", "get_department_services"),
            ("Get department information", "get_department_info"),
            
            # Patient queries
            ("I need to find patient information", "lookup_patient"),
            ("Search for patients by name", "search_patients"),
            ("Create new patient", "create_patient"),
            ("Emergency patient lookup", "emergency_patient_lookup"),
            ("Get medical history", "get_medical_history"),
            ("Add medication to patient", "add_medication"),
            ("Add vital signs", "add_vital_signs"),
            ("Check food allergies", "check_food_allergies"),
            ("Check drug allergies", "check_drug_allergies"),
            ("Get allergy alternatives", "get_allergy_alternatives"),
            
            # Appointment queries
            ("Schedule appointment", "schedule_appointment"),
            ("Book appointment", "book_appointment_with_availability_check"),
            ("Find next available appointment", "find_next_available_appointment"),
            ("Cancel appointment", "cancel_appointment"),
            ("Get doctor schedule", "get_doctor_schedule"),
            ("Check doctor availability", "check_doctor_availability"),
            ("Find available doctors", "find_available_doctors"),
            
            # Doctor and staff queries
            ("Get doctor information", "get_doctor_info"),
            ("Search doctors", "search_doctors"),
            ("Get staff information", "get_staff_info"),
            ("List staff by department", "list_staff_by_department"),
            ("Who are the doctors in neurology?", "get_department_staff"),
            
            # Room queries
            ("Check room availability", "get_room_info"),
            ("Find available rooms", "find_available_rooms"),
            ("Get room equipment", "get_room_equipment"),
            ("Update room status", "update_room_status"),
            
            # Queue queries
            ("Book queue", "book_queue"),
            ("Check queue status", "check_queue_status"),
            ("Get department queue status", "get_department_queue_status"),
            
            # Lab queries
            ("Get lab results", "get_lab_results"),
            ("Add lab result", "add_lab_result"),
            
            # Default fallback
            ("General question about hospital", "list_all_departments")
        ]
        
        print("\nTesting tool selection:")
        for query, expected_tool in test_queries:
            selected_tool = connector.select_appropriate_tool(query)
            status = "✅" if selected_tool == expected_tool else "❌"
            print(f"{status} Query: '{query[:50]}...' -> Tool: {selected_tool} (expected: {expected_tool})")
        
        return True
        
    except Exception as e:
        print(f"Error testing MCP tool selection: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mcp_connection():
    """Test MCP connection with tool selection."""
    try:
        print("\nTesting MCP connection with tool selection...")
        
        from src.infrastructure.connectors.MCPConnector import MCPConnector
        
        # Create connector
        connector = MCPConnector("https://mcp-hackathon.cmkl.ai/mcp")
        
        # Test availability
        available = connector.is_available()
        print(f"MCP connector available: {available}")
        
        if available:
            # Test a query that should select list_all_departments
            test_query = "แผนกไหนที่ให้บริการโรคหัวใจ?"
            selected_tool = connector.select_appropriate_tool(test_query)
            print(f"Query: '{test_query}' -> Selected tool: {selected_tool}")
            
            # Test the actual MCP call
            test_request = [{
                'endpoint': selected_tool,
                'params': {
                    'name': selected_tool,
                    'arguments': {},
                    'query': test_query
                }
            }]
            
            result = connector.fetch(test_request)
            print(f"MCP call result: {result}")
            
        return True
        
    except Exception as e:
        print(f"Error testing MCP connection: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("MCP TOOL SELECTION TEST")
    print("=" * 60)
    
    # Test tool selection
    tool_success = test_mcp_tool_selection()
    
    # Test MCP connection
    connection_success = test_mcp_connection()
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Tool Selection: {'✅ PASS' if tool_success else '❌ FAIL'}")
    print(f"MCP Connection: {'✅ PASS' if connection_success else '❌ FAIL'}")
    print("=" * 60) 