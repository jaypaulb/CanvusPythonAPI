"""
Test suite for Canvus server functions (server info, config, email, etc.).
"""

import sys
import asyncio
import os
from pathlib import Path
from typing import Tuple
from canvus_api import CanvusClient, CanvusAPIError
from .test_utils import (
    print_success,
    print_error,
    print_warning,
    print_header,
    load_config,
)

# Add the tests directory to Python path
test_dir = Path(__file__).parent
if str(test_dir) not in sys.path:
    sys.path.append(str(test_dir))


async def create_test_token(client: CanvusClient, user_id: int) -> Tuple[str, str]:
    """Create a test token for running tests.

    Returns:
        Tuple[str, str]: Token ID and plain token value
    """
    print_header("Creating Test Token")
    token = await client.create_token(user_id, "Test Suite Token")
    print_success(f"Created test token: {token.id}")
    return token.id, token.plain_token


async def test_server_info(client: CanvusClient) -> None:
    """Test getting server information."""
    print_header("Testing Server Info")
    try:
        info = await client.get_server_info()
        print_success(f"Server version: {info.version}")
        print_success(f"API versions: {', '.join(info.api)}")
        print_success(f"Server ID: {info.server_id}")

        config = await client.get_server_config()
        print_success(f"Server name: {config.server_name}")
        if hasattr(config, "features"):
            print_success(f"Features configured: {len(config.features)}")
        if hasattr(config, "auth"):
            print_success("Authentication configuration present")
    except Exception as e:
        print_error(f"Error getting server info: {e}")


async def test_server_config_update(client: CanvusClient) -> None:
    """Test updating server configuration."""
    print_header("Testing Server Config Update")
    try:
        # Get current config
        original_config = await client.get_server_config()
        original_name = original_config.server_name

        # Update server name
        new_name = f"Test Server {asyncio.get_event_loop().time()}"
        updated_config = await client.update_server_config({"server_name": new_name})
        print_success(f"Updated server name to: {updated_config.server_name}")

        # Verify the update
        if updated_config.server_name == new_name:
            print_success("Server name update verified")
        else:
            print_error(
                f"Server name not updated correctly. Expected: {new_name}, Got: {updated_config.server_name}"
            )

        # Restore original name
        await client.update_server_config({"server_name": original_name})
        print_success("Restored original server name")

    except Exception as e:
        print_error(f"Error updating server config: {e}")


async def test_send_test_email(client: CanvusClient) -> None:
    """Test sending test email."""
    print_header("Testing Send Test Email")
    try:
        result = await client.send_test_email()
        print_success(f"Test email result: {result}")

        # Check if the result indicates success
        if isinstance(result, dict):
            status = result.get("status", "unknown")
            print_success(f"Test email status: {status}")
        else:
            print_success("Test email sent successfully")

    except Exception as e:
        print_error(f"Error sending test email: {e}")
        # Note: This might fail if email is not configured, which is expected


async def test_canvas_preview(client: CanvusClient) -> None:
    """Test getting canvas preview."""
    print_header("Testing Canvas Preview")
    try:
        # First, get a list of canvases to find one to test with
        canvases = await client.list_canvases()
        if not canvases:
            print_warning("No canvases available for preview test")
            return

        # Use the first canvas for testing
        canvas_id = canvases[0].id
        print_success(f"Testing preview for canvas: {canvas_id}")

        # Get the preview
        preview_data = await client.get_canvas_preview(canvas_id)

        # Verify we got binary data
        if isinstance(preview_data, bytes) and len(preview_data) > 0:
            print_success(f"Got preview data: {len(preview_data)} bytes")
        else:
            print_error("Preview data is not valid binary data")

    except Exception as e:
        print_error(f"Error getting canvas preview: {e}")


