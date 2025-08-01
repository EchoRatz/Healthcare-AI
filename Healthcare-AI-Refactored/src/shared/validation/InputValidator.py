"""Input validation utilities."""

from typing import Any, Tuple, List
import re


class InputValidator:
    """Input validation utilities."""
    
    @staticmethod
    def validate_non_empty_string(value: Any, field_name: str = "value") -> Tuple[bool, str]:
        """Validate non-empty string."""
        if not isinstance(value, str):
            return False, f"{field_name} must be a string"
        
        if not value.strip():
            return False, f"{field_name} cannot be empty"
        
        return True, "Valid"
    
    @staticmethod
    def validate_positive_number(value: Any, field_name: str = "value") -> Tuple[bool, str]:
        """Validate positive number."""
        try:
            num = float(value)
            if num <= 0:
                return False, f"{field_name} must be positive"
            return True, "Valid"
        except (ValueError, TypeError):
            return False, f"{field_name} must be a valid number"
    
    @staticmethod
    def validate_score(value: Any, field_name: str = "score") -> Tuple[bool, str]:
        """Validate score between 0 and 1."""
        try:
            score = float(value)
            if not 0 <= score <= 1:
                return False, f"{field_name} must be between 0 and 1"
            return True, "Valid"
        except (ValueError, TypeError):
            return False, f"{field_name} must be a valid number"
    
    @staticmethod
    def validate_question_id(question_id: str) -> Tuple[bool, str]:
        """Validate question ID format."""
        if not isinstance(question_id, str):
            return False, "Question ID must be string"
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', question_id):
            return False, "Question ID contains invalid characters"
        
        if len(question_id) > 50:
            return False, "Question ID too long (max 50 characters)"
        
        return True, "Valid"
    
    @staticmethod
    def validate_file_path(file_path: str) -> Tuple[bool, str]:
        """Validate file path."""
        if not isinstance(file_path, str):
            return False, "File path must be string"
        
        if not file_path.strip():
            return False, "File path cannot be empty"
        
        # Check for potentially dangerous paths
        if '..' in file_path or file_path.startswith('/'):
            return False, "File path contains unsafe characters"
        
        return True, "Valid"