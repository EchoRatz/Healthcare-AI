#!/usr/bin/env python3
"""
CMKL MCP Client
===============

Uses the exact API request formats from Raw_Body_MCP.txt
to properly connect to the CMKL MCP healthcare server.
"""

import json
import requests
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class CMKLResponse:
    """CMKL MCP server response"""
    success: bool
    data: Any = None
    error: str = None
    tool_name: str = None

class CMKLMCPClient:
    """Client for CMKL MCP Healthcare Server using exact Raw_Body_MCP formats"""
    
    def __init__(self, server_url: str = "https://mcp-hackathon.cmkl.ai/mcp"):
        self.server_url = server_url
        self.session = None
        # Generate session ID for CMKL server
        import uuid
        self.session_id = str(uuid.uuid4())
        
        # All 37 available tools from Raw_Body_MCP.txt
        self.available_tools = [
            "lookup_patient", "search_patients", "create_patient", "get_medical_history",
            "add_vital_signs", "add_medication", "add_allergy", "get_appointments",
            "schedule_appointment", "get_lab_results", "add_lab_result", "get_staff_info",
            "list_staff_by_department", "emergency_patient_lookup", "get_doctor_info",
            "search_doctors", "get_doctor_schedule", "check_doctor_availability",
            "get_department_info", "list_all_departments", "get_department_staff",
            "get_department_services", "get_room_info", "find_available_rooms",
            "get_room_equipment", "update_room_status", "book_queue", "check_queue_status",
            "get_department_queue_status", "check_food_allergies", "check_drug_allergies",
            "get_allergy_alternatives", "find_available_doctors", 
            "book_appointment_with_doctor_recommendation", "book_appointment_with_availability_check",
            "find_next_available_appointment", "cancel_appointment"
        ]
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> CMKLResponse:
        """Call a tool using Raw_Body_MCP format wrapped in JSON-RPC 2.0"""
        if tool_name not in self.available_tools:
            return CMKLResponse(
                success=False, 
                error=f"Tool '{tool_name}' not available. Available: {self.available_tools[:5]}...",
                tool_name=tool_name
            )
        
        # Wrap Raw_Body_MCP format in proper JSON-RPC 2.0
        request_body = {
            "jsonrpc": "2.0",
            "id": f"tool-{tool_name}-{hash(str(arguments))}",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "X-Session-ID": self.session_id,  # Try session ID in headers
                "Session-ID": self.session_id,  # Alternative header name
                "Authorization": f"Session {self.session_id}"  # Another attempt
            }
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.post(
                self.server_url, 
                json=request_body, 
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    
                    if 'text/event-stream' in content_type:
                        # Handle Server-Sent Events
                        text_data = await response.text()
                        return self._parse_sse_response(text_data, tool_name)
                    else:
                        # Handle regular JSON
                        data = await response.json()
                        return CMKLResponse(success=True, data=data, tool_name=tool_name)
                else:
                    error_text = await response.text()
                    return CMKLResponse(
                        success=False, 
                        error=f"HTTP {response.status}: {error_text}",
                        tool_name=tool_name
                    )
                    
        except Exception as e:
            return CMKLResponse(
                success=False, 
                error=f"Request failed: {str(e)}",
                tool_name=tool_name
            )
    
    def _parse_sse_response(self, sse_data: str, tool_name: str) -> CMKLResponse:
        """Parse Server-Sent Events response"""
        try:
            lines = sse_data.strip().split('\n')
            for line in lines:
                if line.startswith('data: '):
                    json_str = line[6:]  # Remove "data: " prefix
                    if json_str.strip():
                        data = json.loads(json_str)
                        
                        if "error" in data:
                            return CMKLResponse(
                                success=False, 
                                error=data["error"].get("message", "Unknown error"),
                                tool_name=tool_name
                            )
                        elif "result" in data:
                            return CMKLResponse(
                                success=True, 
                                data=data["result"],
                                tool_name=tool_name
                            )
            
            return CMKLResponse(
                success=False, 
                error="No valid data found in SSE stream",
                tool_name=tool_name
            )
            
        except json.JSONDecodeError as e:
            return CMKLResponse(
                success=False, 
                error=f"Failed to parse SSE JSON: {e}",
                tool_name=tool_name
            )
    
    # Healthcare-specific tool methods using Raw_Body_MCP formats
    
    async def lookup_patient(self, patient_id: str) -> CMKLResponse:
        """Lookup patient by ID"""
        return await self.call_tool("lookup_patient", {"patient_id": patient_id})
    
    async def search_patients(self, search_term: str) -> CMKLResponse:
        """Search patients by term"""
        return await self.call_tool("search_patients", {"search_term": search_term})
    
    async def get_medical_history(self, patient_id: str) -> CMKLResponse:
        """Get patient medical history"""
        return await self.call_tool("get_medical_history", {"patient_id": patient_id})
    
    async def search_doctors(self, specialty: str = None, department: str = None) -> CMKLResponse:
        """Search doctors by specialty or department"""
        return await self.call_tool("search_doctors", {
            "specialty": specialty,
            "department": department
        })
    
    async def list_all_departments(self) -> CMKLResponse:
        """List all hospital departments"""
        return await self.call_tool("list_all_departments", {})
    
    async def get_department_info(self, dept_id: str) -> CMKLResponse:
        """Get department information"""
        return await self.call_tool("get_department_info", {"dept_id": dept_id})
    
    async def emergency_patient_lookup(self, identifier: str) -> CMKLResponse:
        """Emergency patient lookup"""
        return await self.call_tool("emergency_patient_lookup", {"identifier": identifier})
    
    async def check_food_allergies(self, patient_id: str, food_items: str) -> CMKLResponse:
        """Check patient food allergies"""
        return await self.call_tool("check_food_allergies", {
            "patient_id": patient_id,
            "food_items": food_items
        })
    
    async def check_drug_allergies(self, patient_id: str, medications: str) -> CMKLResponse:
        """Check patient drug allergies"""
        return await self.call_tool("check_drug_allergies", {
            "patient_id": patient_id,
            "medications": medications
        })

# Test the CMKL MCP client
async def test_cmkl_mcp():
    """Test CMKL MCP client with Real_Body_MCP formats"""
    print("🧪 Testing CMKL MCP Client with Raw_Body_MCP formats")
    print("=" * 60)
    
    async with CMKLMCPClient() as client:
        
        # Test 1: List all departments (no args)
        print("📋 Test 1: List all departments")
        result = await client.list_all_departments()
        print(f"   Success: {result.success}")
        if result.success:
            print(f"   Data: {result.data}")
        else:
            print(f"   Error: {result.error}")
        
        print()
        
        # Test 2: Search doctors
        print("👨‍⚕️ Test 2: Search doctors")
        result = await client.search_doctors(specialty="cardiology")
        print(f"   Success: {result.success}")
        if result.success:
            print(f"   Data: {result.data}")
        else:
            print(f"   Error: {result.error}")
        
        print()
        
        # Test 3: Patient lookup
        print("👤 Test 3: Patient lookup")
        result = await client.lookup_patient("test123")
        print(f"   Success: {result.success}")
        if result.success:
            print(f"   Data: {result.data}")
        else:
            print(f"   Error: {result.error}")
        
        print()
        
        # Test 4: Emergency lookup
        print("🚨 Test 4: Emergency patient lookup")
        result = await client.emergency_patient_lookup("emergency123")
        print(f"   Success: {result.success}")
        if result.success:
            print(f"   Data: {result.data}")
        else:
            print(f"   Error: {result.error}")

if __name__ == "__main__":
    asyncio.run(test_cmkl_mcp())