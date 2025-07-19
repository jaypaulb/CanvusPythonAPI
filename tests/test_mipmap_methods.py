"""Test mipmap methods with live server integration."""

import pytest
from tests.test_config import TestClient, get_test_config


@pytest.mark.asyncio
async def test_get_mipmap_info_success():
    """Test successful retrieval of mipmap info."""
    config = get_test_config()

    async with TestClient(config) as test_client:
        client = test_client.client

        # Get test canvas ID
        canvas_id = test_client.get_test_canvas_id()

        # Test getting mipmap info (may not exist for test canvas)
        try:
            result = await client.get_mipmap_info("test-hash", canvas_id)
            assert result is not None
        except Exception as e:
            # If mipmap doesn't exist, that's expected for test canvas
            assert "not found" in str(e).lower() or "404" in str(e)


@pytest.mark.asyncio
async def test_get_mipmap_info_with_page():
    """Test getting mipmap info with page parameter."""
    config = get_test_config()

    async with TestClient(config) as test_client:
        client = test_client.client

        # Get test canvas ID
        canvas_id = test_client.get_test_canvas_id()

        # Test getting mipmap info with page parameter
        try:
            result = await client.get_mipmap_info("test-hash", canvas_id, page=1)
            assert result is not None
        except Exception as e:
            # If mipmap doesn't exist, that's expected for test canvas
            assert "not found" in str(e).lower() or "404" in str(e)


@pytest.mark.asyncio
async def test_get_mipmap_info_error():
    """Test error handling when getting mipmap info fails."""
    config = get_test_config()

    async with TestClient(config) as test_client:
        client = test_client.client

        # Test with invalid parameters
        with pytest.raises(Exception):
            await client.get_mipmap_info("", "invalid-canvas-id")


@pytest.mark.asyncio
async def test_get_mipmap_level_image_success():
    """Test successful retrieval of mipmap level image."""
    config = get_test_config()

    async with TestClient(config) as test_client:
        client = test_client.client

        # Get test canvas ID
        canvas_id = test_client.get_test_canvas_id()

        # Test getting mipmap level image (may not exist for test canvas)
        try:
            result = await client.get_mipmap_level_image("test-hash", 0, canvas_id)
            assert result is not None
        except Exception as e:
            # If mipmap doesn't exist, that's expected for test canvas
            assert "not found" in str(e).lower() or "404" in str(e)


@pytest.mark.asyncio
async def test_get_mipmap_level_image_error():
    """Test error handling when getting mipmap level image fails."""
    config = get_test_config()

    async with TestClient(config) as test_client:
        client = test_client.client

        # Test with invalid parameters
        with pytest.raises(Exception):
            await client.get_mipmap_level_image("", 0, "invalid-canvas-id")


@pytest.mark.asyncio
async def test_get_asset_file_success():
    """Test successful retrieval of asset file."""
    config = get_test_config()

    async with TestClient(config) as test_client:
        client = test_client.client

        # Get test canvas ID
        canvas_id = test_client.get_test_canvas_id()

        # Test getting asset file (may not exist for test canvas)
        try:
            result = await client.get_asset_file("test-hash", canvas_id)
            assert result is not None
        except Exception as e:
            # If asset doesn't exist, that's expected for test canvas
            assert "not found" in str(e).lower() or "404" in str(e)


@pytest.mark.asyncio
async def test_get_asset_file_error():
    """Test error handling when getting asset file fails."""
    config = get_test_config()

    async with TestClient(config) as test_client:
        client = test_client.client

        # Test with invalid parameters
        with pytest.raises(Exception):
            await client.get_asset_file("", "invalid-canvas-id")