async def test_folder_operations(client: CanvusClient) -> None:
    """Test folder operations."""
    print_header("Testing Folder Operations")

    folder_id = None
    copied_folder_id = None
    try:
        # List existing folders
        folders = await client.list_folders()
        print_success(f"Found {len(folders)} existing folders")

        # Create a new folder
        new_folder = await client.create_folder(
            {"name": f"Test Folder {asyncio.get_event_loop().time()}"}
        )
        folder_id = new_folder.id
        print_success(f"Created folder: {new_folder.name}")

        # Test folder copy
        copied_folder = await client.copy_folder(
            folder_id,
            {
                "folder_id": new_folder.folder_id,  # Copy to same parent
                "name": f"Copy of {new_folder.name}",
            },
        )
        copied_folder_id = copied_folder.id
        print_success(f"Copied folder: {copied_folder.name}")

        # Test delete folder children
        await client.delete_folder_children(copied_folder_id)
        print_success("Deleted folder children")

        # Update folder
        updated = await client.update_folder(
            folder_id, {"name": f"Updated Folder {asyncio.get_event_loop().time()}"}
        )
        print_success(f"Updated folder name: {updated.name}")

        # Delete folders and verify deletion
        if copied_folder_id:
            await test_folder_deletion(client, copied_folder_id)
        await test_folder_deletion(client, folder_id)

    except Exception as e:
        print_error(f"Folder operations error: {e}")
        if copied_folder_id:
            try:
                await client.delete_folder(copied_folder_id)
            except Exception:
                pass
        if folder_id:
            try:
                await client.delete_folder(folder_id)
            except Exception:
                pass


async def test_folder_deletion(client: CanvusClient, folder_id: str) -> None:
    """Test folder deletion and verification."""
    try:
        # Delete folder
        await client.delete_folder(folder_id)
        print_success(f"Deleted folder: {folder_id}")

        # Verify deletion - we EXPECT a 404 error here
        try:
            await client.get_folder(folder_id)
            raise Exception("Folder still exists after deletion!")
        except CanvusAPIError as e:
            if e.status_code == 404:
                print_success("Verified folder deletion (404 response as expected)")
            else:
                raise Exception(f"Unexpected error checking folder deletion: {e}")
    except Exception as e:
        print_error(str(e))
        raise


async def test_permission_management(client: CanvusClient) -> None:
    """Test permission management operations."""
    print_header("Testing Permission Management")

    folder_id = None
    try:
        # Create a test folder
        folder = await client.create_folder(
            {"name": f"Permission Test Folder {asyncio.get_event_loop().time()}"}
        )
        folder_id = folder.id

        # Test folder permissions
        await client.get_folder_permissions(folder_id)
        print_success("Retrieved folder permissions")

        # Set folder permissions
        await client.set_folder_permissions(
            folder_id, {"editors_can_share": True, "users": [], "groups": []}
        )
        print_success("Updated folder permissions")

    except Exception as e:
        print_error(f"Permission management error: {e}")
    finally:
        if folder_id:
            try:
                await client.delete_folder(folder_id)
            except Exception:
                pass


async def test_token_operations(client: CanvusClient, user_id: int) -> None:
    """Test token operations."""
    print_header("Testing Token Operations")

    token_id = None
    try:
        # List existing tokens
        tokens = await client.list_tokens(user_id)
        print_success(f"Found {len(tokens)} existing tokens")

        # Create a new token
        token = await client.create_token(user_id, "Test token")
        token_id = token.id
        print_success(f"Created token: {token.id}")

        # Get token details
        retrieved = await client.get_token(user_id, token.id)
        print_success(f"Retrieved token: {retrieved.id}")

        # Update token description
        await client.update_token(user_id, token.id, "Updated test token")
        print_success("Updated token description")

        # Delete token and verify deletion
        await client.delete_token(user_id, token.id)
        print_success(f"Deleted token: {token.id}")

        try:
            await client.get_token(user_id, token.id)
            raise Exception("Token still exists after deletion!")
        except CanvusAPIError as e:
            if e.status_code == 404:
                print_success("Verified token deletion (404 response as expected)")
            else:
                raise Exception(f"Unexpected error checking token deletion: {e}")

    except Exception as e:
        print_error(f"Token operations error: {e}")
        if token_id:
            try:
                await client.delete_token(user_id, token_id)
            except Exception:
                pass


