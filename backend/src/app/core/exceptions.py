"""
Custom exceptions for the application.
"""
from typing import Any, Dict, Optional


class MyChordHubException(Exception):
    """Base exception class for MyChordHub application."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(MyChordHubException):
    """Exception for validation errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)


class AuthenticationException(MyChordHubException):
    """Exception for authentication errors."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationException(MyChordHubException):
    """Exception for authorization errors."""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status_code=403)


class NotFoundException(MyChordHubException):
    """Exception for resource not found errors."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ConflictException(MyChordHubException):
    """Exception for resource conflict errors."""
    
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status_code=409)


class RateLimitException(MyChordHubException):
    """Exception for rate limit errors."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)