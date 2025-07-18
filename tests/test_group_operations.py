"""
Test suite for Canvus group operations.
"""

import pytest
from unittest.mock import AsyncMock
from canvus_api import CanvusClient


@pytest.mark.asyncio
async def test_add_user_to_group_success():
    """Test successful addition of user to group."""
    client = CanvusClient("https://test.com", "test-token")

    # Mock the _request method
    mock_response = {"success": True, "message": "User added to group"}
    client._request = AsyncMock(return_value=mock_response)

    # Test the method
    result = await client.add_user_to_group("group-123", "user-456")

    # Verify the result
    assert result == mock_response

    # Verify the request was made correctly
    client._request.assert_called_once_with(
        "POST", "groups/group-123/members", json_data={"user_id": "user-456"}
    )


@pytest.mark.asyncio
async def test_add_user_to_group_error():
    """Test error handling when adding user to group fails."""
    client = CanvusClient("https://test.com", "test-token")

    # Mock the _request method to raise an exception
    client._request = AsyncMock(side_effect=Exception("API Error"))

    # Test that the exception is propagated
    with pytest.raises(Exception, match="API Error"):
        await client.add_user_to_group("group-123", "user-456")


@pytest.mark.asyncio
async def test_add_user_to_group_validation():
    """Test parameter validation for add_user_to_group."""
    client = CanvusClient("https://test.com", "test-token")

    # Test with empty group_id
    with pytest.raises(Exception):
        await client.add_user_to_group("", "user-456")

    # Test with empty user_id
    with pytest.raises(Exception):
        await client.add_user_to_group("group-123", "")


@pytest.mark.asyncio
async def test_list_group_members_success():
    """Test successful listing of group members."""
    client = CanvusClient("https://test.com", "test-token")

    # Mock the _request method
    mock_response = [
        {"id": "user-1", "name": "User One", "email": "user1@example.com"},
        {"id": "user-2", "name": "User Two", "email": "user2@example.com"},
    ]
    client._request = AsyncMock(return_value=mock_response)

    # Test the method
    result = await client.list_group_members("group-123")

    # Verify the result
    assert result == mock_response
    assert len(result) == 2
    assert result[0]["id"] == "user-1"
    assert result[1]["id"] == "user-2"

    # Verify the request was made correctly
    client._request.assert_called_once_with("GET", "groups/group-123/members")


@pytest.mark.asyncio
async def test_list_group_members_error():
    """Test error handling when listing group members fails."""
    client = CanvusClient("https://test.com", "test-token")

    # Mock the _request method to raise an exception
    client._request = AsyncMock(side_effect=Exception("API Error"))

    # Test that the exception is propagated
    with pytest.raises(Exception, match="API Error"):
        await client.list_group_members("group-123")


@pytest.mark.asyncio
async def test_list_group_members_empty_group():
    """Test listing members of an empty group."""
    client = CanvusClient("https://test.com", "test-token")

    # Mock the _request method to return empty list
    mock_response = []
    client._request = AsyncMock(return_value=mock_response)

    # Test the method
    result = await client.list_group_members("group-123")

    # Verify the result
    assert result == []
    assert len(result) == 0


@pytest.mark.asyncio
async def test_remove_user_from_group_success():
    """Test successful removal of user from group."""
    client = CanvusClient("https://test.com", "test-token")

    # Mock the _request method
    client._request = AsyncMock(return_value=None)

    # Test the method
    await client.remove_user_from_group("group-123", "user-456")

    # Verify the request was made correctly
    client._request.assert_called_once_with(
        "DELETE", "groups/group-123/members/user-456"
    )


@pytest.mark.asyncio
async def test_remove_user_from_group_error():
    """Test error handling when removing user from group fails."""
    client = CanvusClient("https://test.com", "test-token")

    # Mock the _request method to raise an exception
    client._request = AsyncMock(side_effect=Exception("API Error"))

    # Test that the exception is propagated
    with pytest.raises(Exception, match="API Error"):
        await client.remove_user_from_group("group-123", "user-456")


@pytest.mark.asyncio
async def test_remove_user_from_group_validation():
    """Test parameter validation for remove_user_from_group."""
    client = CanvusClient("https://test.com", "test-token")

    # Test with empty group_id
    with pytest.raises(Exception):
        await client.remove_user_from_group("", "user-456")

    # Test with empty user_id
    with pytest.raises(Exception):
        await client.remove_user_from_group("group-123", "")


@pytest.mark.asyncio
async def test_get_client_success():
    """Test successful retrieval of client."""
    client = CanvusClient("https://test.com", "test-token")

    # Mock the _request method
    mock_response = {"id": "client-123", "name": "Test Client", "status": "active"}
    client._request = AsyncMock(return_value=mock_response)

    # Test the method
    result = await client.get_client("client-123")

    # Verify the result
    assert result == mock_response
    assert result["id"] == "client-123"
    assert result["name"] == "Test Client"

    # Verify the request was made correctly
    client._request.assert_called_once_with("GET", "clients/client-123")


@pytest.mark.asyncio
async def test_get_client_error():
    """Test error handling when getting client fails."""
    client = CanvusClient("https://test.com", "test-token")

    # Mock the _request method to raise an exception
    client._request = AsyncMock(side_effect=Exception("API Error"))

    # Test that the exception is propagated
    with pytest.raises(Exception, match="API Error"):
        await client.get_client("client-123")


@pytest.mark.asyncio
async def test_get_client_not_found():
    """Test getting a non-existent client."""
    client = CanvusClient("https://test.com", "test-token")

    # Mock the _request method to raise a not found error
    client._request = AsyncMock(side_effect=Exception("Client not found"))

    # Test that the exception is propagated
    with pytest.raises(Exception, match="Client not found"):
        await client.get_client("non-existent-client")
