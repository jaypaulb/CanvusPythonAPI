#!/usr/bin/env python3
"""
Visual test script to investigate parent ID changes using visual snapshots.
This test creates colored notes and captures canvas previews to detect visual movement
when parent relationships change.
"""

import asyncio
import json
import csv
import os
import base64
from datetime import datetime
from typing import Dict, List, Any
import sys
from pathlib import Path

# Add the parent directory to the path to import the API client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_config import TestClient, get_test_config


class VisualParentIDTest:
    def __init__(self):
        self.config = get_test_config()
        self.test_data = []
        self.canvas_id = None
        self.note_ids = []
        self.snapshots_dir = Path("visual_snapshots")
        self.snapshots_dir.mkdir(exist_ok=True)
        
    async def setup(self):
        """Set up the test environment"""
        print("🔧 Setting up test environment...")
        
        # Create test client and authenticate
        async with TestClient(self.config) as test_client:
            self.client = test_client.client
            
            # Create a new canvas
            canvas_payload = {
                "name": f"Visual Parent ID Test - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test canvas for visual parent ID coordinate transformation investigation"
            }
            canvas_data = await self.client.create_canvas(canvas_payload)
            self.canvas_id = canvas_data.id
            print(f"✅ Created test canvas: {self.canvas_id}")
            
            # Create test notes within the same context
            await self.create_test_notes()
        
    async def create_test_notes(self):
        """Create three colored notes with known positions and sizes"""
        print("📝 Creating colored test notes...")
        
        if not self.canvas_id:
            print("❌ No canvas ID available")
            return
        
        # Note 1: Red - Top left
        note1_payload = {
            "text": "RED NOTE 1",
            "location": {"x": 100, "y": 100},
            "scale": {"x": 1.0, "y": 1.0},
            "size": {"width": 200, "height": 150},
            "background_color": "#ff0000ff"  # Red
        }
        note1_data = await self.client.create_note(self.canvas_id, note1_payload)
        self.note_ids.append(note1_data.id)
        print(f"✅ Created RED Note 1: {note1_data.id} at [100, 100]")
        
        # Note 2: Green - Center
        note2_payload = {
            "text": "GREEN NOTE 2",
            "location": {"x": 400, "y": 300},
            "scale": {"x": 1.5, "y": 1.5},
            "size": {"width": 250, "height": 200},
            "background_color": "#00ff00ff"  # Green
        }
        note2_data = await self.client.create_note(self.canvas_id, note2_payload)
        self.note_ids.append(note2_data.id)
        print(f"✅ Created GREEN Note 2: {note2_data.id} at [400, 300]")
        
        # Note 3: Blue - Bottom right
        note3_payload = {
            "text": "BLUE NOTE 3",
            "location": {"x": 700, "y": 500},
            "scale": {"x": 0.8, "y": 0.8},
            "size": {"width": 180, "height": 120},
            "background_color": "#0000ffff"  # Blue
        }
        note3_data = await self.client.create_note(self.canvas_id, note3_payload)
        self.note_ids.append(note3_data.id)
        print(f"✅ Created BLUE Note 3: {note3_data.id} at [700, 500]")
        
    async def capture_canvas_preview(self, stage: str) -> str:
        """Capture canvas preview and save to disk"""
        print(f"📸 Capturing canvas preview for stage: {stage}")
        
        if not self.canvas_id:
            print("❌ No canvas ID available")
            return ""
            
        try:
            # Get canvas preview
            preview_data = await self.client.get_canvas_preview(self.canvas_id)
            
            # Save preview to file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"preview_{stage}_{timestamp}.png"
            filepath = self.snapshots_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(preview_data)
            
            print(f"✅ Saved preview to: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"❌ Error capturing preview: {e}")
            return ""
            
    async def get_widgets_data(self) -> List[Dict[str, Any]]:
        """Get all widgets data from the canvas"""
        if not self.canvas_id:
            return []
        widgets = await self.client.list_widgets(self.canvas_id)
        # Convert Widget objects to dictionaries
        return [widget.model_dump() if hasattr(widget, 'model_dump') else dict(widget) for widget in widgets]
        
    async def record_widget_state(self, stage: str, widgets: List[Dict[str, Any]], preview_path: str = ""):
        """Record the current state of all widgets"""
        print(f"📊 Recording widget state for stage: {stage}")
        
        for widget in widgets:
            if widget.get("widget_type") == "Note" and widget.get("id") in self.note_ids:
                location = widget.get("location", {})
                scale = widget.get("scale", 1)  # Single scale value
                size = widget.get("size", {})
                
                widget_data = {
                    "stage": stage,
                    "timestamp": datetime.now().isoformat(),
                    "widget_id": widget["id"],
                    "content": widget.get("text", ""),
                    "parent_id": widget.get("parent_id"),
                    "location_x": location.get("x", 0),
                    "location_y": location.get("y", 0),
                    "scale": scale,
                    "size_width": size.get("width", 0),
                    "size_height": size.get("height", 0),
                    "background_color": widget.get("background_color", ""),
                    "preview_path": preview_path
                }
                self.test_data.append(widget_data)
                print(f"  📝 {widget['id']}: pos=[{widget_data['location_x']}, {widget_data['location_y']}], "
                      f"scale={widget_data['scale']}, parent={widget_data['parent_id']}, "
                      f"color={widget_data['background_color']}")
        
    async def change_parent_id(self, widget_id: str, new_parent_id: str):
        """Change the parent ID of a widget"""
        print(f"🔄 Changing parent of {widget_id} to {new_parent_id}")
        
        if not self.canvas_id:
            print("❌ No canvas ID available")
            return None
            
        # Update the widget with new parent_id
        update_payload = {
            "parent_id": new_parent_id
        }
        
        try:
            updated_widget = await self.client.update_note(
                self.canvas_id,
                widget_id,
                update_payload
            )
            print(f"✅ Successfully updated parent of {widget_id}")
            return updated_widget
        except Exception as e:
            print(f"❌ Error updating parent: {e}")
            return None
            
    async def run_test_sequence(self):
        """Run the complete test sequence with visual captures"""
        print("🚀 Starting visual parent ID test sequence...")
        
        # Step 1: Get initial state and capture preview
        print("\n📋 Step 1: Initial widget state")
        widgets = await self.get_widgets_data()
        preview_path = await self.capture_canvas_preview("INITIAL")
        await self.record_widget_state("INITIAL", widgets, preview_path)
        
        # Wait a moment for any UI updates
        await asyncio.sleep(2)
        
        # Step 2: Change Note 1's parent to Note 2 and capture
        print("\n🔄 Step 2: Setting Note 1's parent to Note 2")
        await self.change_parent_id(self.note_ids[0], self.note_ids[1])
        
        # Wait for UI to update
        await asyncio.sleep(2)
        
        # Get state and capture preview after first change
        widgets = await self.get_widgets_data()
        preview_path = await self.capture_canvas_preview("NOTE1_TO_NOTE2")
        await self.record_widget_state("NOTE1_TO_NOTE2", widgets, preview_path)
        
        # Step 3: Change Note 2's parent to Note 3 and capture
        print("\n🔄 Step 3: Setting Note 2's parent to Note 3")
        await self.change_parent_id(self.note_ids[1], self.note_ids[2])
        
        # Wait for UI to update
        await asyncio.sleep(2)
        
        # Get state and capture preview after second change
        widgets = await self.get_widgets_data()
        preview_path = await self.capture_canvas_preview("NOTE2_TO_NOTE3")
        await self.record_widget_state("NOTE2_TO_NOTE3", widgets, preview_path)
        
        print("\n✅ Visual test sequence completed!")
        
    async def save_results(self):
        """Save test results to files"""
        print("💾 Saving test results...")
        
        # Save as JSON
        json_filename = f"visual_parent_id_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_filename, 'w') as f:
            json.dump({
                "test_info": {
                    "canvas_id": self.canvas_id,
                    "note_ids": self.note_ids,
                    "timestamp": datetime.now().isoformat(),
                    "description": "Visual parent ID transition test with colored notes",
                    "snapshots_dir": str(self.snapshots_dir)
                },
                "test_data": self.test_data
            }, f, indent=2)
        print(f"✅ Saved JSON results to: {json_filename}")
        
        # Save as CSV
        csv_filename = f"visual_parent_id_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        if self.test_data:
            fieldnames = self.test_data[0].keys()
            with open(csv_filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.test_data)
        print(f"✅ Saved CSV results to: {csv_filename}")
        
        # Create analysis summary
        await self.create_analysis_summary()
        
    async def create_analysis_summary(self):
        """Create a summary of the visual analysis"""
        summary_filename = f"visual_analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(summary_filename, 'w') as f:
            f.write("# Visual Parent ID Test Analysis Summary\n\n")
            f.write(f"**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Canvas ID:** {self.canvas_id}\n\n")
            
            f.write("## Test Setup\n\n")
            f.write("- **RED Note 1:** Initial position [100, 100]\n")
            f.write("- **GREEN Note 2:** Initial position [400, 300]\n")
            f.write("- **BLUE Note 3:** Initial position [700, 500]\n\n")
            
            f.write("## Test Sequence\n\n")
            f.write("1. **INITIAL:** All notes with background parent\n")
            f.write("2. **NOTE1_TO_NOTE2:** RED note becomes child of GREEN note\n")
            f.write("3. **NOTE2_TO_NOTE3:** GREEN note becomes child of BLUE note\n\n")
            
            f.write("## Visual Analysis Instructions\n\n")
            f.write("Compare the PNG files in the `visual_snapshots/` directory:\n\n")
            f.write("- `preview_INITIAL_*.png` - Initial state\n")
            f.write("- `preview_NOTE1_TO_NOTE2_*.png` - After RED note reparented\n")
            f.write("- `preview_NOTE2_TO_NOTE3_*.png` - After GREEN note reparented\n\n")
            
            f.write("## Expected Results\n\n")
            f.write("**If coordinates ARE relative to parents:**\n")
            f.write("- RED note should visually move when it becomes child of GREEN note\n")
            f.write("- GREEN note should visually move when it becomes child of BLUE note\n")
            f.write("- API location values may remain the same (since they're relative)\n\n")
            
            f.write("**If coordinates are NOT relative to parents:**\n")
            f.write("- Notes should remain in the same visual positions\n")
            f.write("- API location values should remain the same\n\n")
            
            f.write("## Data Files\n\n")
            f.write("- JSON results: `visual_parent_id_test_results_*.json`\n")
            f.write("- CSV results: `visual_parent_id_test_results_*.csv`\n")
            f.write("- Visual snapshots: `visual_snapshots/` directory\n\n")
            
        print(f"✅ Created analysis summary: {summary_filename}")
        
    async def cleanup(self):
        """Clean up test resources"""
        print("🧹 Cleaning up test resources...")
        
        if self.canvas_id:
            try:
                await self.client.delete_canvas(self.canvas_id)
                print(f"✅ Deleted test canvas: {self.canvas_id}")
            except Exception as e:
                print(f"⚠️ Could not delete canvas: {e}")
                
    async def run(self):
        """Run the complete test"""
        try:
            await self.setup()
            await self.run_test_sequence()
            await self.save_results()
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.cleanup()


async def main():
    """Main function"""
    print("🔬 Visual Parent ID Coordinate Transformation Test")
    print("=" * 60)
    
    test = VisualParentIDTest()
    await test.run()
    
    print("\n🎯 Visual test completed!")
    print("📁 Check the generated files and visual_snapshots/ directory for results.")


if __name__ == "__main__":
    asyncio.run(main()) 