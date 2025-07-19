#!/usr/bin/env python3
"""
Test Client Manager for Canvus API Integration Testing

This module provides utilities to detect and manage Canvus clients for integration testing.
Since we don't know the exact location or startup method for Canvus client software,
this module focuses on detecting existing clients and providing guidance for setup.
"""

import asyncio
from typing import Dict, Any, Optional, List

try:
    import psutil
except ImportError:
    psutil = None  # type: ignore

from canvus_api import CanvusClient
from tests.test_config import get_test_config


class TestClientManager:
    """Manages Canvus client detection and testing setup."""

    def __init__(self, config: Any):
        self.config = config
        self.client_id: Optional[str] = None
        self.client_info: Optional[Dict[str, Any]] = None
        self.is_available: bool = False

    async def detect_clients(self) -> List[Dict[str, Any]]:
        """Detect any Canvus clients currently connected to the server."""
        print("🔍 Detecting Canvus clients...")

        try:
            async with CanvusClient(
                base_url=self.config.server_url,
                api_key=self.config.api_key,
                verify_ssl=self.config.verify_ssl,
            ) as client:
                clients = await client.list_clients()

                if clients:
                    print(f"✅ Found {len(clients)} connected client(s):")
                    for i, client_info in enumerate(clients):
                        print(f"   {i+1}. ID: {client_info.get('id', 'Unknown')}")
                        print(
                            f"      Name: {client_info.get('installation_name', 'Unknown')}"
                        )
                        print(f"      Version: {client_info.get('version', 'Unknown')}")
                        print(f"      State: {client_info.get('state', 'Unknown')}")
                        print(f"      Access: {client_info.get('access', 'Unknown')}")
                        print()

                    self.is_available = True
                    if clients:
                        self.client_id = clients[0]["id"]
                        self.client_info = clients[0]
                else:
                    print("⚠️  No Canvus clients are currently connected")
                    print("ℹ️  To test client-related methods, you need:")
                    print("   1. Canvus client software installed and running")
                    print("   2. Client configured to connect to the test server")
                    print("   3. Client API access enabled")

                return clients

        except Exception as e:
            print(f"❌ Error detecting clients: {e}")
            return []

    async def check_client_requirements(self) -> Dict[str, bool]:
        """Check what's needed to run client tests."""
        requirements = {
            "server_accessible": False,
            "clients_connected": False,
            "api_enabled": False,
            "test_ready": False,
        }

        print("🔧 Checking client testing requirements...")

        # Check server accessibility
        try:
            async with CanvusClient(
                base_url=self.config.server_url,
                api_key=self.config.api_key,
                verify_ssl=self.config.verify_ssl,
            ) as client:
                await client.get_server_info()
                requirements["server_accessible"] = True
                print("✅ Server is accessible")
        except Exception as e:
            print(f"❌ Server not accessible: {e}")
            return requirements

        # Check for connected clients
        clients = await self.detect_clients()
        if clients:
            requirements["clients_connected"] = True
            print("✅ Clients are connected")

            # Check if API access is enabled (try a client API call)
            try:
                async with CanvusClient(
                    base_url=self.config.server_url,
                    api_key=self.config.api_key,
                    verify_ssl=self.config.verify_ssl,
                ) as client:
                    # Try to get video outputs from first client
                    client_id = clients[0]["id"]
                    try:
                        await client.list_client_video_outputs(client_id)
                        requirements["api_enabled"] = True
                        print("✅ Client API access is enabled")
                    except Exception as api_error:
                        if "offline" in str(api_error).lower():
                            print("⚠️  Client is offline or API access not enabled")
                        else:
                            print(f"⚠️  Client API test failed: {api_error}")
            except Exception as e:
                print(f"❌ Error testing client API access: {e}")
        else:
            print("❌ No clients connected")

        # Overall test readiness
        requirements["test_ready"] = (
            requirements["server_accessible"]
            and requirements["clients_connected"]
            and requirements["api_enabled"]
        )

        return requirements

    async def get_client_id(self) -> Optional[str]:
        """Get the client ID from the server."""
        if not self.client_id:
            clients = await self.detect_clients()
            if clients:
                self.client_id = clients[0]["id"]
                print(f"✅ Using client ID: {self.client_id}")

        return self.client_id

    def get_setup_instructions(self) -> str:
        """Get instructions for setting up a test client."""
        return """
🔧 SETUP INSTRUCTIONS FOR CANVUS CLIENT TESTING

To enable full integration testing of client-related methods, you need:

1. INSTALL CANVUS CLIENT SOFTWARE
   - Download Canvus client from the official source
   - Install according to your platform requirements
   - Verify the client can run independently

2. CONFIGURE CLIENT CONNECTION
   - Open Canvus client settings
   - Set server URL to: {server_url}
   - Configure authentication if required
   - Test connection to server

3. ENABLE API ACCESS
   - In client settings, find "API Access" or "Developer Mode"
   - Enable API access (may require admin privileges)
   - Restart client if necessary

4. VERIFY CONNECTION
   - Ensure client shows as "Connected" or "Online"
   - Check that client appears in server client list
   - Verify API endpoints respond correctly

5. RUN TESTS
   - Execute: python tests/test_validation_integration.py
   - Tests should now detect and use the connected client

CURRENT SERVER CONFIG:
- Server URL: {server_url}
- API Key: {api_key}
- SSL Verification: {verify_ssl}

For more information, see: tests/CLIENT_TESTING_GUIDE.md
""".format(
            server_url=self.config.server_url,
            api_key=(
                self.config.api_key[:10] + "..." if self.config.api_key else "Not set"
            ),
            verify_ssl=self.config.verify_ssl,
        )


async def setup_test_client() -> Optional[TestClientManager]:
    """Set up client testing environment."""
    config = get_test_config()
    manager = TestClientManager(config)

    print("🔧 Setting up Canvus client testing environment...")

    # Check requirements
    requirements = await manager.check_client_requirements()

    if requirements["test_ready"]:
        print("✅ Client testing environment is ready!")
        return manager
    else:
        print("⚠️  Client testing environment is not ready")
        print(manager.get_setup_instructions())
        return None


async def cleanup_test_client(manager: TestClientManager) -> None:
    """Clean up the test client environment."""
    if manager:
        print("🧹 Cleaning up client testing environment...")
        # No cleanup needed for detection-only approach
        print("✅ Cleanup complete")


# Example usage
async def main():
    """Example of how to use the test client manager."""
    manager = await setup_test_client()

    if manager:
        try:
            # Run your tests here
            print("🧪 Running tests with detected client...")
            client_id = await manager.get_client_id()
            print(f"Using client ID: {client_id}")
            await asyncio.sleep(5)  # Simulate test execution
        finally:
            await cleanup_test_client(manager)
    else:
        print("⚠️  Running tests without client (limited functionality)")


if __name__ == "__main__":
    asyncio.run(main())
