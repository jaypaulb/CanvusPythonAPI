#!/usr/bin/env python3
"""
Unit tests for the export functionality.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from canvus_api.export import (
    ExportConfig,
    ImportConfig,
    WidgetExporter,
    WidgetImporter,
    export_widgets_to_folder,
    import_widgets_from_folder
)
from canvus_api.client import CanvusClient
from canvus_api.models import Canvas
from canvus_api.exceptions import CanvusAPIError


class TestExportConfig:
    """Test ExportConfig class."""
    
    def test_export_config_defaults(self):
        """Test ExportConfig with default values."""
        config = ExportConfig()
        
        assert config.include_assets is True
        assert config.include_spatial_data is True
        assert config.include_metadata is True
        assert config.asset_format == "original"
        assert config.export_path == Path.cwd()
        assert config.overwrite_existing is False
    
    def test_export_config_custom(self):
        """Test ExportConfig with custom values."""
        config = ExportConfig(
            include_assets=False,
            include_spatial_data=False,
            include_metadata=False,
            asset_format="compressed",
            export_path="/tmp/test",
            overwrite_existing=True
        )
        
        assert config.include_assets is False
        assert config.include_spatial_data is False
        assert config.include_metadata is False
        assert config.asset_format == "compressed"
        assert config.export_path == Path("/tmp/test")
        assert config.overwrite_existing is True


class TestImportConfig:
    """Test ImportConfig class."""
    
    def test_import_config_defaults(self):
        """Test ImportConfig with default values."""
        config = ImportConfig()
        
        assert config.import_assets is True
        assert config.restore_spatial_data is True
        assert config.restore_metadata is True
        assert config.target_canvas_id is None
        assert config.spatial_offset == {"x": 0, "y": 0}
        assert config.preserve_ids is False
    
    def test_import_config_custom(self):
        """Test ImportConfig with custom values."""
        config = ImportConfig(
            import_assets=False,
            restore_spatial_data=False,
            restore_metadata=False,
            target_canvas_id="test-canvas",
            spatial_offset={"x": 100, "y": 200},
            preserve_ids=True
        )
        
        assert config.import_assets is False
        assert config.restore_spatial_data is False
        assert config.restore_metadata is False
        assert config.target_canvas_id == "test-canvas"
        assert config.spatial_offset == {"x": 100, "y": 200}
        assert config.preserve_ids is True


class TestWidgetExporter:
    """Test WidgetExporter class."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock CanvusClient."""
        client = AsyncMock(spec=CanvusClient)
        return client
    
    @pytest.fixture
    def export_config(self):
        """Create a test export configuration."""
        return ExportConfig(
            include_assets=True,
            include_spatial_data=True,
            include_metadata=True,
            overwrite_existing=True
        )
    
    @pytest.fixture
    def test_widgets(self):
        """Create test widget data."""
        return [
            {
                "id": "widget-1",
                "widget_type": "Note",
                "title": "Test Note",
                "text": "Test content",
                "location": {"x": 100, "y": 100},
                "size": {"width": 200, "height": 150},
                "background_color": "#ff0000ff"
            },
            {
                "id": "widget-2", 
                "widget_type": "Image",
                "title": "Test Image",
                "image_url": "https://example.com/image.jpg",
                "location": {"x": 300, "y": 300},
                "size": {"width": 300, "height": 200}
            }
        ]
    
    @pytest.fixture
    def test_canvas(self):
        """Create test canvas data."""
        return Canvas(
            id="test-canvas",
            name="Test Canvas",
            access="public",
            asset_size=1024,
            folder_id="folder-1",
            in_trash=False,
            mode="normal",
            state="normal",
            description="Test canvas for export"
        )
    
    async def test_export_widgets_to_folder_success(self, mock_client, export_config, test_widgets, test_canvas):
        """Test successful widget export."""
        # Setup mocks
        mock_client.get_canvas.return_value = test_canvas
        mock_client.list_widgets.return_value = test_widgets
        mock_client._request.return_value = b"fake_image_data"
        
        # Create exporter
        exporter = WidgetExporter(mock_client, export_config)
        
        # Create temporary directory for test
        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = Path(temp_dir) / "export"
            
            # Export widgets
            result = await exporter.export_widgets_to_folder(
                canvas_id="test-canvas",
                folder_path=str(export_path)
            )
            
            # Verify result
            assert result is not None
            assert Path(result).exists()
            
            # Verify directory structure
            export_folder = Path(result)
            assert (export_folder / "widgets").exists()
            assert (export_folder / "assets").exists()
            assert (export_folder / "metadata").exists()
            assert (export_folder / "manifest.json").exists()
            
            # Verify widget files
            widget_files = list((export_folder / "widgets").glob("*.json"))
            assert len(widget_files) == 2
            
            # Verify manifest
            with open(export_folder / "manifest.json") as f:
                manifest = json.load(f)
            
            assert manifest["version"] == "1.0"
            assert "test-canvas" in manifest["canvases"]
            assert manifest["canvases"]["test-canvas"]["name"] == "Test Canvas"
    
    async def test_export_widgets_to_folder_with_specific_ids(self, mock_client, export_config, test_widgets, test_canvas):
        """Test widget export with specific widget IDs."""
        # Setup mocks
        mock_client.get_canvas.return_value = test_canvas
        mock_client.list_widgets.return_value = test_widgets
        mock_client._request.return_value = b"fake_image_data"
        
        # Create exporter
        exporter = WidgetExporter(mock_client, export_config)
        
        # Create temporary directory for test
        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = Path(temp_dir) / "export"
            
            # Export specific widgets
            result = await exporter.export_widgets_to_folder(
                canvas_id="test-canvas",
                widget_ids=["widget-1"],
                folder_path=str(export_path)
            )
            
            # Verify result
            assert result is not None
            export_folder = Path(result)
            
            # Verify only specified widget was exported
            widget_files = list((export_folder / "widgets").glob("*.json"))
            assert len(widget_files) == 1
            assert widget_files[0].name == "widget-1.json"
    
    async def test_export_widgets_to_folder_no_assets(self, mock_client, test_widgets, test_canvas):
        """Test widget export without assets."""
        # Setup config without assets
        config = ExportConfig(include_assets=False)
        
        # Setup mocks
        mock_client.get_canvas.return_value = test_canvas
        mock_client.list_widgets.return_value = test_widgets
        
        # Create exporter
        exporter = WidgetExporter(mock_client, config)
        
        # Create temporary directory for test
        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = Path(temp_dir) / "export"
            
            # Export widgets
            result = await exporter.export_widgets_to_folder(
                canvas_id="test-canvas",
                folder_path=str(export_path)
            )
            
            # Verify result
            assert result is not None
            export_folder = Path(result)
            
            # Verify assets directory is empty
            asset_files = list((export_folder / "assets").glob("*"))
            assert len(asset_files) == 0
    
    async def test_export_widgets_to_folder_failure(self, mock_client, export_config):
        """Test widget export failure."""
        # Setup mock to raise exception
        mock_client.get_canvas.side_effect = CanvusAPIError("API Error")
        
        # Create exporter
        exporter = WidgetExporter(mock_client, export_config)
        
        # Create temporary directory for test
        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = Path(temp_dir) / "export"
            
            # Test export failure
            with pytest.raises(CanvusAPIError, match="Export failed: API Error"):
                await exporter.export_widgets_to_folder(
                    canvas_id="test-canvas",
                    folder_path=str(export_path)
                )
            
            # Verify no export folder was created
            assert not Path(export_path).exists()