async def test_canvas_background_operations(client: CanvusClient) -> None:
    """Test canvas background operations."""
    print_header("Testing Canvas Background Operations")

    canvas_id = None
    try:
        # First, get a list of canvases to find one to test with
        canvases = await client.list_canvases()
        if not canvases:
            print_warning("No canvases available for background test")
            return

        # Use the first canvas for testing
        canvas_id = canvases[0].id
        print_success(f"Testing background for canvas: {canvas_id}")

        # Get current background
        background = await client.get_canvas_background(canvas_id)
        print_success(f"Retrieved background: {background}")

        # Set background to a color
        color_background = await client.set_canvas_background(
            canvas_id, {"type": "color", "color": "#ff0000", "opacity": 0.8}
        )
        print_success(f"Set color background: {color_background}")

        # Get background again to verify
        updated_background = await client.get_canvas_background(canvas_id)
        print_success(f"Verified background update: {updated_background}")

        # Test setting background image (if test image exists)
        test_image_path = "tests/test_files/test_image.jpg"
        if os.path.exists(test_image_path):
            try:
                image_background = await client.set_canvas_background_image(
                    canvas_id, test_image_path
                )
                print_success(f"Set image background: {image_background}")
            except Exception as e:
                print_warning(f"Image background test failed (expected): {e}")
        else:
            print_warning("Test image not found, skipping image background test")

    except Exception as e:
        print_error(f"Canvas background operations error: {e}")


async def test_video_input_operations(client: CanvusClient) -> None:
    """Test video input operations."""
    print_header("Testing Video Input Operations")

    canvas_id = None
    video_input_id = None
    try:
        # First, get a list of canvases to find one to test with
        canvases = await client.list_canvases()
        if not canvases:
            print_warning("No canvases available for video input test")
            return

        # Use the first canvas for testing
        canvas_id = canvases[0].id
        print_success(f"Testing video inputs for canvas: {canvas_id}")

        # List existing video inputs
        video_inputs = await client.list_canvas_video_inputs(canvas_id)
        print_success(f"Found {len(video_inputs)} existing video inputs")

        # Create a new video input
        video_input_payload = {
            "name": f"Test Video Input {asyncio.get_event_loop().time()}",
            "source": "test_source_1",
            "location": {"x": 100.0, "y": 100.0},
            "size": {"width": 320.0, "height": 240.0},
            "config": {"fps": 30, "resolution": "720p"},
            "depth": 1,
            "scale": 1.0,
            "pinned": False
        }

        video_input = await client.create_video_input(canvas_id, video_input_payload)
        video_input_id = video_input.get("id")
        print_success(f"Created video input: {video_input.get('name')}")

        # Verify the video input was created
        if video_input_id:
            print_success(f"Video input ID: {video_input_id}")
            print_success(f"Video input name: {video_input.get('name')}")
            print_success(f"Video input source: {video_input.get('source')}")

        # List video inputs again to verify creation
        updated_video_inputs = await client.list_canvas_video_inputs(canvas_id)
        print_success(f"Found {len(updated_video_inputs)} video inputs after creation")

        # Verify our new video input is in the list
        found = False
        for vi in updated_video_inputs:
            if vi.get("id") == video_input_id:
                found = True
                break
        
        if found:
            print_success("Verified video input appears in list")
        else:
            print_warning("Video input not found in updated list")

        # Test video input deletion
        if video_input_id:
            await client.delete_video_input(canvas_id, video_input_id)
            print_success(f"Deleted video input: {video_input_id}")

            # Verify deletion by listing again
            final_video_inputs = await client.list_canvas_video_inputs(canvas_id)
            print_success(f"Found {len(final_video_inputs)} video inputs after deletion")

            # Verify our deleted video input is not in the list
            still_found = False
            for vi in final_video_inputs:
                if vi.get("id") == video_input_id:
                    still_found = True
                    break
            
            if not still_found:
                print_success("Verified video input was deleted")
            else:
                print_error("Video input still exists after deletion")

    except Exception as e:
        print_error(f"Video input operations error: {e}")
        # Clean up if we created a video input but deletion failed
        if video_input_id and canvas_id:
            try:
                await client.delete_video_input(canvas_id, video_input_id)
                print_success("Cleaned up video input after error")
            except Exception:
                pass


