"""
Validators - Input validation utilities.
"""

from typing import Any


class Validators:
    """Input validation utilities."""
    
    @staticmethod
    def is_non_empty_string(value: Any) -> bool:
        """Check if value is non-empty string."""
        return isinstance(value, str) and len(value.strip()) > 0
    
    @staticmethod
    def is_positive_number(value: Any) -> bool:
        """Check if value is positive number."""
        try:
            return float(value) > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_valid_relevance_score(value: Any) -> bool:
        """Check if value is valid relevance score (0-1)."""
        try:
            score = float(value)
            return 0.0 <= score <= 1.0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_query(query: str) -> tuple[bool, str]:
        """Validate search query."""
        if not query:
            return False, "Query cannot be empty"
        
        if not query.strip():
            return False, "Query cannot be only whitespace"
        
        if len(query.strip()) > 1000:
            return False, "Query too long (max 1000 characters)"
        
        return True, "Valid query"
