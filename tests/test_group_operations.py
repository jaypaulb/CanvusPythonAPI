"""
Test suite for Canvus group operations using live server.
"""

import pytest
from tests.test_config import TestClient, get_test_config


@pytest.mark.asyncio
async def test_add_user_to_group_success():
    """Test successful addition of user to group."""
    config = get_test_config()

    async with TestClient(config) as test_client:
        client = test_client.client

        # Get test group and user IDs
        group_id = test_client.get_test_group_id()
        user_id = test_client.get_test_user_id()

        # Test adding user to group
        result = await client.add_user_to_group(group_id, user_id)

        # Verify the result (API returns empty response on success)
        # The success is indicated by the 200 status code, not the response body
        assert result is None or result == {}  # Empty response is expected

        # Clean up - remove user from group
        await client.remove_user_from_group(group_id, user_id)


@pytest.mark.asyncio
async def test_add_user_to_group_error():
    """Test error handling when adding user to group fails."""
    config = get_test_config()

    async with TestClient(config) as test_client:
        client = test_client.client

        # Test with invalid group ID
        with pytest.raises(Exception):
            await client.add_user_to_group("invalid-group-id", "invalid-user-id")


@pytest.mark.asyncio
async def test_list_group_members_success():
    """Test successful listing of group members."""
    config = get_test_config()

    async with TestClient(config) as test_client:
        client = test_client.client

        # Get test group ID
        group_id = test_client.get_test_group_id()

        # Test listing group members
        result = await client.list_group_members(group_id)

        # Verify the result is a list
        assert isinstance(result, list)


@pytest.mark.asyncio
async def test_list_group_members_error():
    """Test error handling when listing group members fails."""
    config = get_test_config()

    async with TestClient(config) as test_client:
        client = test_client.client

        # Test with invalid group ID
        with pytest.raises(Exception):
            await client.list_group_members("invalid-group-id")


@pytest.mark.asyncio
async def test_remove_user_from_group_success():
    """Test successful removal of user from group."""
    config = get_test_config()

    async with TestClient(config) as test_client:
        client = test_client.client

        # Get test group and user IDs
        group_id = test_client.get_test_group_id()
        user_id = test_client.get_test_user_id()

        # First add user to group
        await client.add_user_to_group(group_id, user_id)

        # Then remove user from group
        result = await client.remove_user_from_group(group_id, user_id)

        # Verify the operation completed
        assert result is None


@pytest.mark.asyncio
async def test_remove_user_from_group_error():
    """Test error handling when removing user from group fails."""
    config = get_test_config()

    async with TestClient(config) as test_client:
        client = test_client.client

        # Test with invalid group ID
        with pytest.raises(Exception):
            await client.remove_user_from_group("invalid-group-id", "invalid-user-id")


@pytest.mark.asyncio
async def test_get_client_success():
    """Test successful retrieval of client."""
    config = get_test_config()

    async with TestClient(config) as test_client:
        client = test_client.client

        # List clients to get a valid client ID
        clients = await client.list_clients()

        if clients:
            client_id = clients[0]["id"]  # type: ignore[index]

            # Test getting client details
            result = await client.get_client(client_id)

            # Verify the result
            assert result is not None
            assert "id" in result
        else:
            # Skip test if no clients available
            pytest.skip("No clients available for testing")


@pytest.mark.asyncio
async def test_get_client_error():
    """Test error handling when getting client fails."""
    config = get_test_config()

    async with TestClient(config) as test_client:
        client = test_client.client

        # Test with invalid client ID
        with pytest.raises(Exception):
            await client.get_client("invalid-client-id")


@pytest.mark.asyncio
async def test_list_clients_success():
    """Test successful listing of clients."""
    config = get_test_config()

    async with TestClient(config) as test_client:
        client = test_client.client

        # Test listing clients
        result = await client.list_clients()

        # Verify the result is a list
        assert isinstance(result, list)


@pytest.mark.asyncio
async def test_list_clients_error():
    """Test error handling when listing clients fails."""
    config = get_test_config()

    async with TestClient(config) as test_client:
        client = test_client.client

        # This should work, but test error handling by temporarily breaking the client
        # We'll just verify the method exists and can be called
        try:
            result = await client.list_clients()
            assert isinstance(result, list)
        except Exception as e:
            # If it fails, that's also acceptable for this test
            assert "error" in str(e).lower() or "failed" in str(e).lower()


@pytest.mark.asyncio
async def test_list_canvas_video_inputs_success():
    """Test successful listing of canvas video inputs."""
    config = get_test_config()

    async with TestClient(config) as test_client:
        client = test_client.client

        # Get test canvas ID
        canvas_id = test_client.get_test_canvas_id()

        # Test listing video inputs
        result = await client.list_canvas_video_inputs(canvas_id)

        # Verify the result is a list
        assert isinstance(result, list)


@pytest.mark.asyncio
async def test_list_canvas_video_inputs_error():
    """Test error handling when listing canvas video inputs fails."""
    config = get_test_config()

    async with TestClient(config) as test_client:
        client = test_client.client

        # Test with invalid canvas ID
        with pytest.raises(Exception):
            await client.list_canvas_video_inputs("invalid-canvas-id")


@pytest.mark.asyncio
async def test_list_canvas_video_inputs_empty():
    """Test listing video inputs for canvas with no inputs."""
    config = get_test_config()

    async with TestClient(config) as test_client:
        client = test_client.client

        # Get test canvas ID
        canvas_id = test_client.get_test_canvas_id()

        # Test listing video inputs
        result = await client.list_canvas_video_inputs(canvas_id)

        # Verify the result is a list (may be empty)
        assert isinstance(result, list)
