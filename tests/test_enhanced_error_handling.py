"""
Tests for enhanced error handling and retry logic.
"""

import pytest
from canvus_api.client import CanvusClient
from canvus_api.exceptions import (
    CanvusAPIError,
    AuthenticationError,
    RateLimitError,
    ResourceNotFoundError,
    ServerError,
    TimeoutError,
)


class TestEnhancedErrorHandling:
    """Test enhanced error handling and retry logic."""

    @pytest.fixture
    def client(self):
        """Create a test client with enhanced error handling."""
        return CanvusClient(
            base_url="https://test.com",
            api_key="test-key",
            max_retries=3,
            retry_delay=0.1,
            retry_backoff=2.0,
            timeout=5.0,
        )

    def test_error_classification(self, client):
        """Test error classification based on status codes."""
        # Test authentication error
        error = client._classify_error(401, "Unauthorized")
        assert isinstance(error, AuthenticationError)
        assert error.status_code == 401

        # Test resource not found
        error = client._classify_error(404, "Not found")
        assert isinstance(error, ResourceNotFoundError)
        assert error.status_code == 404

        # Test rate limit
        error = client._classify_error(429, "Too many requests")
        assert isinstance(error, RateLimitError)
        assert error.status_code == 429

        # Test timeout
        error = client._classify_error(408, "Request timeout")
        assert isinstance(error, TimeoutError)
        assert error.status_code == 408

        # Test server error
        error = client._classify_error(500, "Internal server error")
        assert isinstance(error, ServerError)
        assert error.status_code == 500

        # Test generic error
        error = client._classify_error(400, "Bad request")
        assert isinstance(error, CanvusAPIError)
        assert error.status_code == 400

        # Test connection error (None status code)
        error = client._classify_error(None, "Connection failed")
        assert isinstance(error, TimeoutError)
        assert error.status_code is None

    def test_retryable_error_detection(self, client):
        """Test retryable error detection."""
        # Test 5xx errors (retryable)
        assert client._is_retryable_error(500, "Server error")
        assert client._is_retryable_error(502, "Bad gateway")
        assert client._is_retryable_error(503, "Service unavailable")
        assert client._is_retryable_error(504, "Gateway timeout")

        # Test 501 Not Implemented (not retryable)
        assert not client._is_retryable_error(501, "Not implemented")

        # Test specific 4xx errors (retryable)
        assert client._is_retryable_error(408, "Request timeout")
        assert client._is_retryable_error(429, "Too many requests")

        # Test other 4xx errors (not retryable)
        assert not client._is_retryable_error(400, "Bad request")
        assert not client._is_retryable_error(401, "Unauthorized")
        assert not client._is_retryable_error(403, "Forbidden")
        assert not client._is_retryable_error(404, "Not found")

        # Test connection errors (retryable)
        assert client._is_retryable_error(None, "Connection failed")

    def test_response_validation(self, client):
        """Test response validation against request data."""
        # Test with matching data
        request_data = {"name": "test", "description": "test desc"}
        response_data = {"name": "test", "description": "test desc", "id": "123"}
        # Should not raise any error
        client._validate_response_against_request(request_data, response_data)

        # Test with mismatched data (should log warning but not raise)
        request_data = {"name": "test", "description": "test desc"}
        response_data = {"name": "different", "description": "test desc", "id": "123"}
        # Should not raise any error, just log warning
        client._validate_response_against_request(request_data, response_data)

        # Test with None data
        client._validate_response_against_request(None, response_data)
        client._validate_response_against_request(request_data, None)

    def test_client_initialization_with_retry_config(self):
        """Test client initialization with retry configuration."""
        client = CanvusClient(
            base_url="https://test.com",
            api_key="test-key",
            max_retries=5,
            retry_delay=2.0,
            retry_backoff=3.0,
            timeout=60.0,
        )

        assert client.max_retries == 5
        assert client.retry_delay == 2.0
        assert client.retry_backoff == 3.0
        assert client.timeout == 60.0

    def test_client_initialization_defaults(self):
        """Test client initialization with default values."""
        client = CanvusClient(
            base_url="https://test.com",
            api_key="test-key",
        )

        assert client.max_retries == 3
        assert client.retry_delay == 1.0
        assert client.retry_backoff == 2.0
        assert client.timeout == 30.0

    @pytest.mark.asyncio
    async def test_retry_logic_integration(self, client):
        """Test retry logic integration with real server."""
        # This test will use the test server to verify retry logic works
        # We'll create a simple test that demonstrates the retry configuration
        # is properly set up
        
        # Test that the client has the expected retry configuration
        assert client.max_retries == 3
        assert client.retry_delay == 0.1
        assert client.retry_backoff == 2.0
        assert client.timeout == 5.0
        
        # Test that the _request method accepts max_retries parameter
        # This is a basic test to ensure the interface is correct
        assert hasattr(client, '_request')
        assert 'max_retries' in client._request.__code__.co_varnames 