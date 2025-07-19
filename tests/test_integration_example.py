"""
Example integration test showing how to use the test configuration.
This demonstrates the layered approach: create content, test, cleanup.
"""

import pytest
from tests.test_config import TestClient, get_test_config


@pytest.mark.asyncio
async def test_canvas_operations_integration():
    """Example integration test for canvas operations."""

    # Use the test client as a context manager for automatic setup/cleanup
    async with TestClient(get_test_config()) as test_client:
        client = test_client.client

        # Get the test canvas ID that was created during setup
        canvas_id = test_client.get_test_canvas_id()

        # Test 1: Get canvas details
        canvas = await client.get_canvas(canvas_id)
        assert canvas is not None
        # Guest canvas name is "1st", so just check it's not empty
        assert canvas.name and len(canvas.name) > 0

        # Test 2: Update canvas
        update_payload = {
            "name": "Updated Test Canvas",
            "description": "Canvas updated by integration test",
        }
        updated_canvas = await client.update_canvas(canvas_id, update_payload)
        assert updated_canvas.name == "Updated Test Canvas"

        # Test 3: Upload a file to the canvas
        image_path = get_test_config().test_files["image"]
        image = await client.create_image(
            canvas_id,
            image_path,
            {"title": "Test Image", "position": {"x": 100, "y": 100}},
        )
        assert image is not None
        assert image.title == "Test Image"

        # Test 4: List images in canvas
        images = await client.list_images(canvas_id)
        assert len(images) >= 1

        # Test 5: Download the image
        image_data = await client.download_image(canvas_id, image.id)
        assert len(image_data) > 0

        # Test 6: Delete the image
        await client.delete_image(canvas_id, image.id)

        # Verify image was deleted
        images_after_delete = await client.list_images(canvas_id)
        assert len(images_after_delete) == len(images) - 1


@pytest.mark.asyncio
async def test_folder_operations_integration():
    """Example integration test for folder operations."""

    async with TestClient(get_test_config()) as test_client:
        client = test_client.client

        # Get the test folder ID
        folder_id = test_client.get_test_folder_id()

        # Test 1: Get folder details
        folder = await client.get_folder(folder_id)
        assert folder is not None
        # Don't assert exact name since folder names include timestamps
        assert "Folder" in folder.name or "folder" in folder.name.lower()

        # Test 2: Create a new canvas in the folder
        new_canvas_payload = {
            "name": "Integration Test Canvas",
            "description": "Canvas created during integration test",
            "folder_id": folder_id,
        }
        new_canvas = await client.create_canvas(new_canvas_payload)
        assert new_canvas is not None
        assert new_canvas.name == "Integration Test Canvas"

        # Test 3: List canvases in folder
        canvases = await client.list_canvases({"folder_id": folder_id})
        assert len(canvases) >= 2  # Original test canvas + new canvas

        # Test 4: Delete the new canvas
        await client.delete_canvas(new_canvas.id)

        # Verify canvas was deleted
        canvases_after_delete = await client.list_canvases({"folder_id": folder_id})
        assert len(canvases_after_delete) == len(canvases) - 1


@pytest.mark.asyncio
async def test_group_operations_integration():
    """Example integration test for group operations."""

    async with TestClient(get_test_config()) as test_client:
        client = test_client.client

        # Get the test group ID
        group_id = test_client.get_test_group_id()

        # Test 1: Get group details
        group = await client.get_group(group_id)
        assert group is not None
        # Don't assert exact name since group names include timestamps
        assert "Group" in group["name"] or "group" in group["name"].lower()

        # Test 2: List group members (should be empty initially)
        members = await client.list_group_members(group_id)
        assert len(members) == 0

        # Test 3: Add a user to the group
        # Note: This would require a test user ID
        # For now, we'll just test the method exists
        # user_id = test_client.get_test_user_id()
        # result = await client.add_user_to_group(group_id, user_id)
        # assert result is not None

        # Test 4: Remove user from group
        # await client.remove_user_from_group(group_id, user_id)


@pytest.mark.asyncio
async def test_file_upload_integration():
    """Example integration test for file upload operations."""

    async with TestClient(get_test_config()) as test_client:
        client = test_client.client
        canvas_id = test_client.get_test_canvas_id()

        # Track created widgets for cleanup
        created_widgets = []

        try:
            # Test 1: Upload image
            image_path = get_test_config().test_files["image"]
            image = await client.create_image(
                canvas_id, image_path, {"title": "Integration Test Image"}
            )
            assert image is not None
            created_widgets.append(("image", image.id))

            # Test 2: Upload video
            video_path = get_test_config().test_files["video"]
            video = await client.create_video(
                canvas_id, video_path, {"title": "Integration Test Video"}
            )
            assert video is not None
            created_widgets.append(("video", video.id))

            # Test 3: Upload PDF
            pdf_path = get_test_config().test_files["pdf"]
            pdf = await client.create_pdf(
                canvas_id, pdf_path, {"title": "Integration Test PDF"}
            )
            assert pdf is not None
            created_widgets.append(("pdf", pdf.id))

            # Test 4: List all widgets
            widgets = await client.list_widgets(canvas_id)
            assert len(widgets) >= 3  # At least our 3 uploaded files

            # Test 5: Download files
            image_data = await client.download_image(canvas_id, image.id)
            video_data = await client.download_video(canvas_id, video.id)
            pdf_data = await client.download_pdf(canvas_id, pdf.id)

            assert len(image_data) > 0
            assert len(video_data) > 0
            assert len(pdf_data) > 0

        finally:
            # Cleanup: Delete uploaded files (even if test fails)
            for widget_type, widget_id in created_widgets:
                try:
                    if widget_type == "image":
                        await client.delete_image(canvas_id, widget_id)
                    elif widget_type == "video":
                        await client.delete_video(canvas_id, widget_id)
                    elif widget_type == "pdf":
                        await client.delete_pdf(canvas_id, widget_id)
                except Exception as e:
                    print(f"Warning: Failed to delete {widget_type} {widget_id}: {e}")


@pytest.mark.asyncio
async def test_server_operations_integration():
    """Example integration test for server operations."""

    async with TestClient(get_test_config()) as test_client:
        client = test_client.client

        # Test 1: Get server info
        server_info = await client.get_server_info()
        assert server_info is not None

        # Test 2: Get server config
        server_config = await client.get_server_config()
        assert server_config is not None

        # Test 3: List clients
        clients = await client.list_clients()
        assert isinstance(clients, list)

        # Test 4: Get specific client (if any exist)
        if clients:
            client_id = clients[0]["id"]
            client_details = await client.get_client(client_id)
            assert client_details is not None


if __name__ == "__main__":
    # Example of running a single test
    import asyncio

    async def run_example():
        async with TestClient(get_test_config()) as test_client:
            print("Test environment setup complete!")
            print(f"Test canvas ID: {test_client.get_test_canvas_id()}")
            print(f"Test folder ID: {test_client.get_test_folder_id()}")
            print(f"Test group ID: {test_client.get_test_group_id()}")

    asyncio.run(run_example())
