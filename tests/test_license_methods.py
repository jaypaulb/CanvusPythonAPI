"""Test license methods with mocked responses."""

from unittest.mock import AsyncMock, patch

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
            "instructions": "Use this data to complete offline activation",
        }

        # Mock the _request method
        with patch.object(
            mock_client, "_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response

            # Test the method
            result = await mock_client.request_offline_activation(
                "TEST-KEY-1234-5678-9ABC"
            )

            # Verify the result
            assert result == mock_response
            assert (
                result["request_data"]
                == "eyJ0eXBlIjoib2ZmbGluZS1hY3RpdmF0aW9uLXJlcXVlc3QiLCJkYXRhIjoiLi4uIn0="
            )
            assert result["expires_at"] == "2024-12-31T23:59:59Z"
            assert (
                result["instructions"] == "Use this data to complete offline activation"
            )

            # Verify the _request method was called correctly
            mock_request.assert_called_once_with(
                "GET", "license/request", params={"key": "TEST-KEY-1234-5678-9ABC"}
            )

    @pytest.mark.asyncio
    async def test_request_offline_activation_error(self, mock_client):
        """Test offline activation request with error."""
        # Mock the _request method to raise an exception
        with patch.object(
            mock_client, "_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = CanvusAPIError(
                "Invalid license key", status_code=400
            )

            # Test the method should raise the exception
            with pytest.raises(CanvusAPIError) as exc_info:
                await mock_client.request_offline_activation("INVALID-KEY")

            # Verify the exception
            assert str(exc_info.value) == "Invalid license key"
            assert exc_info.value.status_code == 400

            # Verify the _request method was called correctly
            mock_request.assert_called_once_with(
                "GET", "license/request", params={"key": "INVALID-KEY"}
            )

    @pytest.mark.asyncio
    async def test_request_offline_activation_empty_key(self, mock_client):
        """Test offline activation request with empty key."""
        # Mock the _request method to raise an exception
        with patch.object(
            mock_client, "_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = CanvusAPIError(
                "License key is required", status_code=400
            )

            # Test the method should raise the exception
            with pytest.raises(CanvusAPIError) as exc_info:
                await mock_client.request_offline_activation("")

            # Verify the exception
            assert str(exc_info.value) == "License key is required"
            assert exc_info.value.status_code == 400

            # Verify the _request method was called correctly
            mock_request.assert_called_once_with(
                "GET", "license/request", params={"key": ""}
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
            "valid_until": "2024-12-31",
        }

        # Mock the _request method
        with patch.object(
            mock_client, "_request", new_callable=AsyncMock
        ) as mock_request:
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

    @pytest.mark.asyncio
    async def test_install_offline_license_success(self, mock_client):
        """Test successful offline license installation."""
        # Mock response data
        mock_response = {
            "status": "success",
            "message": "License installed successfully",
            "license_info": {
                "edition": "Professional",
                "has_expired": False,
                "is_valid": True,
                "max_clients": 10,
                "type": "subscription",
                "valid_until": "2024-12-31",
            },
        }

        # Mock the _request method
        with patch.object(
            mock_client, "_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response

            # Test the method
            test_license_data = (
                "eyJ0eXBlIjoibGljZW5zZSIsImRhdGEiOiJ0ZXN0X2xpY2Vuc2VfZGF0YSJ9"
            )
            result = await mock_client.install_offline_license(test_license_data)

            # Verify the result
            assert result == mock_response
            assert result["status"] == "success"
            assert result["message"] == "License installed successfully"
            assert result["license_info"]["edition"] == "Professional"

            # Verify the _request method was called correctly
            mock_request.assert_called_once_with(
                "POST", "license", json_data={"license": test_license_data}
            )

    @pytest.mark.asyncio
    async def test_install_offline_license_error(self, mock_client):
        """Test offline license installation with error."""
        # Mock the _request method to raise an exception
        with patch.object(
            mock_client, "_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = CanvusAPIError(
                "Invalid license data", status_code=400
            )

            # Test the method should raise the exception
            with pytest.raises(CanvusAPIError) as exc_info:
                await mock_client.install_offline_license("invalid_license_data")

            # Verify the exception
            assert str(exc_info.value) == "Invalid license data"
            assert exc_info.value.status_code == 400

            # Verify the _request method was called correctly
            mock_request.assert_called_once_with(
                "POST", "license", json_data={"license": "invalid_license_data"}
            )

    @pytest.mark.asyncio
    async def test_install_offline_license_empty_data(self, mock_client):
        """Test offline license installation with empty data."""
        # Mock the _request method to raise an exception
        with patch.object(
            mock_client, "_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = CanvusAPIError(
                "License data is required", status_code=400
            )

            # Test the method should raise the exception
            with pytest.raises(CanvusAPIError) as exc_info:
                await mock_client.install_offline_license("")

            # Verify the exception
            assert str(exc_info.value) == "License data is required"
            assert exc_info.value.status_code == 400

            # Verify the _request method was called correctly
            mock_request.assert_called_once_with(
                "POST", "license", json_data={"license": ""}
            )

    @pytest.mark.asyncio
    async def test_get_audit_log_success(self, mock_client):
        """Test successful audit log retrieval."""
        # Mock response data
        mock_response = {
            "events": [
                {
                    "id": "1",
                    "author_id": "123",
                    "target_type": "user",
                    "target_id": "456",
                    "action": "created",
                    "created_at": "2024-01-01T12:00:00Z",
                    "details": {"email": "test@example.com"},
                },
                {
                    "id": "2",
                    "author_id": "123",
                    "target_type": "canvas",
                    "target_id": "789",
                    "action": "updated",
                    "created_at": "2024-01-01T13:00:00Z",
                    "details": {"name": "Test Canvas"},
                },
            ],
            "pagination": {
                "per_page": 20,
                "current_page": 1,
                "total_pages": 1,
                "total_count": 2,
            },
        }

        # Mock the _request method
        with patch.object(
            mock_client, "_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response

            # Test the method without filters
            result = await mock_client.get_audit_log()

            # Verify the result
            assert result == mock_response
            assert len(result["events"]) == 2
            assert result["events"][0]["action"] == "created"
            assert result["pagination"]["total_count"] == 2

            # Verify the _request method was called correctly
            mock_request.assert_called_once_with("GET", "audit-log", params=None)

    @pytest.mark.asyncio
    async def test_get_audit_log_with_filters(self, mock_client):
        """Test audit log retrieval with filters."""
        # Mock response data
        mock_response = {
            "events": [
                {
                    "id": "1",
                    "author_id": "123",
                    "target_type": "user",
                    "target_id": "456",
                    "action": "created",
                    "created_at": "2024-01-01T12:00:00Z",
                }
            ],
            "pagination": {
                "per_page": 10,
                "current_page": 1,
                "total_pages": 1,
                "total_count": 1,
            },
        }

        # Mock the _request method
        with patch.object(
            mock_client, "_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response

            # Test the method with filters
            filters = {
                "author_id": "123",
                "created_after": "2024-01-01T00:00:00Z",
                "per_page": 10,
            }
            result = await mock_client.get_audit_log(filters)

            # Verify the result
            assert result == mock_response
            assert len(result["events"]) == 1
            assert result["events"][0]["author_id"] == "123"

            # Verify the _request method was called correctly
            mock_request.assert_called_once_with("GET", "audit-log", params=filters)

    @pytest.mark.asyncio
    async def test_get_audit_log_error(self, mock_client):
        """Test audit log retrieval with error."""
        # Mock the _request method to raise an exception
        with patch.object(
            mock_client, "_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = CanvusAPIError("Access denied", status_code=403)

            # Test the method should raise the exception
            with pytest.raises(CanvusAPIError) as exc_info:
                await mock_client.get_audit_log()

            # Verify the exception
            assert str(exc_info.value) == "Access denied"
            assert exc_info.value.status_code == 403

            # Verify the _request method was called correctly
            mock_request.assert_called_once_with("GET", "audit-log", params=None)

    @pytest.mark.asyncio
    async def test_export_audit_log_csv_success(self, mock_client):
        """Test successful audit log CSV export."""
        # Mock response data (CSV bytes)
        mock_response = b"id,author_id,target_type,target_id,action,created_at\n1,123,user,456,created,2024-01-01T12:00:00Z\n2,123,canvas,789,updated,2024-01-01T13:00:00Z"

        # Mock the _request method
        with patch.object(
            mock_client, "_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response

            # Test the method without filters
            result = await mock_client.export_audit_log_csv()

            # Verify the result
            assert result == mock_response
            assert isinstance(result, bytes)
            assert b"id,author_id,target_type" in result

            # Verify the _request method was called correctly
            mock_request.assert_called_once_with(
                "GET", "audit-log/export-csv", params=None, return_binary=True
            )

    @pytest.mark.asyncio
    async def test_export_audit_log_csv_with_filters(self, mock_client):
        """Test audit log CSV export with filters."""
        # Mock response data (CSV bytes)
        mock_response = b"id,author_id,target_type,target_id,action,created_at\n1,123,user,456,created,2024-01-01T12:00:00Z"

        # Mock the _request method
        with patch.object(
            mock_client, "_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response

            # Test the method with filters
            filters = {"author_id": "123", "created_after": "2024-01-01T00:00:00Z"}
            result = await mock_client.export_audit_log_csv(filters)

            # Verify the result
            assert result == mock_response
            assert isinstance(result, bytes)
            assert b"123" in result

            # Verify the _request method was called correctly
            mock_request.assert_called_once_with(
                "GET", "audit-log/export-csv", params=filters, return_binary=True
            )

    @pytest.mark.asyncio
    async def test_export_audit_log_csv_error(self, mock_client):
        """Test audit log CSV export with error."""
        # Mock the _request method to raise an exception
        with patch.object(
            mock_client, "_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = CanvusAPIError("Export failed", status_code=500)

            # Test the method should raise the exception
            with pytest.raises(CanvusAPIError) as exc_info:
                await mock_client.export_audit_log_csv()

            # Verify the exception
            assert str(exc_info.value) == "Export failed"
            assert exc_info.value.status_code == 500

            # Verify the _request method was called correctly
            mock_request.assert_called_once_with(
                "GET", "audit-log/export-csv", params=None, return_binary=True
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
