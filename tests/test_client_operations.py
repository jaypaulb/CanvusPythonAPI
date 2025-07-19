"""
Test suite for Canvus client discovery and workspace operations.
"""

import sys
import asyncio
from pathlib import Path
import time
from typing import Dict, Any
from canvus_api import CanvusClient
from .test_utils import (
    print_success,
    print_error,
    print_info,
    print_warning,
    print_header,
    load_config,
)
import pytest

# Add the tests directory to Python path
test_dir = Path(__file__).parent
if str(test_dir) not in sys.path:
    sys.path.append(str(test_dir))


async def wait_for_workspace_canvas(
    client: CanvusClient,
    client_id: str,
    workspace_index: int,
    expected_canvas_id: str,
    max_retries: int = 30,
) -> bool:
    """Wait for workspace to open the expected canvas.

    Args:
        client: The CanvusClient instance
        client_id: ID of the client
        workspace_index: Index of the workspace
        expected_canvas_id: The canvas ID we expect to be opened
        max_retries: Maximum number of retries (default: 30)

    Returns:
        bool: True if canvas was opened, False if timed out
    """
    for i in range(max_retries):
        # Check current workspace state
        workspace = await client.get_workspace(client_id, workspace_index)
        print_info(
            f"Current workspace state: canvas_id={workspace.canvas_id}, server_id={workspace.server_id}"
        )

        if workspace.canvas_id == expected_canvas_id:
            return True

        # If canvas hasn't opened, try opening it again
        print_info(f"Canvas not opened yet, retry {i+1}/{max_retries}...")
        try:
            # Send open request again
            open_payload = {
                "canvas_id": expected_canvas_id,
                "server_id": workspace.server_id,
            }
            await client._request(
                "POST",
                f"clients/{client_id}/workspaces/{workspace_index}/open-canvas",
                json_data=open_payload,
            )
            print_info("Re-sent open canvas request")
        except Exception as e:
            print_error(f"Error re-sending open request: {e}")

        await asyncio.sleep(1)  # Wait 1 second between checks

    return False


@pytest.mark.asyncio
async def test_client_discovery(client: CanvusClient) -> str:
    """Test client listing and admin discovery.

    Returns:
        str: The admin client ID if found
    """
    print_header("Testing Client Discovery")

    try:
        # List all clients
        clients = await client.list_clients()
        print_success(f"Found {len(clients)} connected clients")

        # Check each client for admin user
        for client_info in clients:
            try:
                client_id = client_info["id"]  # type: ignore[index]
                workspaces = await client.get_client_workspaces(client_id)
                for workspace in workspaces:
                    if workspace.user == "admin@local.local":
                        print_success(f"Found admin client: {client_id}")
                        return client_id
            except Exception:
                continue

        print_error("No admin client found")
        return ""

    except Exception as e:
        print_error(f"Client discovery error: {e}")
        return ""