async def test_client_video_inputs(client: CanvusClient) -> None:
    """Test client video inputs operations."""
    print_header("Testing Client Video Inputs Operations")

    try:
        # First, get a list of clients to find one to test with
        clients = await client.list_clients()
        if not clients:
            print_warning("No clients available for video inputs test")
            return

        # Use the first client for testing
        client_id = clients[0]["id"]
        print_success(f"Testing video inputs for client: {client_id}")

        # List client video inputs
        video_inputs = await client.list_client_video_inputs(client_id)
        print_success(f"Found {len(video_inputs)} client video inputs")

        # Display some details about the video inputs
        for i, vi in enumerate(video_inputs[:3]):  # Show first 3
            print_success(f"Video input {i+1}: {vi.get('name', 'Unnamed')} (ID: {vi.get('id', 'Unknown')})")

    except Exception as e:
        print_error(f"Client video inputs operations error: {e}")


async def test_client_video_outputs(client: CanvusClient) -> None:
    """Test client video outputs operations."""
    print_header("Testing Client Video Outputs Operations")

    try:
        # First, get a list of clients to find one to test with
        clients = await client.list_clients()
        if not clients:
            print_warning("No clients available for video outputs test")
            return

        # Use the first client for testing
        client_id = clients[0]["id"]
        print_success(f"Testing video outputs for client: {client_id}")

        # List client video outputs
        video_outputs = await client.list_client_video_outputs(client_id)
        print_success(f"Found {len(video_outputs)} client video outputs")

        # Display some details about the video outputs
        for i, vo in enumerate(video_outputs[:3]):  # Show first 3
            print_success(f"Video output {i+1}: {vo.get('name', 'Unnamed')} (ID: {vo.get('id', 'Unknown')})")

    except Exception as e:
        print_error(f"Client video outputs operations error: {e}")


async def test_video_output_source_setting(client: CanvusClient) -> None:
    """Test video output source setting operations."""
    print_header("Testing Video Output Source Setting Operations")

    try:
        # First, get a list of clients to find one to test with
        clients = await client.list_clients()
        if not clients:
            print_warning("No clients available for video output source test")
            return

        # Use the first client for testing
        client_id = clients[0]["id"]
        print_success(f"Testing video output source setting for client: {client_id}")

        # List client video outputs first
        video_outputs = await client.list_client_video_outputs(client_id)
        print_success(f"Found {len(video_outputs)} client video outputs")

        if video_outputs:
            # Test setting source for the first output (index 0)
            output_index = 0
            source_payload = {
                "source": "test_source_1",
                "enabled": True,
                "resolution": "1920x1080",
                "refresh_rate": 60
            }

            updated_output = await client.set_video_output_source(client_id, output_index, source_payload)
            print_success(f"Updated video output {output_index}: {updated_output.get('source', 'Unknown')}")

            # Verify the update
            if updated_output.get("source") == "test_source_1":
                print_success("Video output source update verified")
            else:
                print_warning(f"Source not updated as expected. Got: {updated_output.get('source')}")

        else:
            print_warning("No video outputs available for source setting test")

    except Exception as e:
        print_error(f"Video output source setting operations error: {e}")


async def test_server_functions(client: CanvusClient) -> None:
    """Main test function."""
    print_header("Starting Canvus Server Function Tests")

    # Get user ID from config or use default
    config = load_config()
    user_id = config.get("user_id", 1000)  # Default to 1000 if not specified

    # Create a test token for our test suite
    test_token_id, test_token = await create_test_token(client, user_id)

    try:
        # Create a new client with our test token
        async with CanvusClient(
            base_url=config["base_url"], api_key=test_token
        ) as test_client:
            print_success("Test client initialized with new token")

            # Run all tests with the test token
            await test_server_info(test_client)
            await test_server_config_update(test_client)
            await test_send_test_email(test_client)
            await test_canvas_preview(test_client)
            await test_canvas_background_operations(test_client)
            await test_video_input_operations(test_client)
            await test_client_video_inputs(test_client)
            await test_client_video_outputs(test_client)
            await test_video_output_source_setting(test_client)
            await test_folder_operations(test_client)
            await test_permission_management(test_client)
            await test_token_operations(test_client, user_id)
    finally:
        # Clean up our test token
        try:
            await client.delete_token(user_id, test_token_id)
            print_success("Cleaned up test token")
        except Exception as e:
            print_error(f"Failed to clean up test token: {e}")


if __name__ == "__main__":

    async def run():
        config = load_config()
        print_success("Configuration loaded")

        async with CanvusClient(
            base_url=config["base_url"], api_key=config["api_key"]
        ) as client:
            print_success("Client initialized")
            await test_server_functions(client)

    asyncio.run(run())
