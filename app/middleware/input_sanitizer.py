"""Input sanitization utilities for AI and user inputs."""
import re
from typing import Any, Dict
from fastapi import HTTPException, status


class InputSanitizer:
    """Sanitize and validate user inputs to prevent injection attacks."""
    
    # Maximum lengths for different input types
    MAX_TEXT_LENGTH = 10000  # 10K characters
    MAX_AI_PROMPT_LENGTH = 4000  # 4K characters for AI prompts
    MAX_FIELD_NAME_LENGTH = 100
    MAX_TOPIC_LENGTH = 500
    
    # Dangerous patterns to detect
    DANGEROUS_PATTERNS = [
        r"<script[^>]*>.*?</script>",  # Script tags
        r"javascript:",  # JavaScript protocol
        r"on\w+\s*=",  # Event handlers (onclick, onload, etc.)
        r"<iframe",  # Iframes
        r"<object",  # Objects
        r"<embed",  # Embeds
    ]
    
    @classmethod
    def sanitize_text(cls, text: str, max_length: int = MAX_TEXT_LENGTH, field_name: str = "text") -> str:
        """
        Sanitize text input.
        
        Args:
            text: Input text to sanitize
            max_length: Maximum allowed length
            field_name: Name of the field (for error messages)
            
        Returns:
            Sanitized text
            
        Raises:
            HTTPException: If input is invalid or dangerous
        """
        if not isinstance(text, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} must be a string"
            )
        
        # Check length
        if len(text) > max_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} exceeds maximum length of {max_length} characters"
            )
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid content detected in {field_name}"
                )
        
        # Remove null bytes
        text = text.replace("\x00", "")
        
        # Normalize whitespace (but preserve newlines)
        text = re.sub(r"[ \t]+", " ", text)
        
        return text.strip()
    
    @classmethod
    def sanitize_ai_prompt(cls, prompt: str, field_name: str = "prompt") -> str:
        """
        Sanitize AI prompt input with stricter limits.
        
        Args:
            prompt: AI prompt to sanitize
            field_name: Name of the field
            
        Returns:
            Sanitized prompt
        """
        return cls.sanitize_text(prompt, max_length=cls.MAX_AI_PROMPT_LENGTH, field_name=field_name)
    
    @classmethod
    def sanitize_field_name(cls, field_name: str) -> str:
        """
        Sanitize field name (alphanumeric and underscores only).
        
        Args:
            field_name: Field name to sanitize
            
        Returns:
            Sanitized field name
        """
        if not isinstance(field_name, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Field name must be a string"
            )
        
        if len(field_name) > cls.MAX_FIELD_NAME_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Field name exceeds maximum length of {cls.MAX_FIELD_NAME_LENGTH}"
            )
        
        # Only allow alphanumeric and underscores
        if not re.match(r"^[a-zA-Z0-9_]+$", field_name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Field name must contain only letters, numbers, and underscores"
            )
        
        return field_name
    
    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any], max_items: int = 50) -> Dict[str, Any]:
        """
        Sanitize dictionary values.
        
        Args:
            data: Dictionary to sanitize
            max_items: Maximum number of items allowed
            
        Returns:
            Sanitized dictionary
        """
        if not isinstance(data, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data must be a dictionary"
            )
        
        if len(data) > max_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dictionary exceeds maximum of {max_items} items"
            )
        
        sanitized = {}
        for key, value in data.items():
            # Sanitize key
            sanitized_key = cls.sanitize_field_name(key)
            
            # Sanitize value if it's a string
            if isinstance(value, str):
                sanitized[sanitized_key] = cls.sanitize_text(value, max_length=1000, field_name=key)
            elif isinstance(value, (int, float, bool, type(None))):
                sanitized[sanitized_key] = value
            else:
                # Convert other types to string and sanitize
                sanitized[sanitized_key] = cls.sanitize_text(str(value), max_length=1000, field_name=key)
        
        return sanitized
    
    @classmethod
    def validate_no_sql_injection(cls, text: str) -> bool:
        """
        Check for potential SQL injection patterns.
        
        Note: This is a defense-in-depth measure. Primary protection
        is using parameterized queries (SQLAlchemy ORM).
        
        Args:
            text: Text to check
            
        Returns:
            True if safe, raises exception if dangerous
        """
        sql_patterns = [
            r"(\bUNION\b.*\bSELECT\b)",
            r"(\bDROP\b.*\bTABLE\b)",
            r"(\bINSERT\b.*\bINTO\b)",
            r"(\bDELETE\b.*\bFROM\b)",
            r"(\bUPDATE\b.*\bSET\b)",
            r"(--|\#|\/\*|\*\/)",  # SQL comments
            r"(\bEXEC\b|\bEXECUTE\b)",
            r"(\bxp_\w+)",  # SQL Server extended procedures
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid content detected"
                )
        
        return True
