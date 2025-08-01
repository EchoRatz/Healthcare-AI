"""MCP (Model Context Protocol) connector implementation."""

import json
import requests
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
            
            for req in requests:
                endpoint = req.get('endpoint')
                params = req.get('params', {})
                
                if not endpoint:
                    self.logger.warning(f"Skipping request without endpoint: {req}")
                    continue
                
                # MCP JSON-RPC call
                payload = {
                    "jsonrpc": "2.0",
                    "id": f"req_{datetime.now().timestamp()}",
                    "method": endpoint,
                    "params": params
                }
                
                self.logger.debug(f"Sending MCP request to {endpoint}: {params}")
                
                response = self.session.post(
                    f"{self.server_url}/api/jsonrpc",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if 'error' in result:
                        self.logger.error(f"MCP error for {endpoint}: {result['error']}")
                        results[endpoint] = {
                            'error': result['error'],
                            'data': None
                        }
                    else:
                        results[endpoint] = {
                            'data': result.get('result'),
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
    
    def is_available(self) -> bool:
        """Check if MCP server is available."""
        try:
            # Try to get server info
            payload = {
                "jsonrpc": "2.0",
                "id": "health_check",
                "method": "serverInfo",
                "params": {}
            }
            
            response = self.session.post(
                f"{self.server_url}/api/jsonrpc",
                json=payload,
                timeout=5
            )
            
            return response.status_code == 200
            
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
                "id": "list_resources",
                "method": "resources.list",
                "params": {}
            }
            
            response = self.session.post(
                f"{self.server_url}/api/jsonrpc",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'result' in result:
                    return [resource['name'] for resource in result['result']]
            
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