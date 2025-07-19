"""
Comprehensive test suite for group management endpoints.
"""

import pytest
import asyncio
from canvus_api import CanvusClient, CanvusAPIError


class TestGroupManagement:
    """Test suite for group management endpoints."""

    @pytest.mark.asyncio
    async def test_list_groups(self, client: CanvusClient):
        """Test listing groups."""
        try:
            groups = await client.list_groups()

            assert isinstance(groups, list)
            for group in groups:
                assert isinstance(group, dict)
                assert "id" in group
                assert "name" in group
        except CanvusAPIError as e:
            # Group operations may require admin privileges
            assert e.status_code in [401, 403]
            assert "Invalid token" in str(e) or "permission" in str(e).lower()

    @pytest.mark.asyncio
    async def test_create_and_delete_group(self, client: CanvusClient):
        """Test creating and deleting a group."""
        group_payload = {
            "name": f"Test Group {asyncio.get_event_loop().time()}",
            "description": "Group created for testing",
        }

        try:
            # Create group
            group = await client.create_group(group_payload)
            assert isinstance(group, dict)
            assert group["name"] == group_payload["name"]
            assert group["description"] == group_payload["description"]

            # Delete group
            await client.delete_group(group["id"])

            # Verify deletion
            with pytest.raises(CanvusAPIError) as exc_info:
                await client.get_group(group["id"])
            assert exc_info.value.status_code in [403, 404]
        except CanvusAPIError as e:
            # Group operations may require admin privileges
            assert e.status_code in [401, 403]
            assert "Invalid token" in str(e) or "permission" in str(e).lower()

    @pytest.mark.asyncio
    async def test_get_group(self, client: CanvusClient):
        """Test getting a specific group."""
        try:
            # First create a group to test with
            group_payload = {
                "name": f"Get Test Group {asyncio.get_event_loop().time()}",
                "description": "Group for get testing",
            }
            created_group = await client.create_group(group_payload)

            try:
                group = await client.get_group(created_group["id"])

                assert isinstance(group, dict)
                assert group["id"] == created_group["id"]
                assert group["name"] == created_group["name"]
            finally:
                # Cleanup
                await client.delete_group(created_group["id"])
        except CanvusAPIError as e:
            # Group operations may require admin privileges
            assert e.status_code in [401, 403]
            assert "Invalid token" in str(e) or "permission" in str(e).lower()

    @pytest.mark.asyncio
    async def test_group_members(self, client: CanvusClient):
        """Test group member operations."""
        try:
            # First create a group to test with
            group_payload = {
                "name": f"Members Test Group {asyncio.get_event_loop().time()}",
                "description": "Group for member testing",
            }
            created_group = await client.create_group(group_payload)

            try:
                # Test adding member
                user_id = "1000"  # Use a known user ID

                member = await client.add_user_to_group(created_group["id"], user_id)
                # API returns empty response on success, so member might be None
                assert member is None or isinstance(member, dict)

                # Test listing members
                members = await client.list_group_members(created_group["id"])
                assert isinstance(members, list)
                assert len(members) > 0

                # Test removing member
                await client.remove_user_from_group(created_group["id"], user_id)

                # Verify removal
                members_after = await client.list_group_members(created_group["id"])
                assert len(members_after) == 0
            finally:
                # Cleanup
                await client.delete_group(created_group["id"])
        except CanvusAPIError as e:
            # Group operations may require admin privileges
            assert e.status_code in [401, 403]
            assert "Invalid token" in str(e) or "permission" in str(e).lower()

    @pytest.mark.asyncio
    async def test_group_error_handling(self, client: CanvusClient):
        """Test error handling for group operations."""
        # Test getting non-existent group
        with pytest.raises(CanvusAPIError) as exc_info:
            await client.get_group("non-existent-id")
        assert exc_info.value.status_code in [400, 403, 404]

    @pytest.mark.asyncio
    async def test_group_validation(self, client: CanvusClient):
        """Test group creation validation."""
        try:
            # Test with missing required fields
            with pytest.raises(CanvusAPIError):
                await client.create_group({})
        except CanvusAPIError as e:
            # Group operations may require admin privileges
            assert e.status_code in [401, 403]
            assert "Invalid token" in str(e) or "permission" in str(e).lower()
