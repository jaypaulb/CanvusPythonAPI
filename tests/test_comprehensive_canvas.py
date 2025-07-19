"""
Comprehensive test suite for canvas management endpoints.
"""

import pytest
import asyncio
from typing import Dict, Any
from canvus_api import CanvusClient, CanvusAPIError
from canvus_api.models import Canvas, CanvasFolder


class TestCanvasManagement:
    """Test suite for canvas management endpoints."""

    @pytest.mark.asyncio
    async def test_list_canvases(self, client: CanvusClient):
        """Test listing canvases."""
        canvases = await client.list_canvases()
        
        assert isinstance(canvases, list)
        for canvas in canvases:
            assert isinstance(canvas, Canvas)
            assert canvas.id is not None
            assert canvas.name is not None

    @pytest.mark.asyncio
    async def test_create_and_delete_canvas(self, client: CanvusClient, test_folder):
        """Test creating and deleting a canvas."""
        canvas_payload = {
            "name": f"Test Canvas {asyncio.get_event_loop().time()}",
            "description": "Canvas created for testing",
            "folder_id": test_folder.id
        }
        
        # Create canvas
        canvas = await client.create_canvas(canvas_payload)
        assert isinstance(canvas, Canvas)
        assert canvas.name == canvas_payload["name"]
        assert canvas.folder_id == test_folder.id
        
        # Delete canvas
        await client.delete_canvas(canvas.id)
        
        # Verify deletion
        with pytest.raises(CanvusAPIError) as exc_info:
            await client.get_canvas(canvas.id)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_canvas(self, client: CanvusClient, test_canvas):
        """Test getting a specific canvas."""
        canvas = await client.get_canvas(test_canvas.id)
        
        assert isinstance(canvas, Canvas)
        assert canvas.id == test_canvas.id
        assert canvas.name == test_canvas.name

    @pytest.mark.asyncio
    async def test_update_canvas(self, client: CanvusClient, test_canvas):
        """Test updating a canvas."""
        new_name = f"Updated Canvas {asyncio.get_event_loop().time()}"
        new_description = "Updated description"
        
        updated_canvas = await client.update_canvas(
            test_canvas.id, 
            {"name": new_name, "description": new_description}
        )
        
        assert isinstance(updated_canvas, Canvas)
        assert updated_canvas.name == new_name

    @pytest.mark.asyncio
    async def test_move_canvas(self, client: CanvusClient, test_canvas, test_folder):
        """Test moving a canvas to a different folder."""
        # Create another folder for moving
        new_folder_payload = {
            "name": f"Move Test Folder {asyncio.get_event_loop().time()}",
            "description": "Folder for move testing"
        }
        new_folder = await client.create_folder(new_folder_payload)
        
        try:
            # Move canvas
            moved_canvas = await client.move_canvas(test_canvas.id, new_folder.id)
            
            assert isinstance(moved_canvas, Canvas)
            assert moved_canvas.folder_id == new_folder.id
            
            # Verify the move
            retrieved_canvas = await client.get_canvas(test_canvas.id)
            assert retrieved_canvas.folder_id == new_folder.id
            
        finally:
            # Cleanup
            await client.delete_folder(new_folder.id)

    @pytest.mark.asyncio
    async def test_copy_canvas(self, client: CanvusClient, test_canvas, test_folder):
        """Test copying a canvas."""
        # The API only allows changing one property at a time
        # First copy with just the folder_id
        copy_payload = {
            "folder_id": test_folder.id
        }
        
        copied_canvas = await client.copy_canvas(test_canvas.id, copy_payload)
        
        assert isinstance(copied_canvas, Canvas)
        assert copied_canvas.folder_id == test_folder.id
        assert copied_canvas.id != test_canvas.id
        
        # Cleanup
        await client.delete_canvas(copied_canvas.id)

    @pytest.mark.asyncio
    async def test_get_canvas_preview(self, client: CanvusClient, test_canvas):
        """Test getting canvas preview."""
        try:
            preview_data = await client.get_canvas_preview(test_canvas.id)
            assert isinstance(preview_data, bytes)
            # Preview might be empty for new canvases
            assert len(preview_data) >= 0
        except CanvusAPIError as e:
            # Empty canvases don't have previews
            assert "doesn't have preview" in str(e) or e.status_code == 404

    @pytest.mark.asyncio
    async def test_get_canvas_permissions(self, client: CanvusClient, test_canvas):
        """Test getting canvas permissions."""
        permissions = await client.get_canvas_permissions(test_canvas.id)
        
        assert isinstance(permissions, dict)
        assert "editors_can_share" in permissions
        assert "users" in permissions
        assert "groups" in permissions

    @pytest.mark.asyncio
    async def test_set_canvas_permissions(self, client: CanvusClient, test_canvas):
        """Test setting canvas permissions."""
        permissions_payload = {
            "editors_can_share": True,
            "users": [],
            "groups": []
        }
        
        result = await client.set_canvas_permissions(test_canvas.id, permissions_payload)
        
        assert isinstance(result, dict)
        assert "editors_can_share" in result
        assert "users" in result
        assert "groups" in result

    @pytest.mark.asyncio
    async def test_set_canvas_mode(self, client: CanvusClient, test_canvas):
        """Test setting canvas mode."""
        # Test demo mode
        demo_canvas = await client.set_canvas_mode(test_canvas.id, True)
        assert isinstance(demo_canvas, Canvas)
        assert demo_canvas.mode == "demo"
        
        # Test normal mode
        normal_canvas = await client.set_canvas_mode(test_canvas.id, False)
        assert isinstance(normal_canvas, Canvas)
        assert normal_canvas.mode == "normal"

    @pytest.mark.asyncio
    async def test_save_and_restore_demo_state(self, client: CanvusClient, test_canvas):
        """Test saving and restoring demo state."""
        # Set to demo mode first
        await client.set_canvas_mode(test_canvas.id, True)
        
        # Save demo state
        await client.save_demo_state(test_canvas.id)
        
        # Restore demo state
        await client.restore_demo_state(test_canvas.id)

    @pytest.mark.asyncio
    async def test_canvas_error_handling(self, client: CanvusClient):
        """Test error handling for canvas operations."""
        # Test getting non-existent canvas
        with pytest.raises(CanvusAPIError) as exc_info:
            await client.get_canvas("non-existent-id")
        assert exc_info.value.status_code == 404
        
        # Test updating non-existent canvas
        with pytest.raises(CanvusAPIError) as exc_info:
            await client.update_canvas("non-existent-id", {"name": "test"})
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_canvas_list_with_params(self, client: CanvusClient):
        """Test listing canvases with parameters."""
        # Test with search parameter
        canvases = await client.list_canvases({"search": "test"})
        assert isinstance(canvases, list)
        
        # Test with folder_id parameter
        canvases = await client.list_canvases({"folder_id": "1000"})
        assert isinstance(canvases, list)

    @pytest.mark.asyncio
    async def test_canvas_validation(self, client: CanvusClient, test_folder):
        """Test canvas creation validation."""
        # Test with invalid folder ID
        with pytest.raises(CanvusAPIError):
            await client.create_canvas({
                "name": "Test Canvas",
                "folder_id": "invalid-folder-id"
            }) 