"""
Test configuration and utilities for Canvus API integration tests.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from canvus_api import CanvusClient


class TestConfig:
    """Configuration manager for integration tests."""

    def __init__(self, config_file: str = "tests/test_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        self._test_data = {}

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        config_path = Path(self.config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Test config file not found: {self.config_file}")

        with open(config_path, "r") as f:
            return json.load(f)

    @property
    def server_url(self) -> str:
        """Get the server base URL."""
        return self.config["server"]["base_url"]

    @property
    def api_key(self) -> str:
        """Get the API key."""
        return self.config["authentication"]["api_key"]

    @property
    def verify_ssl(self) -> bool:
        """Get SSL verification setting."""
        return self.config["server"].get("verify_ssl", True)

    @property
    def admin_credentials(self) -> Dict[str, str]:
        """Get admin user credentials."""
        return self.config["authentication"]["admin_user"]

    @property
    def user_credentials(self) -> Dict[str, str]:
        """Get regular user credentials."""
        return self.config["authentication"]["regular_user"]

    @property
    def test_files(self) -> Dict[str, str]:
        """Get test file paths."""
        return self.config["test_files"]

    @property
    def test_settings(self) -> Dict[str, Any]:
        """Get test settings."""
        return self.config["test_settings"]

    def get_test_data(self, key: str) -> Dict[str, Any]:
        """Get test data by key."""
        return self.config["test_data"].get(key, {})

    def set_test_data(self, key: str, data: Dict[str, Any]) -> None:
        """Set test data for a key."""
        self._test_data[key] = data

    def get_test_data_id(self, key: str, id_field: str = "id") -> Optional[str]:
        """Get the ID from test data."""
        data = self._test_data.get(key) or self.config["test_data"].get(key, {})
        return data.get(id_field)


class TestDataManager:
    """Manages test data creation and cleanup."""

    def __init__(self, client: CanvusClient, config: TestConfig):
        self.client = client
        self.config = config
        self.created_resources = []

    async def setup_test_environment(self) -> None:
        """Set up the test environment with required data."""
        if not self.config.test_settings["create_test_data"]:
            return

        print("Setting up test environment...")

        # Create test folder with unique name
        folder_data = await self._create_test_folder()
        self.config.set_test_data("test_folder", folder_data)

        # Create test canvas
        canvas_data = await self._create_test_canvas(folder_data["id"])
        self.config.set_test_data("test_canvas", canvas_data)

        # Create test group with unique name
        group_data = await self._create_test_group()
        self.config.set_test_data("test_group", group_data)

        # Skip user creation if it already exists
        try:
            user_data = await self._create_test_user()
            self.config.set_test_data("test_user", user_data)
        except Exception as e:
            if "already in use" in str(e):
                print("Test user already exists, skipping creation")
                # Try to find existing user
                users = await self.client.list_users()
                for user in users:
                    if user.email == self.config.get_test_data("test_user")["email"]:
                        self.config.set_test_data(
                            "test_user",
                            (
                                user.model_dump()
                                if hasattr(user, "model_dump")
                                else dict(user)
                            ),
                        )
                        break
            else:
                raise

        print("Test environment setup complete!")

    async def cleanup_test_environment(self) -> None:
        """Clean up test environment."""
        if not self.config.test_settings["cleanup_after_tests"]:
            return

        print("Cleaning up test environment...")

        # Clean up in reverse order of creation
        for resource in reversed(self.created_resources):
            try:
                await self._delete_resource(resource)
            except Exception as e:
                print(f"Warning: Failed to clean up {resource['type']}: {e}")

        self.created_resources.clear()
        print("Test environment cleanup complete!")

    async def _create_test_folder(self) -> Dict[str, Any]:
        """Create a test folder."""
        folder_payload = self.config.get_test_data("test_folder").copy()
        # Add timestamp to make name unique
        import time

        timestamp = int(time.time())
        folder_payload["name"] = f"{folder_payload['name']} - {timestamp}"

        folder = await self.client.create_folder(folder_payload)
        folder_dict = (
            folder.model_dump() if hasattr(folder, "model_dump") else dict(folder)
        )
        self.created_resources.append(
            {
                "type": "folder",
                "id": folder_dict["id"],
                "delete_func": lambda: self.client.delete_folder(folder_dict["id"]),
            }
        )
        return folder_dict

    async def _create_test_canvas(self, folder_id: str) -> Dict[str, Any]:
        """Create a test canvas."""
        canvas_payload = self.config.get_test_data("test_canvas")
        canvas_payload["folder_id"] = folder_id
        canvas = await self.client.create_canvas(canvas_payload)
        canvas_dict = (
            canvas.model_dump() if hasattr(canvas, "model_dump") else dict(canvas)
        )
        self.created_resources.append(
            {
                "type": "canvas",
                "id": canvas_dict["id"],
                "delete_func": lambda: self.client.delete_canvas(canvas_dict["id"]),
            }
        )
        return canvas_dict

    async def _create_test_group(self) -> Dict[str, Any]:
        """Create a test group."""
        group_payload = self.config.get_test_data("test_group").copy()
        # Add timestamp to make name unique
        import time

        timestamp = int(time.time())
        group_payload["name"] = f"{group_payload['name']} - {timestamp}"

        group = await self.client.create_group(group_payload)
        group_dict = group if isinstance(group, dict) else dict(group)
        self.created_resources.append(
            {
                "type": "group",
                "id": group_dict["id"],
                "delete_func": lambda: self.client.delete_group(group_dict["id"]),
            }
        )
        return group_dict

    async def _create_test_user(self) -> Dict[str, Any]:
        """Create a test user."""
        user_payload = self.config.get_test_data("test_user").copy()
        # Add timestamp to make email unique
        import time

        timestamp = int(time.time())
        base_email = user_payload["email"].split("@")[0]
        domain = user_payload["email"].split("@")[1]
        user_payload["email"] = f"{base_email}_{timestamp}@{domain}"

        user = await self.client.create_user(user_payload)
        user_dict = user.model_dump() if hasattr(user, "model_dump") else dict(user)
        self.created_resources.append(
            {
                "type": "user",
                "id": user_dict["id"],
                "delete_func": lambda: self.client.delete_user(user_dict["id"]),
            }
        )
        return user_dict

    async def _delete_resource(self, resource: Dict[str, Any]) -> None:
        """Delete a resource."""
        await resource["delete_func"]()


class TestClient:
    """Enhanced test client with authentication and utilities."""

    def __init__(self, config: TestConfig):
        self.config = config
        # Create client with SSL verification setting
        self.client = CanvusClient(
            config.server_url, config.api_key, verify_ssl=config.verify_ssl
        )
        self.data_manager = TestDataManager(self.client, config)
        self._authenticated = False

    async def __aenter__(self):
        """Async context manager entry."""
        await self.authenticate()
        await self.data_manager.setup_test_environment()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.data_manager.cleanup_test_environment()
        # Note: CanvusClient doesn't have a close method, so we skip it

    async def authenticate(self, use_admin: bool = True) -> None:
        """Authenticate with the server."""
        if self._authenticated:
            return

        credentials = (
            self.config.admin_credentials if use_admin else self.config.user_credentials
        )

        try:
            # Try to login with credentials
            login_response = await self.client.login(
                email=credentials["email"], password=credentials["password"]
            )

            if "token" in login_response:
                # Update the client with the new token
                self.client.api_key = login_response["token"]
                credentials["token"] = login_response["token"]

            self._authenticated = True
            print(f"Authenticated as: {credentials['email']}")

        except Exception as e:
            print(f"Authentication failed: {e}")
            print("Continuing with API key authentication...")
            self._authenticated = True

    def get_test_canvas_id(self) -> str:
        """Get the test canvas ID."""
        canvas_id = self.config.get_test_data_id("test_canvas")
        if not canvas_id:
            raise ValueError(
                "Test canvas not found. Run setup_test_environment() first."
            )
        return canvas_id

    def get_test_folder_id(self) -> str:
        """Get the test folder ID."""
        folder_id = self.config.get_test_data_id("test_folder")
        if not folder_id:
            raise ValueError(
                "Test folder not found. Run setup_test_environment() first."
            )
        return folder_id

    def get_test_group_id(self) -> str:
        """Get the test group ID."""
        group_id = self.config.get_test_data_id("test_group")
        if not group_id:
            raise ValueError(
                "Test group not found. Run setup_test_environment() first."
            )
        return group_id

    def get_test_user_id(self) -> str:
        """Get the test user ID."""
        user_id = self.config.get_test_data_id("test_user")
        if not user_id:
            raise ValueError("Test user not found. Run setup_test_environment() first.")
        return user_id


# Global test configuration instance
test_config = TestConfig()


def get_test_config() -> TestConfig:
    """Get the global test configuration."""
    return test_config


async def create_test_client(use_admin: bool = True) -> TestClient:
    """Create a test client with authentication."""
    client = TestClient(test_config)
    await client.authenticate(use_admin)
    return client
