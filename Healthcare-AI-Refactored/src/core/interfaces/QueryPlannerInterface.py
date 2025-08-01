"""Query planner interface for chain-of-thought reasoning."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class QueryPlannerInterface(ABC):
    """Abstract interface for query planning with chain-of-thought reasoning."""
    
    @abstractmethod
    def plan(self, query: str) -> Dict[str, Any]:
        """
        Analyze a query and create a structured retrieval plan.
        
        Args:
            query: The user's question
            
        Returns:
            Structured plan specifying what data to fetch from each source
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the planner is available."""
        pass
    
    @abstractmethod
    def get_planning_info(self) -> Dict[str, Any]:
        """Get information about the planning capabilities."""
        pass 