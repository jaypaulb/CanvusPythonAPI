"""
Custom exceptions for the Canvus API client.
"""

from typing import Optional


class CanvusAPIError(Exception):
    """Base exception for all Canvus API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_text: Optional[str] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


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
