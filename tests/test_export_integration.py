#!/usr/bin/env python3
"""
Integration tests for the export functionality.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from tests.test_config import TestClient, TestConfig
from canvus_api.export import (
    ExportConfig,
    ImportConfig,
    WidgetExporter,
    WidgetImporter,
    export_widgets_to_folder,
    import_widgets_from_folder
)


class TestExportIntegration:
    """Integration tests for export functionality."""
    
    @pytest.fixture
    def test_config(self):
        """Create test configuration."""
        return TestConfig('tests/test_config.json')
    
    @pytest.fixture
    def export_config(self):
        """Create export configuration."""
        return ExportConfig(
            include_assets=True,
            include_spatial_data=True,
            include_metadata=True,
            overwrite_existing=True
        )
    
    @pytest.fixture
    def import_config(self):
        """Create import configuration."""
        return ImportConfig(
            import_assets=True,
            restore_spatial_data=True,
            restore_metadata=True
        )
    
    async def test_export_import_round_trip(self, test_config, export_config, import_config):
        """Test complete export and import round trip."""
        # Target canvas ID for testing
        canvas_id = '30b6d41a-05bf-4e41-b002-9d85ea295fa4'  # API TEST canvas
        
        async with TestClient(test_config) as test_client:
            client = test_client.client
            
            try:
                # Step 1: Create test widgets for export
                print("📝 Creating test widgets for export...")
                
                # Create a test note
                note_payload = {
                    "title": "EXPORT_TEST_NOTE",
                    "text": "This is a test note for export functionality",
                    "background_color": "#00ff00ff",
                    "location": {"x": 100, "y": 100},
                    "size": {"width": 200, "height": 150}
                }
                test_note = await client.create_note(canvas_id, note_payload)
                print(f"✅ Created test note: {test_note.title} (ID: {test_note.id})")
                
                # Create a test browser widget
                browser_payload = {
                    "url": "https://example.com",
                    "title": "EXPORT_TEST_BROWSER",
                    "location": {"x": 350, "y": 100},
                    "size": {"width": 300, "height": 200}
                }
                test_browser = await client.create_browser(canvas_id, browser_payload)
                print(f"✅ Created test browser: {test_browser.title} (ID: {test_browser.id})")
                
                # Step 2: Export widgets
                print("📦 Exporting widgets...")
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    export_path = Path(temp_dir) / "export"
                    
                    # Export specific widgets
                    exported_folder = await export_widgets_to_folder(
                        client=client,
                        canvas_id=canvas_id,
                        widget_ids=[test_note.id, test_browser.id],
                        folder_path=str(export_path),
                        config=export_config
                    )
                    
                    print(f"✅ Exported widgets to: {exported_folder}")
                    
                    # Verify export structure
                    export_folder = Path(exported_folder)
                    assert export_folder.exists()
                    assert (export_folder / "widgets").exists()
                    assert (export_folder / "assets").exists()
                    assert (export_folder / "manifest.json").exists()
                    
                    # Verify widget files
                    widget_files = list((export_folder / "widgets").glob("*.json"))
                    assert len(widget_files) == 2
                    
                    # Verify manifest
                    import json
                    with open(export_folder / "manifest.json") as f:
                        manifest = json.load(f)
                    
                    assert manifest["version"] == "1.0"
                    assert canvas_id in manifest["canvases"]
                    
                    # Step 3: Import widgets to a different location
                    print("📥 Importing widgets...")
                    
                    # Create a new canvas for import testing
                    new_canvas_payload = {
                        "name": f"Import Test Canvas {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        "description": "Test canvas for import functionality"
                    }
                    new_canvas = await client.create_canvas(new_canvas_payload)
                    print(f"✅ Created new canvas: {new_canvas.name} (ID: {new_canvas.id})")
                    
                    # Import widgets with spatial offset
                    import_config.spatial_offset = {"x": 500, "y": 0}
                    import_result = await import_widgets_from_folder(
                        client=client,
                        folder_path=exported_folder,
                        target_canvas_id=new_canvas.id,
                        config=import_config
                    )
                    
                    print(f"✅ Imported {import_result['imported_count']} widgets")
                    
                    # Verify import results
                    assert import_result["imported_count"] == 2
                    assert import_result["target_canvas"] == new_canvas.id
                    assert len(import_result["widgets"]) == 2
                    assert len(import_result["id_mapping"]) == 2
                    
                    # Verify widgets were created in new canvas
                    new_widgets = await client.list_widgets(new_canvas.id)
                    assert len(new_widgets) == 2
                    
                    # Verify spatial offset was applied
                    for widget in new_widgets:
                        widget_data = widget.model_dump() if hasattr(widget, 'model_dump') else dict(widget)
                        title = widget_data.get('title', '')
                        if title == "EXPORT_TEST_NOTE":
                            assert widget.location["x"] == 600  # 100 + 500 offset
                            assert widget.location["y"] == 100
                        elif title == "EXPORT_TEST_BROWSER":
                            assert widget.location["x"] == 850  # 350 + 500 offset
                            assert widget.location["y"] == 100
                    
                    print("✅ Round-trip export/import test completed successfully!")
                    
                    # Cleanup: Delete the test canvas
                    await client.delete_canvas(new_canvas.id)
                    print(f"🧹 Cleaned up test canvas: {new_canvas.id}")
                
            except Exception as e:
                print(f"❌ Test failed: {e}")
                raise
    
    async def test_export_all_widgets(self, test_config, export_config):
        """Test exporting all widgets from a canvas."""
        # Target canvas ID for testing
        canvas_id = '30b6d41a-05bf-4e41-b002-9d85ea295fa4'  # API TEST canvas
        
        async with TestClient(test_config) as test_client:
            client = test_client.client
            
            try:
                # Get current widget count
                widgets = await client.list_widgets(canvas_id)
                initial_count = len(widgets)
                print(f"📊 Canvas has {initial_count} widgets")
                
                if initial_count == 0:
                    print("⚠️ No widgets to export, skipping test")
                    return
                
                # Export all widgets
                print("📦 Exporting all widgets...")
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    export_path = Path(temp_dir) / "export_all"
                    
                    exported_folder = await export_widgets_to_folder(
                        client=client,
                        canvas_id=canvas_id,
                        folder_path=str(export_path),
                        config=export_config
                    )
                    
                    print(f"✅ Exported all widgets to: {exported_folder}")
                    
                    # Verify export
                    export_folder = Path(exported_folder)
                    widget_files = list((export_folder / "widgets").glob("*.json"))
                    assert len(widget_files) == initial_count
                    
                    print(f"✅ Successfully exported {len(widget_files)} widgets")
                
            except Exception as e:
                print(f"❌ Test failed: {e}")
                raise
    
    async def test_export_without_assets(self, test_config):
        """Test exporting widgets without assets."""
        # Target canvas ID for testing
        canvas_id = '30b6d41a-05bf-4e41-b002-9d85ea295fa4'  # API TEST canvas
        
        # Create config without assets
        export_config = ExportConfig(
            include_assets=False,
            include_spatial_data=True,
            include_metadata=True,
            overwrite_existing=True
        )
        
        async with TestClient(test_config) as test_client:
            client = test_client.client
            
            try:
                # Export widgets without assets
                print("📦 Exporting widgets without assets...")
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    export_path = Path(temp_dir) / "export_no_assets"
                    
                    exported_folder = await export_widgets_to_folder(
                        client=client,
                        canvas_id=canvas_id,
                        folder_path=str(export_path),
                        config=export_config
                    )
                    
                    print(f"✅ Exported widgets to: {exported_folder}")
                    
                    # Verify export structure
                    export_folder = Path(exported_folder)
                    assert export_folder.exists()
                    assert (export_folder / "widgets").exists()
                    assert (export_folder / "assets").exists()
                    
                    # Verify assets directory is empty (no assets exported)
                    asset_files = list((export_folder / "assets").glob("*"))
                    assert len(asset_files) == 0
                    
                    print("✅ Successfully exported widgets without assets")
                
            except Exception as e:
                print(f"❌ Test failed: {e}")
                raise
    
    async def test_export_config_validation(self, test_config):
        """Test export configuration validation."""
        # Target canvas ID for testing
        canvas_id = '30b6d41a-05bf-4e41-b002-9d85ea295fa4'  # API TEST canvas
        
        async with TestClient(test_config) as test_client:
            client = test_client.client
            
            try:
                # Test with different export configurations
                configs = [
                    ExportConfig(include_assets=True, asset_format="original"),
                    ExportConfig(include_assets=False, asset_format="compressed"),
                    ExportConfig(include_spatial_data=False, include_metadata=False)
                ]
                
                for i, config in enumerate(configs):
                    print(f"🧪 Testing export config {i+1}...")
                    
                    with tempfile.TemporaryDirectory() as temp_dir:
                        export_path = Path(temp_dir) / f"export_config_{i}"
                        
                        exported_folder = await export_widgets_to_folder(
                            client=client,
                            canvas_id=canvas_id,
                            folder_path=str(export_path),
                            config=config
                        )
                        
                        # Verify export was successful
                        export_folder = Path(exported_folder)
                        assert export_folder.exists()
                        assert (export_folder / "manifest.json").exists()
                        
                        # Verify config was saved in manifest
                        import json
                        with open(export_folder / "manifest.json") as f:
                            manifest = json.load(f)
                        
                        saved_config = manifest["config"]
                        assert saved_config["include_assets"] == config.include_assets
                        assert saved_config["asset_format"] == config.asset_format
                        
                        print(f"✅ Export config {i+1} test passed")
                
            except Exception as e:
                print(f"❌ Test failed: {e}")
                raise 