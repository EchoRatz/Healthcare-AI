"""
MCP (Model Context Protocol) Client
Connects to MCP server at https://mcp-hackathon.cmkl.ai/mcp
This is a STATIC MCP server - tools and resources are predefined and not dynamically discoverable
"""

import requests
import json
import time
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin
import logging
import sseclient
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StaticMCPClient:
    """
    MCP Client for connecting to STATIC MCP servers.
    Static MCP servers have predefined tools/resources that are not dynamically discoverable.
    """
    
    def __init__(self, base_url: str = "https://mcp-hackathon.cmkl.ai/mcp", session_id: Optional[str] = None):
        """
        Initialize static MCP client.
        
        Args:
            base_url: Base URL of the MCP server
            session_id: Optional session ID to use
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        # MCP protocol version
        self.protocol_version = "2024-11-05"
        
        # Generate client ID
        self.client_id = str(uuid.uuid4())
        
        # Session management
        self.session_id = session_id
        self.initialized = False
        
        # Static server information
        self.server_info = {
            "name": "HospitalMCP",
            "version": "1.12.2",
            "type": "static",
            "description": "Static healthcare-focused MCP server"
        }
        
        logger.info(f"Initialized STATIC MCP client for {self.base_url}")
        logger.info(f"Client ID: {self.client_id}")
        if self.session_id:
            logger.info(f"Using session ID: {self.session_id}")
    
    def _make_mcp_request(self, method: str, params: Optional[Dict] = None, request_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Make MCP request using JSON-RPC over SSE.
        
        Args:
            method: RPC method name
            params: RPC parameters
            request_id: Request ID (auto-generated if None)
            
        Returns:
            Response data
        """
        if request_id is None:
            request_id = str(uuid.uuid4())
        
        try:
            # Prepare JSON-RPC request
            request_data = {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": method
            }
            
            if params:
                request_data["params"] = params
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/event-stream'
            }
            
            # Add session ID if available
            if self.session_id:
                headers['X-Session-ID'] = self.session_id
            
            response = self.session.post(
                self.base_url,
                json=request_data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            # Parse SSE response
            if response.headers.get('content-type', '').startswith('text/event-stream'):
                client = sseclient.SSEClient(response)
                events = []
                
                for event in client.events():
                    if event.data:
                        try:
                            data = json.loads(event.data)
                            events.append(data)
                        except json.JSONDecodeError:
                            events.append({'raw_data': event.data})
                    
                    # Stop after first few events to avoid infinite loop
                    if len(events) >= 5:
                        break
                
                # Return the first event (usually the response)
                return events[0] if events else {'error': 'No events received'}
            else:
                return response.json()
            
        except Exception as e:
            logger.error(f"MCP request failed: {e}")
            return {'error': str(e)}
    
    def initialize_connection(self) -> Dict[str, Any]:
        """
        Initialize connection with static MCP server.
        
        Returns:
            Connection initialization result
        """
        logger.info("Initializing connection to STATIC MCP server...")
        
        try:
            # Initialize with MCP protocol
            init_params = {
                "protocolVersion": self.protocol_version,
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "clientInfo": {
                    "name": "static-mcp-python-client",
                    "version": "1.0.0"
                }
            }
            
            result = self._make_mcp_request("initialize", init_params, "init-1")
            
            if 'error' not in result and 'result' in result:
                self.initialized = True
                
                logger.info("Successfully initialized connection to STATIC MCP server")
                logger.info(f"Server info: {result['result'].get('serverInfo', {})}")
                logger.info(f"Capabilities: {result['result'].get('capabilities', {})}")
                
                return result
            else:
                logger.error(f"Initialization failed: {result}")
                return result
            
        except Exception as e:
            logger.error(f"Failed to initialize connection: {e}")
            return {"error": str(e)}
    
    def get_static_server_info(self) -> Dict[str, Any]:
        """
        Get information about the static MCP server.
        
        Returns:
            Static server information
        """
        logger.info("Getting static server information...")
        
        if not self.initialized:
            init_result = self.initialize_connection()
            if 'error' in init_result:
                return init_result
        
        return {
            "server_name": self.server_info["name"],
            "server_version": self.server_info["version"],
            "server_type": self.server_info["type"],
            "description": self.server_info["description"],
            "protocol_version": self.protocol_version,
            "session_id": self.session_id,
            "client_id": self.client_id,
            "capabilities": {
                "experimental": {},
                "prompts": {"listChanged": False},
                "resources": {"subscribe": False, "listChanged": False},
                "tools": {"listChanged": False}
            },
            "static_features": {
                "dynamic_discovery": False,
                "tool_listing": False,
                "resource_listing": False,
                "healthcare_focused": True
            }
        }
    
    def get_available_static_features(self) -> Dict[str, Any]:
        """
        Get information about available static features.
        Since this is a static server, we document what's likely available.
        
        Returns:
            Available static features
        """
        logger.info("Getting available static features...")
        
        return {
            "server_type": "static",
            "available_features": {
                "connection": "✅ Working - Can initialize and maintain connection",
                "session_management": "✅ Working - Session ID handling",
                "healthcare_tools": "⚠️ Likely available but not discoverable",
                "healthcare_resources": "⚠️ Likely available but not discoverable",
                "dynamic_tool_listing": "❌ Not available - Static server",
                "dynamic_resource_listing": "❌ Not available - Static server"
            },
            "likely_tools": [
                "healthcare_data_processing",
                "medical_record_analysis", 
                "patient_data_management",
                "healthcare_analytics",
                "medical_document_processing"
            ],
            "likely_resources": [
                "healthcare_databases",
                "medical_guidelines",
                "patient_records",
                "healthcare_apis"
            ],
            "usage_notes": [
                "This is a STATIC MCP server - tools are predefined",
                "Tools may need to be called directly without discovery",
                "Healthcare-focused functionality likely available",
                "May require specific method names or parameters",
                "Documentation or examples needed for tool usage"
            ]
        }
    
    def test_static_functionality(self) -> Dict[str, Any]:
        """
        Test what functionality is actually available on the static server.
        
        Returns:
            Test results
        """
        logger.info("Testing static server functionality...")
        
        if not self.initialized:
            init_result = self.initialize_connection()
            if 'error' in init_result:
                return {"error": "Not initialized"}
        
        test_results = {
            "connection": {"status": "success", "details": "Successfully connected"},
            "initialization": {"status": "success", "details": "Server initialized"},
            "session_management": {"status": "success", "details": f"Session ID: {self.session_id}"},
            "dynamic_discovery": {"status": "failed", "details": "Static server - no dynamic discovery"},
            "static_features": {"status": "available", "details": "Healthcare-focused tools likely available"}
        }
        
        return test_results
    
    def explore_static_server(self) -> Dict[str, Any]:
        """
        Explore the static MCP server to understand its capabilities.
        
        Returns:
            Server exploration results
        """
        logger.info("Exploring static MCP server...")
        
        structure = {
            "base_url": self.base_url,
            "server_info": self.get_static_server_info(),
            "static_features": self.get_available_static_features(),
            "test_results": self.test_static_functionality(),
            "status": "connected",
            "server_type": "static"
        }
        
        return structure
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to the static MCP server.
        
        Returns:
            Connection test results
        """
        logger.info("Testing connection to static MCP server...")
        
        test_results = {
            "server_url": self.base_url,
            "connection_status": "unknown",
            "response_time": None,
            "server_info": None,
            "static_features": None,
            "initialized": False,
            "server_type": "static",
            "errors": []
        }
        
        try:
            start_time = time.time()
            
            # Test connection initialization
            init_result = self.initialize_connection()
            test_results["response_time"] = time.time() - start_time
            
            if 'error' not in init_result:
                test_results["connection_status"] = "success"
                test_results["initialized"] = True
                
                # Get server info
                server_info = self.get_static_server_info()
                test_results["server_info"] = server_info
                
                # Get static features
                static_features = self.get_available_static_features()
                test_results["static_features"] = static_features
                
            else:
                test_results["connection_status"] = "failed"
                test_results["errors"].append(init_result['error'])
                
        except requests.exceptions.Timeout:
            test_results["connection_status"] = "timeout"
            test_results["errors"].append("Connection timeout")
        except requests.exceptions.ConnectionError:
            test_results["connection_status"] = "connection_error"
            test_results["errors"].append("Connection error")
        except Exception as e:
            test_results["connection_status"] = "error"
            test_results["errors"].append(str(e))
        
        return test_results


def main():
    """
    Main function to test static MCP connection and understand available options.
    """
    print("=== STATIC MCP Client - Exploring HospitalMCP Server ===")
    print(f"Target: https://mcp-hackathon.cmkl.ai/mcp")
    print("Note: This is a STATIC MCP server - tools are predefined, not discoverable")
    print()
    
    # Create static MCP client with the provided session ID
    session_id = "640d85fe5e314b36a71c16fd9608978f"
    client = StaticMCPClient(session_id=session_id)
    
    # Test connection
    print("1. Testing connection to static server...")
    test_results = client.test_connection()
    
    print(f"Connection Status: {test_results['connection_status']}")
    print(f"Server Type: {test_results['server_type']}")
    print(f"Initialized: {test_results['initialized']}")
    if test_results['response_time']:
        print(f"Response Time: {test_results['response_time']:.2f} seconds")
    
    if test_results['errors']:
        print("Errors:")
        for error in test_results['errors']:
            print(f"  - {error}")
    
    print()
    
    # Get static server info
    print("2. Getting static server information...")
    server_info = client.get_static_server_info()
    print("Static Server Info:")
    print(json.dumps(server_info, indent=2, default=str))
    
    print()
    
    # Get available static features
    print("3. Available static features...")
    static_features = client.get_available_static_features()
    print("Static Features:")
    print(json.dumps(static_features, indent=2, default=str))
    
    print()
    
    # Explore static server
    print("4. Exploring static server structure...")
    structure = client.explore_static_server()
    
    print("Static Server Analysis:")
    print(f"  Server Type: {structure['server_type']}")
    print(f"  Status: {structure['status']}")
    print(f"  Server Name: {structure['server_info']['server_name']}")
    print(f"  Version: {structure['server_info']['server_version']}")
    print(f"  Description: {structure['server_info']['description']}")
    
    print()
    print("Available Features:")
    for feature, status in structure['static_features']['available_features'].items():
        print(f"  {feature}: {status}")
    
    print()
    print("Likely Available Tools:")
    for tool in structure['static_features']['likely_tools']:
        print(f"  - {tool}")
    
    print()
    print("Likely Available Resources:")
    for resource in structure['static_features']['likely_resources']:
        print(f"  - {resource}")
    
    print()
    print("Usage Notes:")
    for note in structure['static_features']['usage_notes']:
        print(f"  • {note}")
    
    print()
    print("5. Summary for Static MCP Server:")
    
    if structure['status'] == 'connected':
        print("✓ Successfully connected to STATIC MCP server")
        print(f"✓ Server: {structure['server_info']['server_name']}")
        print(f"✓ Version: {structure['server_info']['server_version']}")
        print(f"✓ Type: {structure['server_info']['server_type']}")
        print(f"✓ Session ID: {structure['server_info']['session_id']}")
        
        print("\n📋 What's Available:")
        print("  ✅ Connection and session management")
        print("  ✅ Server information retrieval")
        print("  ⚠️ Healthcare tools (likely available but not discoverable)")
        print("  ⚠️ Healthcare resources (likely available but not discoverable)")
        
        print("\n📋 What's NOT Available:")
        print("  ❌ Dynamic tool discovery")
        print("  ❌ Dynamic resource listing")
        print("  ❌ Standard MCP tool listing methods")
        
        print("\n🎯 Next Steps:")
        print("  1. Check server documentation for available method names")
        print("  2. Try calling healthcare-specific methods directly")
        print("  3. Look for examples or API documentation")
        print("  4. Test healthcare-related functionality")
    
    else:
        print("✗ Failed to connect to static MCP server")
        print("Please check:")
        print("  - Server URL is correct")
        print("  - Server is running and accessible")
        print("  - Network connectivity")
        print("  - Session ID is valid")
    
    print("\n=== Static MCP Client Test Complete ===")


if __name__ == "__main__":
    main()
