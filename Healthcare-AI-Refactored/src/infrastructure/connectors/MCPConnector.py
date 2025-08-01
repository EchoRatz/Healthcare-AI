"""MCP (Model Context Protocol) connector implementation."""

import json
import requests
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from core.interfaces.DataConnectorInterface import DataConnectorInterface
from shared.logging.LoggerMixin import LoggerMixin


class MCPConnector(DataConnectorInterface, LoggerMixin):
    """MCP client implementation for fetching data from MCP servers."""
    
    def __init__(self, server_url: str, auth_token: Optional[str] = None):
        super().__init__()
        self.server_url = server_url.rstrip('/')
        self.auth_token = auth_token
        self.session = requests.Session()
        
        if auth_token:
            self.session.headers.update({
                'Authorization': f'Bearer {auth_token}',
                'Content-Type': 'application/json'
            })
        else:
            self.session.headers.update({
                'Content-Type': 'application/json'
            })
    
    def select_appropriate_tool(self, query: str) -> str:
        """Select the most appropriate MCP tool based on query content."""
        query_lower = query.lower()
        
        # Tool selection logic based on query keywords
        tool_mapping = {
            # Patient-related tools
            'patient': 'lookup_patient',
            'search': 'search_patients',
            'create': 'create_patient',
            'emergency': 'emergency_patient_lookup',
            'medical history': 'get_medical_history',
            'vital signs': 'add_vital_signs',
            'medication': 'add_medication',
            'allergy': 'add_allergy',
            'food allergy': 'check_food_allergies',
            'drug allergy': 'check_drug_allergies',
            'allergy alternative': 'get_allergy_alternatives',
            
            # Appointment-related tools
            'appointment': 'get_appointments',
            'schedule': 'schedule_appointment',
            'book appointment': 'book_appointment_with_availability_check',
            'doctor recommendation': 'book_appointment_with_doctor_recommendation',
            'next available': 'find_next_available_appointment',
            'cancel': 'cancel_appointment',
            'doctor schedule': 'get_doctor_schedule',
            'doctor availability': 'check_doctor_availability',
            'available doctor': 'find_available_doctors',
            
            # Department-related tools
            'department': 'list_all_departments',
            'departments': 'list_all_departments',
            'แผนก': 'list_all_departments',
            'department info': 'get_department_info',
            'department staff': 'get_department_staff',
            'department service': 'get_department_services',
            'services': 'get_department_services',
            
            # Staff and doctor tools
            'staff': 'get_staff_info',
            'staff by department': 'list_staff_by_department',
            'doctor': 'get_doctor_info',
            'search doctor': 'search_doctors',
            'doctor info': 'get_doctor_info',
            
            # Room-related tools
            'ห้อง': 'get_room_info',
            'room': 'get_room_info',
            'room equipment': 'get_room_equipment',
            'available room': 'find_available_rooms',
            'room status': 'update_room_status',
            
            # Queue-related tools
            'queue': 'book_queue',
            'queue status': 'check_queue_status',
            'department queue': 'get_department_queue_status',
            
            # Lab-related tools
            'lab result': 'get_lab_results',
            'add lab': 'add_lab_result'
        }
        
        # Check for exact matches first
        for keyword, tool in tool_mapping.items():
            if keyword in query_lower:
                self.logger.info(f"Selected MCP tool '{tool}' based on keyword '{keyword}'")
                return tool
        
        # Default to list_all_departments for general queries
        self.logger.info("No specific tool match found, using default 'list_all_departments'")
        return 'list_all_departments'
    
    def fetch(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Fetch data from MCP server based on requests.
        
        Args:
            requests: List of request dictionaries with 'endpoint' and 'params' keys
            
        Returns:
            Dictionary containing fetched data organized by endpoint
        """
        try:
            results = {}
            
            # Initialize MCP connection if not already done
            if not hasattr(self, '_initialized') or not self._initialized:
                self._initialize_mcp()
            
            for req in requests:
                endpoint = req.get('endpoint')
                params = req.get('params', {})
                
                if not endpoint:
                    self.logger.warning(f"Skipping request without endpoint: {req}")
                    continue
                
                # Auto-select appropriate tool if not specified
                tool_name = params.get("name", endpoint)
                if tool_name == endpoint and not params.get("arguments"):
                    # If no specific tool is requested, try to select based on query context
                    tool_name = self.select_appropriate_tool(str(params.get("query", "")))
                
                # MCP server expects JSON-RPC format based on working examples
                payload = {
                    "jsonrpc": "2.0",
                    "id": f"req_{int(time.time() * 1000)}",
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": params.get("arguments", {})
                    }
                }
                
                self.logger.debug(f"Sending MCP request to {endpoint}: {params}")
                
                # Try different endpoints based on working examples
                endpoints = ["/message", "/mcp", "/api/mcp", ""]
                response = None
                
                for ep in endpoints:
                    try:
                        response = self.session.post(
                            f"{self.server_url}{ep}",
                            json=payload,
                            timeout=30
                        )
                        if response.status_code == 200:
                            break
                    except Exception as e:
                        self.logger.debug(f"Failed to connect to {ep}: {e}")
                        continue
                
                if not response:
                    self.logger.error(f"Failed to connect to any MCP endpoint")
                    results[endpoint] = {
                        'error': 'Connection failed',
                        'data': None
                    }
                    continue
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Handle JSON-RPC response format
                    if 'error' in result:
                        self.logger.error(f"MCP error for {endpoint}: {result['error']}")
                        results[endpoint] = {
                            'error': result['error'],
                            'data': None
                        }
                    elif 'result' in result:
                        # JSON-RPC success response
                        results[endpoint] = {
                            'data': result['result'],
                            'error': None
                        }
                    else:
                        # Direct response (non-JSON-RPC)
                        results[endpoint] = {
                            'data': result,
                            'error': None
                        }
                else:
                    self.logger.error(f"MCP HTTP error {response.status_code}: {response.text}")
                    results[endpoint] = {
                        'error': f"HTTP {response.status_code}",
                        'data': None
                    }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to fetch from MCP server: {e}")
            return {'error': str(e)}
    
    def _initialize_mcp(self):
        """Initialize MCP connection using JSON-RPC format"""
        try:
            self.logger.info("Initializing MCP connection...")
            
            init_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "clientInfo": {
                        "name": "healthcare-ai-client",
                        "version": "1.0.0"
                    },
                    "capabilities": {
                        "tools": {"listChanged": True},
                        "resources": {"listChanged": True, "subscribe": True}
                    }
                }
            }
            
            # Try different endpoints for initialization
            endpoints = ["/message", "/mcp", "/api/mcp", ""]
            
            for ep in endpoints:
                try:
                    response = self.session.post(
                        f"{self.server_url}{ep}",
                        json=init_payload,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if 'result' in result or 'error' not in result:
                            self.logger.info(f"MCP initialized successfully via {ep}")
                            self._initialized = True
                            return
                            
                except Exception as e:
                    self.logger.debug(f"Failed to initialize via {ep}: {e}")
                    continue
            
            self.logger.warning("Failed to initialize MCP connection")
            self._initialized = False
            
        except Exception as e:
            self.logger.error(f"MCP initialization error: {e}")
            self._initialized = False
    
    def is_available(self) -> bool:
        """Check if MCP server is available."""
        try:
            # Try different possible endpoints based on working examples
            endpoints = [
                "/message",
                "/mcp", 
                "/api/mcp",
                "",
                "/health",
                "/status"
            ]
            
            for endpoint in endpoints:
                try:
                    # Try a simple GET request first
                    response = self.session.get(
                        f"{self.server_url}{endpoint}",
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        self.logger.info(f"MCP server available at {endpoint}")
                        return True
                    
                    # Try JSON-RPC tools/list format
                    payload = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/list"
                    }
                    
                    response = self.session.post(
                        f"{self.server_url}{endpoint}",
                        json=payload,
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        self.logger.info(f"MCP server available at {endpoint}")
                        return True
                        
                except Exception as e:
                    self.logger.debug(f"MCP endpoint {endpoint} failed: {e}")
                    continue
            
            self.logger.warning(f"MCP server not available at any endpoint")
            return False
            
        except Exception as e:
            self.logger.debug(f"MCP server not available: {e}")
            return False
    
    def get_connector_info(self) -> Dict[str, Any]:
        """Get information about the MCP connector."""
        return {
            'type': 'mcp',
            'server_url': self.server_url,
            'available': self.is_available(),
            'auth_configured': bool(self.auth_token)
        }
    
    def list_resources(self) -> List[str]:
        """List available MCP resources."""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list"
            }
            
            # Try different endpoints based on working examples
            endpoints = ["/message", "/mcp", "/api/mcp", ""]
            response = None
            
            for ep in endpoints:
                try:
                    response = self.session.post(
                        f"{self.server_url}{ep}",
                        json=payload,
                        timeout=10
                    )
                    if response.status_code == 200:
                        break
                except Exception as e:
                    self.logger.debug(f"Failed to connect to {ep}: {e}")
                    continue
            
            if response and response.status_code == 200:
                result = response.json()
                
                # Handle JSON-RPC response format
                if 'result' in result:
                    result = result['result']
                
                # Extract department names from the response
                if isinstance(result, list):
                    return [dept.get('name', '') for dept in result if dept.get('name')]
                elif isinstance(result, dict) and 'departments' in result:
                    return [dept.get('name', '') for dept in result['departments'] if dept.get('name')]
                elif isinstance(result, dict) and 'tools' in result:
                    # Extract tool names from tools list
                    return [tool.get('name', '') for tool in result['tools'] if tool.get('name')]
            
            return []
            
        except Exception as e:
            self.logger.error(f"Failed to list MCP resources: {e}")
            return []
    
    def get_resource(self, resource_name: str, **params) -> Optional[Dict[str, Any]]:
        """Get a specific MCP resource."""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": f"get_{resource_name}",
                "method": "resources.read",
                "params": {
                    "name": resource_name,
                    **params
                }
            }
            
            response = self.session.post(
                f"{self.server_url}/api/jsonrpc",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('result')
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get MCP resource {resource_name}: {e}")
            return None 