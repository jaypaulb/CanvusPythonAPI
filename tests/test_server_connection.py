"""
Test server connection and basic operations.
"""

import pytest
from tests.test_config import TestClient, get_test_config


@pytest.mark.asyncio
async def test_server_connection():
    """Test basic server connection and authentication."""
    print("Testing server connection...")

    config = get_test_config()
    print(f"Server URL: {config.server_url}")
    print(f"API Key: {config.api_key[:10]}...")

    try:
        async with TestClient(config) as test_client:
            client = test_client.client

            # Test 1: Get server info
            print("Testing server info...")
            server_info = await client.get_server_info()
            print(f"✅ Server info retrieved: {server_info}")

            # Test 2: Get server config
            print("Testing server config...")
            server_config = await client.get_server_config()
            print(f"✅ Server config retrieved: {server_config}")

            # Test 3: List clients
            print("Testing client listing...")
            clients = await client.list_clients()
            print(f"✅ Found {len(clients)} clients")

            # Test 4: List canvases
            print("Testing canvas listing...")
            canvases = await client.list_canvases()
            print(f"✅ Found {len(canvases)} canvases")

            # Test 5: List folders
            print("Testing folder listing...")
            folders = await client.list_folders()
            print(f"✅ Found {len(folders)} folders")

            # Test 6: List groups
            print("Testing group listing...")
            groups = await client.list_groups()
            print(f"✅ Found {len(groups)} groups")

            # Test 7: List users
            print("Testing user listing...")
            users = await client.list_users()
            print(f"✅ Found {len(users)} users")

            print("🎉 All basic connection tests passed!")
            return True

    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False


@pytest.mark.asyncio
async def test_authentication():
    """Test authentication with provided credentials."""
    print("\nTesting authentication...")

    config = get_test_config()

    try:
        # Test admin authentication
        print("Testing admin authentication...")
        async with TestClient(config) as test_client:
            client = test_client.client

            # Try to get current user
            current_user = await client.get_current_user()
            print(f"✅ Admin authentication successful: {current_user.email}")

        # Test regular user authentication
        print("Testing regular user authentication...")
        config_copy = get_test_config()
        test_client = TestClient(config_copy)
        await test_client.authenticate(use_admin=False)

        client = test_client.client
        current_user = await client.get_current_user()
        print(f"✅ Regular user authentication successful: {current_user.email}")

        print("🎉 All authentication tests passed!")
        return True

    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False


@pytest.mark.asyncio
async def test_file_operations():
    """Test basic file operations."""
    print("\nTesting file operations...")

    config = get_test_config()

    try:
        async with TestClient(config) as test_client:
            client = test_client.client

            # Get test canvas ID
            canvas_id = test_client.get_test_canvas_id()
            print(f"Using test canvas: {canvas_id}")

            # Test file upload - use async context manager for client
            image_path = config.test_files["image"]
            print(f"Testing image upload: {image_path}")

            async with client:
                image = await client.create_image(
                    canvas_id, image_path, {"title": "Connection Test Image"}
                )
                print(f"✅ Image uploaded successfully: {image.id}")

                # Test file download
                image_data = await client.download_image(canvas_id, image.id)
                print(f"✅ Image downloaded successfully: {len(image_data)} bytes")

                # Test file deletion
                await client.delete_image(canvas_id, image.id)
                print("✅ Image deleted successfully")

            print("🎉 All file operation tests passed!")
            return True

    except Exception as e:
        print(f"❌ File operation test failed: {e}")
        return False


@pytest.mark.asyncio
async def main():
    """Run all connection tests."""
    print("🔍 Testing Canvus Server Connection")
    print("=" * 50)

    # Test 1: Basic connection
    connection_ok = await test_server_connection()

    # Test 2: Authentication
    auth_ok = await test_authentication()

    # Test 3: File operations
    file_ok = await test_file_operations()

    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"Connection: {'✅ PASS' if connection_ok else '❌ FAIL'}")
    print(f"Authentication: {'✅ PASS' if auth_ok else '❌ FAIL'}")
    print(f"File Operations: {'✅ PASS' if file_ok else '❌ FAIL'}")

    if connection_ok and auth_ok and file_ok:
        print("\n🎉 All tests passed! Your server configuration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check your configuration.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
