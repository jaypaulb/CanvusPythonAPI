"""Test mipmap methods with mocked responses."""

import asyncio
from unittest.mock import AsyncMock, patch
from typing import Dict, Any

import pytest

from canvus_api import CanvusClient
from canvus_api.exceptions import CanvusAPIError


class TestMipmapMethods:
    """Test mipmap-related methods."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        return CanvusClient("https://test.example.com", "test-api-key")

    @pytest.mark.asyncio
    async def test_get_mipmap_info_success(self, mock_client):
        """Test successful mipmap info retrieval."""
        # Mock response data
        mock_response = {
            "resolution": {"width": 1024, "height": 768},
            "max_level": 4,
            "pages": 1
        }

        # Mock the _request method
        with patch.object(mock_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            # Test the method
            result = await mock_client.get_mipmap_info("abcdef123456", "canvas-123")

            # Verify the result
            assert result == mock_response
            assert result["resolution"]["width"] == 1024
            assert result["resolution"]["height"] == 768
            assert result["max_level"] == 4
            assert result["pages"] == 1

            # Verify the _request method was called correctly
            mock_request.assert_called_once_with(
                "GET", 
                "mipmaps/abcdef123456", 
                headers={"canvas-id": "canvas-123"}, 
                params=None
            )

    @pytest.mark.asyncio
    async def test_get_mipmap_info_with_page(self, mock_client):
        """Test mipmap info retrieval with page parameter."""
        # Mock response data
        mock_response = {
            "resolution": {"width": 800, "height": 600},
            "max_level": 3,
            "pages": 5
        }

        # Mock the _request method
        with patch.object(mock_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            # Test the method with page parameter
            result = await mock_client.get_mipmap_info("abcdef123456", "canvas-123", page=2)

            # Verify the result
            assert result == mock_response
            assert result["resolution"]["width"] == 800
            assert result["pages"] == 5

            # Verify the _request method was called correctly
            mock_request.assert_called_once_with(
                "GET", 
                "mipmaps/abcdef123456", 
                headers={"canvas-id": "canvas-123"}, 
                params={"page": 2}
            )

    @pytest.mark.asyncio
    async def test_get_mipmap_info_error(self, mock_client):
        """Test mipmap info retrieval with error."""
        # Mock the _request method to raise an exception
        with patch.object(mock_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = CanvusAPIError("Asset not found", status_code=404)

            # Test the method should raise the exception
            with pytest.raises(CanvusAPIError) as exc_info:
                await mock_client.get_mipmap_info("invalid_hash", "canvas-123")

            # Verify the exception
            assert str(exc_info.value) == "Asset not found"
            assert exc_info.value.status_code == 404

            # Verify the _request method was called correctly
            mock_request.assert_called_once_with(
                "GET", 
                "mipmaps/invalid_hash", 
                headers={"canvas-id": "canvas-123"}, 
                params=None
            )

    @pytest.mark.asyncio
    async def test_get_mipmap_level_image_success(self, mock_client):
        """Test successful mipmap level image retrieval."""
        # Mock response data (binary image data)
        mock_response = b"fake_mipmap_image_data"

        # Mock the _request method
        with patch.object(mock_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            # Test parameters
            test_hash = "abcdef123456"
            test_level = 2
            test_canvas_id = "canvas-123"

            # Call the method
            result = await mock_client.get_mipmap_level_image(test_hash, test_level, test_canvas_id)

            # Verify the result
            assert result == mock_response

            # Verify the _request method was called correctly
            mock_request.assert_called_once_with(
                "GET", 
                f"mipmaps/{test_hash}/{test_level}", 
                headers={"canvas-id": test_canvas_id},
                params=None,
                return_binary=True
            )

    @pytest.mark.asyncio
    async def test_get_asset_file_success(self, mock_client):
        """Test successful asset file retrieval."""
        # Mock response data (binary file data)
        mock_response = b"fake_image_data_here"

        # Mock the _request method
        with patch.object(mock_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            # Test parameters
            test_hash = "abcdef123456"
            test_canvas_id = "canvas-123"

            # Call the method
            result = await mock_client.get_asset_file(test_hash, test_canvas_id)

            # Verify the result
            assert result == mock_response

            # Verify the _request method was called correctly
            mock_request.assert_called_once_with(
                "GET", 
                f"assets/{test_hash}", 
                headers={"canvas-id": test_canvas_id},
                return_binary=True
            )

    @pytest.mark.asyncio
    async def test_get_asset_file_error(self, mock_client):
        """Test asset file retrieval error handling."""
        # Mock the _request method to raise an error
        with patch.object(mock_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = CanvusAPIError("Asset not found", status_code=404)

            # Test parameters
            test_hash = "invalid_hash"
            test_canvas_id = "canvas-123"

            # Call the method and expect an error
            with pytest.raises(CanvusAPIError) as exc_info:
                await mock_client.get_asset_file(test_hash, test_canvas_id)

            # Verify the error
            assert "Asset not found" in str(exc_info.value)
            assert exc_info.value.status_code == 404

            # Verify the _request method was called correctly
            mock_request.assert_called_once_with(
                "GET", 
                f"assets/{test_hash}", 
                headers={"canvas-id": test_canvas_id},
                return_binary=True
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 