@pytest.mark.asyncio
async def test_workspace_operations(client: CanvusClient) -> None:
    """Test workspace operations."""
    print_header("Testing Workspace Operations")

    try:
        # Get client ID from the client discovery test
        client_id = await test_client_discovery(client)

        # 1. List workspaces and get initial state
        workspaces = await client.get_client_workspaces(client_id)
        print_success(f"Listed {len(workspaces)} workspaces")

        if not workspaces:
            print_error("No workspaces found to test with")
            return

        # Get first workspace and save its state
        workspace = workspaces[0]
        original_canvas_id = workspace.canvas_id
        print_info(
            f"Testing with workspace {workspace.index}: {workspace.workspace_name}"
        )
        print_info(f"Original canvas: {original_canvas_id}")

        # Clean up any existing test canvases first
        canvases = await client.list_canvases()
        for canvas in canvases:
            if canvas.name.startswith("Workspace Test Canvas"):
                try:
                    await client.delete_canvas(canvas.id)
                    print_info(f"Cleaned up existing test canvas: {canvas.id}")
                except Exception as e:
                    print_warning(
                        f"Failed to clean up existing test canvas {canvas.id}: {e}"
                    )

        # 2. Create a test canvas with unique name
        test_canvas_name = f"Workspace Test Canvas {time.time()}"
        test_canvas = await client.create_canvas(
            {"name": test_canvas_name, "width": 1920, "height": 1080}
        )
        print_success(f"Created test canvas: {test_canvas.id}")

        # Verify test canvas exists
        canvas_check = await client.get_canvas(test_canvas.id)
        if not canvas_check:
            print_error("Failed to verify test canvas exists")
            return
        print_success("Verified test canvas exists")

        try:
            # 3. Open test canvas in workspace
            open_payload = {
                "canvas_id": test_canvas.id,
                "server_id": workspace.server_id,
            }
            print_info(
                f'Opening canvas with payload: {{"canvas_id": "{test_canvas.id}", "server_id": "{workspace.server_id}"}}'
            )
            await client._request(
                "POST",
                f"clients/{client_id}/workspaces/{workspace.index}/open-canvas",
                json_data=open_payload,
            )
            print_info("Requested to open test canvas")

            # Wait for canvas to open
            if not await wait_for_workspace_canvas(
                client, client_id, workspace.index, test_canvas.id
            ):
                print_error("Timed out waiting for test canvas to open")
                return
            print_success("Test canvas opened successfully")

            # 4. Save original workspace settings
            original_settings: Dict[str, Any] = {
                "pinned": workspace.pinned,
                "info_panel_visible": workspace.info_panel_visible,
                "view_rectangle": {
                    "x": workspace.view_rectangle.x,
                    "y": workspace.view_rectangle.y,
                    "width": workspace.view_rectangle.width,
                    "height": workspace.view_rectangle.height,
                },
            }
            print_info(
                f"Original settings: pinned={original_settings['pinned']}, info_panel_visible={original_settings['info_panel_visible']}"
            )
            print_info(
                f"Original view rectangle: x={original_settings['view_rectangle']['x']} y={original_settings['view_rectangle']['y']} width={original_settings['view_rectangle']['width']} height={original_settings['view_rectangle']['height']}"
            )

            # 5. Test workspace settings changes
            # Update settings to opposite values
            settings_update = {
                "pinned": not workspace.pinned,
                "info_panel_visible": not workspace.info_panel_visible,
            }
            updated = await client.update_workspace(
                client_id, workspace.index, settings_update
            )

            # Verify settings changed
            if updated.pinned == workspace.pinned:
                print_error("Workspace pinned state did not change")
                return
            if updated.info_panel_visible == workspace.info_panel_visible:
                print_error("Workspace info panel visibility did not change")
                return
            print_success("Updated workspace settings")

            # 6. Test view rectangle update
            view_update = {
                "view_rectangle": {"x": 0.0, "y": 0.0, "width": 1000.0, "height": 800.0}
            }
            updated = await client.update_workspace(
                client_id, workspace.index, view_update
            )

            # Verify view rectangle changed
            if (
                updated.view_rectangle.x == original_settings["view_rectangle"]["x"]
                and updated.view_rectangle.y == original_settings["view_rectangle"]["y"]
                and updated.view_rectangle.width
                == original_settings["view_rectangle"]["width"]
                and updated.view_rectangle.height
                == original_settings["view_rectangle"]["height"]
            ):
                print_error("View rectangle did not change")
                return
            print_success("Updated workspace view rectangle")

            # 7. Restore original settings
            restored = await client.update_workspace(
                client_id,
                workspace.index,
                {
                    "pinned": original_settings["pinned"],
                    "info_panel_visible": original_settings["info_panel_visible"],
                    "view_rectangle": original_settings["view_rectangle"],
                },
            )

            # Verify settings restored
            if restored.pinned != original_settings["pinned"]:
                print_error("Failed to restore pinned state")
                return
            if restored.info_panel_visible != original_settings["info_panel_visible"]:
                print_error("Failed to restore info panel visibility")
                return
            if (
                restored.view_rectangle.x != original_settings["view_rectangle"]["x"]
                or restored.view_rectangle.y != original_settings["view_rectangle"]["y"]
                or restored.view_rectangle.width
                != original_settings["view_rectangle"]["width"]
                or restored.view_rectangle.height
                != original_settings["view_rectangle"]["height"]
            ):
                print_error("Failed to restore view rectangle")
                return
            print_success("Restored original workspace settings")

            # 8. Restore original canvas
            restore_payload = {
                "canvas_id": original_canvas_id,
                "server_id": workspace.server_id,
            }
            print_info(
                f'Restoring canvas with payload: {{"canvas_id": "{original_canvas_id}", "server_id": "{workspace.server_id}"}}'
            )
            await client._request(
                "POST",
                f"clients/{client_id}/workspaces/{workspace.index}/open-canvas",
                json_data=restore_payload,
            )
            print_info("Requested to restore original canvas")

            # Wait for original canvas to restore
            if not await wait_for_workspace_canvas(
                client, client_id, workspace.index, original_canvas_id
            ):
                print_error("Timed out waiting for original canvas to restore")
                return
            print_success("Original canvas restored successfully")

            # 9. Only after everything is verified and restored, clean up test canvas
            await client.delete_canvas(test_canvas.id)
            print_success("Cleaned up test canvas")

        except Exception as e:
            print_error(f"Workspace operations error: {e}")
            raise

    except Exception as e:
        print_error(f"Workspace operations error: {e}")
        raise


async def main():
    """Main test function."""
    print_header("Starting Client Operations Tests")

    config = load_config()
    print_success("Configuration loaded")

    async with CanvusClient(
        base_url=config["base_url"], api_key=config["api_key"]
    ) as client:
        print_success("Client initialized")

        # Test client discovery
        admin_client_id = await test_client_discovery(client)
        if not admin_client_id:
            print_error("Cannot proceed without admin client")
            return

        # Test workspace operations
        await test_workspace_operations(client)


if __name__ == "__main__":
    asyncio.run(main())
