"""Test license methods with mocked responses."""

import asyncio
import json
from unittest.mock import AsyncMock, patch
from typing import Dict, Any

import pytest

from canvus_api import CanvusClient
from canvus_api.exceptions import CanvusAPIError


class TestLicenseMethods:
    """Test license-related methods."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        return CanvusClient("https://test.example.com", "test-api-key")

    @pytest.mark.asyncio
    async def test_request_offline_activation_success(self, mock_client):
        """Test successful offline activation request."""
        # Mock response data
        mock_response = {
            "request_data": "eyJ0eXBlIjoib2ZmbGluZS1hY3RpdmF0aW9uLXJlcXVlc3QiLCJkYXRhIjoiLi4uIn0=",
            "expires_at": "2024-12-31T23:59:59Z",
            "instructions": "Use this data to complete offline activation"
        }

        # Mock the _request method
        with patch.object(mock_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            # Test the method
            result = await mock_client.request_offline_activation("TEST-KEY-1234-5678-9ABC")

            # Verify the result
            assert result == mock_response
            assert result["request_data"] == "eyJ0eXBlIjoib2ZmbGluZS1hY3RpdmF0aW9uLXJlcXVlc3QiLCJkYXRhIjoiLi4uIn0="
            assert result["expires_at"] == "2024-12-31T23:59:59Z"
            assert result["instructions"] == "Use this data to complete offline activation"

            # Verify the _request method was called correctly
            mock_request.assert_called_once_with(
                "GET", 
                "license/request", 
                params={"key": "TEST-KEY-1234-5678-9ABC"}
            )

    @pytest.mark.asyncio
    async def test_request_offline_activation_error(self, mock_client):
        """Test offline activation request with error."""
        # Mock the _request method to raise an exception
        with patch.object(mock_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = CanvusAPIError("Invalid license key", status_code=400)

            # Test the method should raise the exception
            with pytest.raises(CanvusAPIError) as exc_info:
                await mock_client.request_offline_activation("INVALID-KEY")

            # Verify the exception
            assert str(exc_info.value) == "Invalid license key"
            assert exc_info.value.status_code == 400

            # Verify the _request method was called correctly
            mock_request.assert_called_once_with(
                "GET", 
                "license/request", 
                params={"key": "INVALID-KEY"}
            )

    @pytest.mark.asyncio
    async def test_request_offline_activation_empty_key(self, mock_client):
        """Test offline activation request with empty key."""
        # Mock the _request method to raise an exception
        with patch.object(mock_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = CanvusAPIError("License key is required", status_code=400)

            # Test the method should raise the exception
            with pytest.raises(CanvusAPIError) as exc_info:
                await mock_client.request_offline_activation("")

            # Verify the exception
            assert str(exc_info.value) == "License key is required"
            assert exc_info.value.status_code == 400

            # Verify the _request method was called correctly
            mock_request.assert_called_once_with(
                "GET", 
                "license/request", 
                params={"key": ""}
            )

    @pytest.mark.asyncio
    async def test_get_license_info_success(self, mock_client):
        """Test successful license info retrieval."""
        # Mock response data
        mock_response = {
            "edition": "Professional",
            "has_expired": False,
            "is_valid": True,
            "max_clients": 10,
            "type": "subscription",
            "valid_until": "2024-12-31"
        }

        # Mock the _request method
        with patch.object(mock_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            # Test the method
            result = await mock_client.get_license_info()

            # Verify the result
            assert result == mock_response
            assert result["edition"] == "Professional"
            assert result["has_expired"] is False
            assert result["is_valid"] is True
            assert result["max_clients"] == 10

            # Verify the _request method was called correctly
            mock_request.assert_called_once_with("GET", "license")


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 