class TestWidgetImporter:
    """Test WidgetImporter class."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock CanvusClient."""
        client = AsyncMock(spec=CanvusClient)
        return client
    
    @pytest.fixture
    def import_config(self):
        """Create a test import configuration."""
        return ImportConfig(
            import_assets=True,
            restore_spatial_data=True,
            restore_metadata=True,
            target_canvas_id="target-canvas"
        )
    
    @pytest.fixture
    def test_export_folder(self):
        """Create a test export folder structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            export_folder = Path(temp_dir) / "test_export"
            
            # Create directory structure
            (export_folder / "widgets").mkdir(parents=True)
            (export_folder / "assets").mkdir(parents=True)
            (export_folder / "metadata").mkdir(parents=True)
            
            # Create test widget file
            widget_data = {
                "id": "widget-1",
                "widget_type": "Note",
                "canvas_id": "source-canvas",
                "exported_at": datetime.utcnow().isoformat(),
                "data": {
                    "id": "widget-1",
                    "widget_type": "Note",
                    "title": "Test Note",
                    "text": "Test content",
                    "location": {"x": 100, "y": 100},
                    "size": {"width": 200, "height": 150},
                    "background_color": "#ff0000ff"
                }
            }
            
            with open(export_folder / "widgets" / "widget-1.json", "w") as f:
                json.dump(widget_data, f)
            
            # Create manifest
            manifest = {
                "version": "1.0",
                "exported_at": datetime.utcnow().isoformat(),
                "config": {},
                "canvases": {
                    "source-canvas": {
                        "name": "Source Canvas",
                        "description": "Test source canvas"
                    }
                },
                "assets": {},
                "relationships": {}
            }
            
            with open(export_folder / "manifest.json", "w") as f:
                json.dump(manifest, f)
            
            yield export_folder
    
    async def test_import_widgets_from_folder_success(self, mock_client, import_config, test_export_folder):
        """Test successful widget import."""
        # Setup mock for widget creation
        mock_widget = MagicMock()
        mock_widget.id = "new-widget-1"
        mock_client.create_note.return_value = mock_widget
        
        # Create importer
        importer = WidgetImporter(mock_client, import_config)
        
        # Import widgets
        result = await importer.import_widgets_from_folder(
            folder_path=str(test_export_folder),
            target_canvas_id="target-canvas"
        )
        
        # Verify result
        assert result["imported_count"] == 1
        assert result["target_canvas"] == "target-canvas"
        assert len(result["widgets"]) == 1
        assert result["widgets"][0]["original_id"] == "widget-1"
        assert result["widgets"][0]["new_id"] == "new-widget-1"
        assert result["widgets"][0]["widget_type"] == "Note"
        assert result["widgets"][0]["status"] == "imported"
        
        # Verify ID mapping
        assert result["id_mapping"]["widget-1"] == "new-widget-1"
        
        # Verify widget creation was called
        mock_client.create_note.assert_called_once()
        call_args = mock_client.create_note.call_args
        assert call_args[0][0] == "target-canvas"  # canvas_id
        assert call_args[0][1]["title"] == "Test Note"  # payload
    
    async def test_import_widgets_from_folder_with_spatial_offset(self, mock_client, test_export_folder):
        """Test widget import with spatial offset."""
        # Setup config with spatial offset
        config = ImportConfig(
            spatial_offset={"x": 50, "y": 75},
            target_canvas_id="target-canvas"
        )
        
        # Setup mock for widget creation
        mock_widget = MagicMock()
        mock_widget.id = "new-widget-1"
        mock_client.create_note.return_value = mock_widget
        
        # Create importer
        importer = WidgetImporter(mock_client, config)
        
        # Import widgets
        await importer.import_widgets_from_folder(
            folder_path=str(test_export_folder)
        )
        
        # Verify spatial offset was applied
        mock_client.create_note.assert_called_once()
        call_args = mock_client.create_note.call_args
        payload = call_args[0][1]
        assert payload["location"]["x"] == 150  # 100 + 50
        assert payload["location"]["y"] == 175  # 100 + 75
    
    async def test_import_widgets_from_folder_missing_folder(self, mock_client, import_config):
        """Test widget import with missing folder."""
        # Create importer
        importer = WidgetImporter(mock_client, import_config)
        
        # Test import with non-existent folder
        with pytest.raises(CanvusAPIError, match="Export folder.*does not exist"):
            await importer.import_widgets_from_folder(
                folder_path="/non/existent/path"
            )
    
    async def test_import_widgets_from_folder_missing_manifest(self, mock_client, import_config):
        """Test widget import with missing manifest."""
        # Create temporary directory without manifest
        with tempfile.TemporaryDirectory() as temp_dir:
            export_folder = Path(temp_dir)
            (export_folder / "widgets").mkdir(parents=True)
            
            # Create importer
            importer = WidgetImporter(mock_client, import_config)
            
            # Test import with missing manifest
            with pytest.raises(CanvusAPIError, match="Export manifest not found"):
                await importer.import_widgets_from_folder(
                    folder_path=str(export_folder)
                )
    
    async def test_import_widgets_from_folder_no_target_canvas(self, mock_client, test_export_folder):
        """Test widget import without target canvas."""
        # Setup config without target canvas
        config = ImportConfig()
        
        # Create importer
        importer = WidgetImporter(mock_client, config)
        
        # Test import without target canvas
        with pytest.raises(CanvusAPIError, match="Target canvas ID must be specified"):
            await importer.import_widgets_from_folder(
                folder_path=str(test_export_folder)
            )


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock CanvusClient."""
        client = AsyncMock(spec=CanvusClient)
        return client
    
    async def test_export_widgets_to_folder_function(self, mock_client):
        """Test export_widgets_to_folder convenience function."""
        # Setup mocks
        mock_client.get_canvas.return_value = MagicMock()
        mock_client.list_widgets.return_value = []
        
        # Create temporary directory for test
        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = Path(temp_dir) / "export"
            
            # Test convenience function
            result = await export_widgets_to_folder(
                client=mock_client,
                canvas_id="test-canvas",
                folder_path=str(export_path)
            )
            
            # Verify result
            assert result is not None
            assert Path(result).exists()
    
    async def test_import_widgets_from_folder_function(self, mock_client):
        """Test import_widgets_from_folder convenience function."""
        # Create test export folder
        with tempfile.TemporaryDirectory() as temp_dir:
            export_folder = Path(temp_dir)
            
            # Create minimal export structure
            (export_folder / "widgets").mkdir(parents=True)
            
            # Create test widget file
            widget_data = {
                "id": "widget-1",
                "widget_type": "Note",
                "canvas_id": "source-canvas",
                "exported_at": datetime.utcnow().isoformat(),
                "data": {
                    "id": "widget-1",
                    "widget_type": "Note",
                    "title": "Test Note",
                    "text": "Test content",
                    "location": {"x": 100, "y": 100},
                    "size": {"width": 200, "height": 150}
                }
            }
            
            with open(export_folder / "widgets" / "widget-1.json", "w") as f:
                json.dump(widget_data, f)
            
            # Create manifest
            manifest = {
                "version": "1.0",
                "exported_at": datetime.utcnow().isoformat(),
                "config": {},
                "canvases": {},
                "assets": {},
                "relationships": {}
            }
            
            with open(export_folder / "manifest.json", "w") as f:
                json.dump(manifest, f)
            
            # Setup mock for widget creation
            mock_widget = MagicMock()
            mock_widget.id = "new-widget-1"
            mock_client.create_note.return_value = mock_widget
            
            # Test convenience function
            result = await import_widgets_from_folder(
                client=mock_client,
                folder_path=str(export_folder),
                target_canvas_id="target-canvas"
            )
            
            # Verify result
            assert result["imported_count"] == 1
            assert result["target_canvas"] == "target-canvas" 