"""Data connector interface for MCP, PDF, and Text sources."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class DataConnectorInterface(ABC):
    """Abstract interface for data connectors (MCP, PDF, Text)."""
    
    @abstractmethod
    def fetch(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Fetch data based on a list of requests.
        
        Args:
            requests: List of request dictionaries specifying what data to fetch
            
        Returns:
            Dictionary containing the fetched data
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the data source is available."""
        pass
    
    @abstractmethod
    def get_connector_info(self) -> Dict[str, Any]:
        """Get information about the connector."""
        pass 