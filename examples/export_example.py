#!/usr/bin/env python3
"""
Example script demonstrating the export functionality.

This script shows how to export widgets from a canvas and import them to another canvas.
"""

import tempfile
from pathlib import Path

from canvus_api import CanvusClient
from canvus_api.export import (
    ExportConfig,
    ImportConfig,
    export_widgets_to_folder,
    import_widgets_from_folder
)


async def export_import_example():
    """Demonstrate export and import functionality."""
    
    # Configuration - replace with your actual values
    base_url = "https://your-canvus-server.com"
    api_key = "your-api-key"
    source_canvas_id = "source-canvas-id"
    target_canvas_id = "target-canvas-id"
    
    # Create client
    async with CanvusClient(base_url, api_key) as client:
        
        print("🚀 Starting export/import example...")
        
        try:
            # Step 1: Export widgets from source canvas
            print(f"📦 Exporting widgets from canvas {source_canvas_id}...")
            
            # Configure export settings
            export_config = ExportConfig(
                include_assets=True,      # Export image/video/PDF files
                include_spatial_data=True, # Include position and size data
                include_metadata=True,    # Include widget metadata
                asset_format="original",  # Keep original file format
                overwrite_existing=True   # Overwrite existing export folders
            )
            
            # Create temporary directory for export
            with tempfile.TemporaryDirectory() as temp_dir:
                export_path = Path(temp_dir) / "widget_export"
                
                # Export all widgets from source canvas
                exported_folder = await export_widgets_to_folder(
                    client=client,
                    canvas_id=source_canvas_id,
                    folder_path=str(export_path),
                    config=export_config
                )
                
                print(f"✅ Exported widgets to: {exported_folder}")
                
                # Step 2: Import widgets to target canvas
                print(f"📥 Importing widgets to canvas {target_canvas_id}...")
                
                # Configure import settings
                import_config = ImportConfig(
                    import_assets=True,           # Import asset files
                    restore_spatial_data=True,    # Restore position and size
                    restore_metadata=True,        # Restore widget metadata
                    spatial_offset={"x": 100, "y": 100},  # Offset widgets by 100px
                    preserve_ids=False            # Generate new widget IDs
                )
                
                # Import widgets to target canvas
                import_result = await import_widgets_from_folder(
                    client=client,
                    folder_path=exported_folder,
                    target_canvas_id=target_canvas_id,
                    config=import_config
                )
                
                print(f"✅ Imported {import_result['imported_count']} widgets")
                print("📊 Import summary:")
                print(f"   - Target canvas: {import_result['target_canvas']}")
                print(f"   - Widgets imported: {len(import_result['widgets'])}")
                print(f"   - ID mappings: {len(import_result['id_mapping'])}")
                
                # Display widget details
                for widget_info in import_result['widgets']:
                    print(f"   - {widget_info['widget_type']}: {widget_info['original_id']} → {widget_info['new_id']}")
                
                print("🎉 Export/import completed successfully!")
        
        except Exception as e:
            print(f"❌ Error: {e}")
            raise


async def export_specific_widgets_example():
    """Demonstrate exporting specific widgets by ID."""
    
    # Configuration
    base_url = "https://your-canvus-server.com"
    api_key = "your-api-key"
    canvas_id = "canvas-id"
    widget_ids = ["widget-1", "widget-2", "widget-3"]  # Specific widget IDs to export
    
    async with CanvusClient(base_url, api_key) as client:
        
        print("🎯 Exporting specific widgets...")
        
        try:
            # Export only specific widgets
            with tempfile.TemporaryDirectory() as temp_dir:
                export_path = Path(temp_dir) / "specific_widgets"
                
                exported_folder = await export_widgets_to_folder(
                    client=client,
                    canvas_id=canvas_id,
                    widget_ids=widget_ids,  # Export only these widgets
                    folder_path=str(export_path)
                )
                
                print(f"✅ Exported {len(widget_ids)} specific widgets to: {exported_folder}")
        
        except Exception as e:
            print(f"❌ Error: {e}")
            raise


async def export_without_assets_example():
    """Demonstrate exporting widgets without asset files."""
    
    # Configuration
    base_url = "https://your-canvus-server.com"
    api_key = "your-api-key"
    canvas_id = "canvas-id"
    
    async with CanvusClient(base_url, api_key) as client:
        
        print("📄 Exporting widgets without assets...")
        
        try:
            # Configure export without assets
            export_config = ExportConfig(
                include_assets=False,     # Don't export asset files
                include_spatial_data=True,
                include_metadata=True
            )
            
            with tempfile.TemporaryDirectory() as temp_dir:
                export_path = Path(temp_dir) / "widgets_only"
                
                exported_folder = await export_widgets_to_folder(
                    client=client,
                    canvas_id=canvas_id,
                    folder_path=str(export_path),
                    config=export_config
                )
                
                print(f"✅ Exported widgets (without assets) to: {exported_folder}")
                print("📝 Note: Asset files (images, videos, PDFs) were not exported")
        
        except Exception as e:
            print(f"❌ Error: {e}")
            raise


if __name__ == "__main__":
    # Run the examples
    print("📚 Canvus Export/Import Examples")
    print("=" * 50)
    
    # Note: These examples require actual server configuration
    print("⚠️  Note: These examples require actual server configuration.")
    print("   Please update the base_url, api_key, and canvas IDs before running.")
    print()
    
    # Uncomment the example you want to run:
    
    # asyncio.run(export_import_example())
    # asyncio.run(export_specific_widgets_example())
    # asyncio.run(export_without_assets_example())
    
    print("💡 To run an example, uncomment the corresponding line above.") 