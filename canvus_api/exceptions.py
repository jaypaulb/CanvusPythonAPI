"""
Custom exceptions for the Canvus API client.
"""

class CanvusAPIError(Exception):
    """Base exception for all Canvus API errors."""
    pass


class AuthenticationError(CanvusAPIError):
    """Raised when authentication fails."""
    pass


class ConnectionError(CanvusAPIError):
    """Raised when connection to the server fails."""
    pass


class ValidationError(CanvusAPIError):
    """Raised when request or response validation fails."""
    pass


class CanvasError(CanvusAPIError):
    """Raised when an operation on a canvas fails."""
    pass