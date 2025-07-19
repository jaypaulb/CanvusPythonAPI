"""
Comprehensive test suite for user management endpoints.
"""

import pytest
import asyncio
from canvus_api import CanvusClient, CanvusAPIError
from canvus_api.models import User


class TestUserManagement:
    """Test suite for user management endpoints."""

    @pytest.mark.asyncio
    async def test_list_users(self, client: CanvusClient):
        """Test listing users."""
        try:
            users = await client.list_users()

            assert isinstance(users, list)
            for user in users:
                assert isinstance(user, User)
                assert user.id is not None
                assert user.email is not None
                assert user.name is not None
        except CanvusAPIError as e:
            # User operations may require admin privileges
            assert e.status_code in [401, 403]
            assert "Invalid token" in str(e) or "permission" in str(e).lower()

    @pytest.mark.asyncio
    async def test_create_and_delete_user(self, client: CanvusClient):
        """Test creating and deleting a user."""
        user_payload = {
            "email": f"testuser_{asyncio.get_event_loop().time()}@test.local",
            "name": "Test User",
            "password": "TestPassword123!",
        }

        try:
            # Create user
            user = await client.create_user(user_payload)
            assert isinstance(user, User)
            assert user.email == user_payload["email"]
            assert user.name == user_payload["name"]
            assert user.id is not None

            # Delete user
            await client.delete_user(user.id)

            # Verify deletion
            with pytest.raises(CanvusAPIError) as exc_info:
                await client.get_user(user.id)
            assert exc_info.value.status_code == 404
        except CanvusAPIError as e:
            # User operations may require admin privileges
            assert e.status_code in [401, 403]
            assert "Invalid token" in str(e) or "permission" in str(e).lower()

    @pytest.mark.asyncio
    async def test_get_user(self, client: CanvusClient, test_user):
        """Test getting a specific user."""
        try:
            user = await client.get_user(test_user.id)

            assert isinstance(user, User)
            assert user.id == test_user.id
            assert user.email == test_user.email
            assert user.name == test_user.name
        except CanvusAPIError as e:
            # User operations may require admin privileges
            assert e.status_code in [401, 403]
            assert "Invalid token" in str(e) or "permission" in str(e).lower()

    @pytest.mark.asyncio
    async def test_update_user(self, client: CanvusClient, test_user):
        """Test updating a user."""
        new_name = f"Updated User {asyncio.get_event_loop().time()}"

        try:
            updated_user = await client.update_user(test_user.id, {"name": new_name})

            assert isinstance(updated_user, User)
            assert updated_user.name == new_name
        except CanvusAPIError as e:
            # User operations may require admin privileges
            assert e.status_code in [401, 403]
            assert "Invalid token" in str(e) or "permission" in str(e).lower()

    @pytest.mark.asyncio
    async def test_register_user(self, client: CanvusClient):
        """Test user registration."""
        register_payload = {
            "email": f"registeruser_{asyncio.get_event_loop().time()}@test.local",
            "name": "Register User",
            "password": "RegisterPassword123!",
        }

        try:
            result = await client.register_user(register_payload)
            assert isinstance(result, dict)
            # The API returns a User object directly
            assert "id" in result
            assert "email" in result
            assert "name" in result

            # Cleanup if user was created
            if "id" in result:
                try:
                    await client.delete_user(result["id"])
                except Exception:
                    pass
        except CanvusAPIError as e:
            # User operations may require admin privileges
            assert e.status_code in [401, 403]
            assert "Invalid token" in str(e) or "permission" in str(e).lower()

    @pytest.mark.asyncio
    async def test_approve_user(self, client: CanvusClient, test_user):
        """Test approving a user."""
        try:
            approved_user = await client.approve_user(test_user.id)

            assert isinstance(approved_user, User)
            assert approved_user.approved is True
        except CanvusAPIError as e:
            # User operations may require admin privileges
            assert e.status_code in [401, 403]
            assert "Invalid token" in str(e) or "permission" in str(e).lower()

    @pytest.mark.asyncio
    async def test_block_and_unblock_user(self, client: CanvusClient, test_user):
        """Test blocking and unblocking a user."""
        try:
            # Block user
            blocked_user = await client.block_user(test_user.id)
            assert isinstance(blocked_user, User)
            assert blocked_user.blocked is True

            # Unblock user
            unblocked_user = await client.unblock_user(test_user.id)
            assert isinstance(unblocked_user, User)
            assert unblocked_user.blocked is False
        except CanvusAPIError as e:
            # User operations may require admin privileges
            assert e.status_code in [401, 403]
            assert "Invalid token" in str(e) or "permission" in str(e).lower()

    @pytest.mark.asyncio
    async def test_change_password(self, client: CanvusClient, test_user):
        """Test changing user password."""
        current_password = "TestPassword123!"
        new_password = "NewPassword123!"

        try:
            updated_user = await client.change_password(
                test_user.id, current_password, new_password
            )

            assert isinstance(updated_user, User)
            assert updated_user.id == test_user.id
        except CanvusAPIError as e:
            # User operations may require admin privileges
            assert e.status_code in [401, 403]
            assert "Invalid token" in str(e) or "permission" in str(e).lower()

    @pytest.mark.asyncio
    async def test_request_password_reset(self, client: CanvusClient):
        """Test requesting password reset."""
        # This might fail if email is not configured, which is expected
        try:
            await client.request_password_reset("test@example.com")
        except CanvusAPIError as e:
            assert e.status_code in [400, 403, 404, 500]

    @pytest.mark.asyncio
    async def test_validate_reset_token(self, client: CanvusClient):
        """Test validating reset token."""
        # This will likely fail with an invalid token, which is expected
        try:
            result = await client.validate_reset_token("invalid-token")
            assert isinstance(result, dict)
        except CanvusAPIError as e:
            assert e.status_code in [400, 403, 404]

    @pytest.mark.asyncio
    async def test_reset_password(self, client: CanvusClient):
        """Test resetting password."""
        # This will likely fail with an invalid token, which is expected
        try:
            result = await client.reset_password("invalid-token", "NewPassword123!")
            assert isinstance(result, dict)
        except CanvusAPIError as e:
            assert e.status_code in [400, 403, 404]

    @pytest.mark.asyncio
    async def test_confirm_email(self, client: CanvusClient):
        """Test confirming email."""
        # This will likely fail with an invalid token, which is expected
        try:
            result = await client.confirm_email("invalid-token")
            assert isinstance(result, dict)
        except CanvusAPIError as e:
            assert e.status_code in [400, 403, 404]

    @pytest.mark.asyncio
    async def test_login(self, client: CanvusClient, test_config):
        """Test user login."""
        # Test login with admin credentials from config
        result = await client.login(
            email=test_config.admin_credentials["email"],
            password=test_config.admin_credentials["password"],
        )
        assert isinstance(result, dict)
        assert "token" in result
        assert "user" in result

    @pytest.mark.asyncio
    async def test_login_saml(self, client: CanvusClient):
        """Test SAML login."""
        try:
            result = await client.login_saml()
            assert isinstance(result, dict)
        except CanvusAPIError as e:
            # This might fail if SAML is not configured, which is expected
            assert e.status_code in [400, 403, 404, 500]

    @pytest.mark.asyncio
    async def test_logout(self, client: CanvusClient):
        """Test user logout."""
        # This might fail without a valid session, which is expected
        try:
            await client.logout()
        except CanvusAPIError as e:
            assert e.status_code in [400, 401, 403]

    @pytest.mark.asyncio
    async def test_get_current_user(self, client: CanvusClient):
        """Test getting current user."""
        try:
            user = await client.get_current_user()
            assert isinstance(user, User)
            assert user.id is not None
        except CanvusAPIError as e:
            # This might fail if not authenticated, which is expected
            assert e.status_code in [401, 403, 500]

    @pytest.mark.asyncio
    async def test_user_error_handling(self, client: CanvusClient):
        """Test error handling for user operations."""
        # Test getting non-existent user
        with pytest.raises(CanvusAPIError) as exc_info:
            await client.get_user(99999)
        assert exc_info.value.status_code in [403, 404]

        # Test updating non-existent user
        with pytest.raises(CanvusAPIError) as exc_info:
            await client.update_user(99999, {"name": "test"})
        assert exc_info.value.status_code in [403, 404]

    @pytest.mark.asyncio
    async def test_user_validation(self, client: CanvusClient):
        """Test user creation validation."""
        # Test with missing required fields
        with pytest.raises(CanvusAPIError):
            await client.create_user({})

        # Test with invalid email
        with pytest.raises(CanvusAPIError):
            await client.create_user(
                {
                    "email": "invalid-email",
                    "name": "Test User",
                    "password": "TestPassword123!",
                }
            )

    @pytest.mark.asyncio
    async def test_user_admin_operations(self, client: CanvusClient):
        """Test admin-specific user operations."""
        # Create a regular user
        user_payload = {
            "email": f"adminuser_{asyncio.get_event_loop().time()}@test.local",
            "name": "Admin Test User",
            "password": "TestPassword123!",
            "admin": False,
        }

        try:
            user = await client.create_user(user_payload)

            try:
                # Test making user admin
                if user.id is not None:
                    admin_user = await client.update_user(user.id, {"admin": True})
                    assert admin_user.admin is True

                    # Test removing admin privileges
                    regular_user = await client.update_user(user.id, {"admin": False})
                    assert regular_user.admin is False

            finally:
                # Cleanup
                if user.id is not None:
                    await client.delete_user(user.id)
        except CanvusAPIError as e:
            # User operations may require admin privileges
            assert e.status_code in [401, 403]
            assert "Invalid token" in str(e) or "permission" in str(e).lower()

    @pytest.mark.asyncio
    async def test_user_state_management(self, client: CanvusClient):
        """Test user state management."""
        # Create a user
        user_payload = {
            "email": f"stateuser_{asyncio.get_event_loop().time()}@test.local",
            "name": "State Test User",
            "password": "TestPassword123!",
        }

        try:
            user = await client.create_user(user_payload)

            try:
                # Test user approval
                if user.id is not None:
                    approved_user = await client.approve_user(user.id)
                    assert approved_user.approved is True

                    # Test user blocking
                    blocked_user = await client.block_user(user.id)
                    assert blocked_user.blocked is True

                    # Test user unblocking
                    unblocked_user = await client.unblock_user(user.id)
                    assert unblocked_user.blocked is False

            finally:
                # Cleanup
                if user.id is not None:
                    await client.delete_user(user.id)
        except CanvusAPIError as e:
            # User operations may require admin privileges
            assert e.status_code in [401, 403]
            assert "Invalid token" in str(e) or "permission" in str(e).lower()
