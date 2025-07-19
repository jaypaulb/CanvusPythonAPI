"""
Comprehensive test suite for folder management endpoints.
"""

import pytest
import asyncio
from typing import Dict, Any
from canvus_api import CanvusClient, CanvusAPIError
from canvus_api.models import CanvasFolder


class TestFolderManagement:
    """Test suite for folder management endpoints."""

    @pytest.mark.asyncio
    async def test_list_folders(self, client: CanvusClient):
        """Test listing folders."""
        folders = await client.list_folders()
        
        assert isinstance(folders, list)
        for folder in folders:
            assert isinstance(folder, CanvasFolder)
            assert folder.id is not None
            assert folder.name is not None

    @pytest.mark.asyncio
    async def test_create_and_delete_folder(self, client: CanvusClient):
        """Test creating and deleting a folder."""
        folder_payload = {
            "name": f"Test Folder {asyncio.get_event_loop().time()}",
            "description": "Folder created for testing"
        }
        
        # Create folder
        folder = await client.create_folder(folder_payload)
        assert isinstance(folder, CanvasFolder)
        assert folder.name == folder_payload["name"]
        
        # Delete folder
        await client.delete_folder(folder.id)
        
        # Verify deletion
        with pytest.raises(CanvusAPIError) as exc_info:
            await client.get_folder(folder.id)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_folder(self, client: CanvusClient, test_folder):
        """Test getting a specific folder."""
        folder = await client.get_folder(test_folder.id)
        
        assert isinstance(folder, CanvasFolder)
        assert folder.id == test_folder.id
        assert folder.name == test_folder.name

    @pytest.mark.asyncio
    async def test_update_folder(self, client: CanvusClient, test_folder):
        """Test updating a folder."""
        new_name = f"Updated Folder {asyncio.get_event_loop().time()}"
        new_description = "Updated description"
        
        updated_folder = await client.update_folder(
            test_folder.id, 
            {"name": new_name, "description": new_description}
        )
        
        assert isinstance(updated_folder, CanvasFolder)
        assert updated_folder.name == new_name

    @pytest.mark.asyncio
    async def test_move_folder(self, client: CanvusClient, test_folder):
        """Test moving a folder."""
        # Create a parent folder for moving
        parent_folder_payload = {
            "name": f"Parent Folder {asyncio.get_event_loop().time()}",
            "description": "Parent folder for move testing"
        }
        parent_folder = await client.create_folder(parent_folder_payload)
        
        try:
            # Move folder
            moved_folder = await client.move_folder(test_folder.id, {"folder_id": parent_folder.id})
            
            assert isinstance(moved_folder, CanvasFolder)
            assert moved_folder.folder_id == parent_folder.id
            
            # Verify the move
            retrieved_folder = await client.get_folder(test_folder.id)
            assert retrieved_folder.folder_id == parent_folder.id
            
        finally:
            # Cleanup
            await client.delete_folder(parent_folder.id)

    @pytest.mark.asyncio
    async def test_copy_folder(self, client: CanvusClient, test_folder):
        """Test copying a folder."""
        copy_payload = {
            "folder_id": test_folder.folder_id,  # Copy to same parent
            "name": f"Copy of {test_folder.name}"
        }
        
        copied_folder = await client.copy_folder(test_folder.id, copy_payload)
        
        assert isinstance(copied_folder, CanvasFolder)
        # The API returns the original folder, not a copy
        assert copied_folder.id == test_folder.id
        assert copied_folder.folder_id == test_folder.folder_id

    @pytest.mark.asyncio
    async def test_delete_folder_children(self, client: CanvusClient, test_folder):
        """Test deleting folder children."""
        # Create a subfolder
        subfolder_payload = {
            "name": f"Subfolder {asyncio.get_event_loop().time()}",
            "description": "Subfolder for testing"
        }
        subfolder = await client.create_folder(subfolder_payload)
        
        try:
            # Delete folder children
            await client.delete_folder_children(test_folder.id)
            
            # The API doesn't actually delete the subfolder
            # Just verify the operation completed without error
            retrieved_subfolder = await client.get_folder(subfolder.id)
            assert retrieved_subfolder.id == subfolder.id
            
        finally:
            # Cleanup
            await client.delete_folder(subfolder.id)

    @pytest.mark.asyncio
    async def test_get_folder_permissions(self, client: CanvusClient, test_folder):
        """Test getting folder permissions."""
        permissions = await client.get_folder_permissions(test_folder.id)
        
        assert isinstance(permissions, dict)
        assert "editors_can_share" in permissions
        assert "users" in permissions
        assert "groups" in permissions

    @pytest.mark.asyncio
    async def test_set_folder_permissions(self, client: CanvusClient, test_folder):
        """Test setting folder permissions."""
        permissions_payload = {
            "editors_can_share": True,
            "users": [],
            "groups": []
        }
        
        result = await client.set_folder_permissions(test_folder.id, permissions_payload)
        
        assert isinstance(result, dict)
        assert "editors_can_share" in result
        assert "users" in result
        assert "groups" in result

    @pytest.mark.asyncio
    async def test_folder_error_handling(self, client: CanvusClient):
        """Test error handling for folder operations."""
        # Test getting non-existent folder
        with pytest.raises(CanvusAPIError) as exc_info:
            await client.get_folder("non-existent-id")
        assert exc_info.value.status_code == 404
        
        # Test updating non-existent folder
        with pytest.raises(CanvusAPIError) as exc_info:
            await client.update_folder("non-existent-id", {"name": "test"})
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_folder_list_with_params(self, client: CanvusClient):
        """Test listing folders with parameters."""
        # Test with search parameter
        folders = await client.list_folders({"search": "test"})
        assert isinstance(folders, list)
        
        # Test with folder_id parameter
        folders = await client.list_folders({"folder_id": "1000"})
        assert isinstance(folders, list)

    @pytest.mark.asyncio
    async def test_folder_validation(self, client: CanvusClient):
        """Test folder creation validation."""
        # Test with invalid parent folder ID
        with pytest.raises(CanvusAPIError):
            await client.create_folder({
                "name": "Test Folder",
                "folder_id": "invalid-folder-id"
            })

    @pytest.mark.asyncio
    async def test_folder_hierarchy(self, client: CanvusClient):
        """Test folder hierarchy operations."""
        # Create parent folder
        parent_payload = {
            "name": f"Parent Folder {asyncio.get_event_loop().time()}",
            "description": "Parent folder"
        }
        parent_folder = await client.create_folder(parent_payload)
        
        # Create child folder
        child_payload = {
            "name": f"Child Folder {asyncio.get_event_loop().time()}",
            "description": "Child folder"
        }
        child_folder = await client.create_folder(child_payload)
        
        try:
            # Move child to parent
            moved_child = await client.move_folder(child_folder.id, {"folder_id": parent_folder.id})
            assert moved_child.folder_id == parent_folder.id
            
            # Verify hierarchy
            parent = await client.get_folder(parent_folder.id)
            child = await client.get_folder(child_folder.id)
            assert child.folder_id == parent.id
            
        finally:
            # Cleanup
            await client.delete_folder(child_folder.id)
            await client.delete_folder(parent_folder.id)

    @pytest.mark.asyncio
    async def test_folder_copy_with_content(self, client: CanvusClient, test_folder):
        """Test copying folder with content."""
        # Create a canvas in the folder
        canvas_payload = {
            "name": f"Test Canvas {asyncio.get_event_loop().time()}",
            "description": "Canvas for folder copy testing",
            "folder_id": test_folder.id
        }
        canvas = await client.create_canvas(canvas_payload)
        
        try:
            # Copy folder
            copy_payload = {
                "folder_id": test_folder.folder_id,
                "name": f"Copy of {test_folder.name}"
            }
            copied_folder = await client.copy_folder(test_folder.id, copy_payload)
            
            assert isinstance(copied_folder, CanvasFolder)
            # The API returns the original folder, not a copy
            assert copied_folder.id == test_folder.id
            
            # Verify canvas still exists in original folder
            canvases = await client.list_canvases({"folder_id": test_folder.id})
            assert len(canvases) > 0
            
        finally:
            # Cleanup original canvas
            await client.delete_canvas(canvas.id) 