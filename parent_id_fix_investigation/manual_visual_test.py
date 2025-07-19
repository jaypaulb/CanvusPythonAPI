#!/usr/bin/env python3
"""
Manual visual test script for parent ID changes using existing canvas.
This test uses a pre-existing canvas and waits for manual input after each stage
so the user can take manual snapshots.
"""

import asyncio
import json
import csv
import os
from datetime import datetime
from typing import Dict, List, Any
import sys
from pathlib import Path

# Add the parent directory to the path to import the API client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_config import TestClient, get_test_config


class ManualVisualParentIDTest:
    def __init__(self):
        self.config = get_test_config()
        self.test_data = []
        self.canvas_id = "30b6d41a-05bf-4e41-b002-9d85ea295fa4"  # Use existing canvas
        self.note_ids = []
        
    async def setup(self):
        """Set up the test environment"""
        print("🔧 Setting up test environment...")
        print(f"📋 Using existing canvas: {self.canvas_id}")
        
        # Create test client and authenticate
        async with TestClient(self.config) as test_client:
            self.client = test_client.client
            
            # Get existing canvas info
            try:
                canvas_info = await self.client.get_canvas(self.canvas_id)
                print(f"✅ Found canvas: {canvas_info.name}")
            except Exception as e:
                print(f"❌ Error accessing canvas: {e}")
                return False
                
            # Create test notes within the same context
            await self.create_test_notes()
            return True
        
    async def create_test_notes(self):
        """Create three colored notes with known positions and sizes"""
        print("📝 Creating colored test notes...")
        
        if not self.canvas_id:
            print("❌ No canvas ID available")
            return
        
        # Note 1: Red - Starting position
        note1_payload = {
            "location": {"x": 1000, "y": 1000},
            "size": {"width": 100, "height": 100},
            "scale": 1.0,
            "background_color": "#ff0000"
        }
        note1_data = await self.client.create_note(self.canvas_id, note1_payload)
        self.note_ids.append(note1_data.id)
        print(f"✅ Created RED Note 1: {note1_data.id} at [1000, 1000]")
        
        # Note 2: Green - 100 units to the right
        note2_payload = {
            "location": {"x": 1100, "y": 1000},
            "size": {"width": 100, "height": 100},
            "scale": 1.0,
            "background_color": "#00ff00"
        }
        note2_data = await self.client.create_note(self.canvas_id, note2_payload)
        self.note_ids.append(note2_data.id)
        print(f"✅ Created GREEN Note 2: {note2_data.id} at [1100, 1000]")
        
        # Note 3: Blue - 200 units to the right
        note3_payload = {
            "location": {"x": 1200, "y": 1000},
            "size": {"width": 100, "height": 100},
            "scale": 1.0,
            "background_color": "#0000ff"
        }
        note3_data = await self.client.create_note(self.canvas_id, note3_payload)
        self.note_ids.append(note3_data.id)
        print(f"✅ Created BLUE Note 3: {note3_data.id} at [1200, 1000]")
        
    async def get_widgets_data(self) -> List[Dict[str, Any]]:
        """Get all widgets data from the canvas"""
        if not self.canvas_id:
            return []
        widgets = await self.client.list_widgets(self.canvas_id)
        # Convert Widget objects to dictionaries
        return [widget.model_dump() if hasattr(widget, 'model_dump') else dict(widget) for widget in widgets]
        
    async def record_widget_state(self, stage: str, widgets: List[Dict[str, Any]]):
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
                    "background_color": widget.get("background_color", "")
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
            
    async def wait_for_user_input(self, stage: str):
        """Wait for user to take manual snapshot"""
        print(f"\n📸 MANUAL SNAPSHOT REQUIRED for stage: {stage}")
        print("=" * 60)
        print("Please:")
        print("1. Open the canvas in your browser")
        print("2. Take a screenshot of the current state")
        print("3. Save it with a descriptive name")
        print("4. Press Enter when ready to continue...")
        print("=" * 60)
        
        input("Press Enter to continue to the next stage...")
        print("✅ Continuing to next stage...\n")
            
    async def run_test_sequence(self):
        """Run the complete test sequence with manual input"""
        print("🚀 Starting manual visual parent ID test sequence...")
        print("This test will pause after each stage for manual snapshots.")
        
        # Step 1: Get initial state and wait for snapshot
        print("\n📋 Step 1: Initial widget state")
        widgets = await self.get_widgets_data()
        await self.record_widget_state("INITIAL", widgets)
        await self.wait_for_user_input("INITIAL")
        
        # Step 2: Change Note 1's parent to Note 2 and wait for snapshot
        print("\n🔄 Step 2: Setting Note 1's parent to Note 2")
        await self.change_parent_id(self.note_ids[0], self.note_ids[1])
        
        # Get state after first change
        widgets = await self.get_widgets_data()
        await self.record_widget_state("NOTE1_TO_NOTE2", widgets)
        await self.wait_for_user_input("NOTE1_TO_NOTE2")
        
        # Step 3: Change Note 2's parent to Note 3 and wait for snapshot
        print("\n🔄 Step 3: Setting Note 2's parent to Note 3")
        await self.change_parent_id(self.note_ids[1], self.note_ids[2])
        
        # Get state after second change
        widgets = await self.get_widgets_data()
        await self.record_widget_state("NOTE2_TO_NOTE3", widgets)
        await self.wait_for_user_input("NOTE2_TO_NOTE3")
        
        print("\n✅ Manual test sequence completed!")
        
    async def save_results(self):
        """Save test results to files"""
        print("💾 Saving test results...")
        
        # Save as JSON
        json_filename = f"manual_visual_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_filename, 'w') as f:
            json.dump({
                "test_info": {
                    "canvas_id": self.canvas_id,
                    "note_ids": self.note_ids,
                    "timestamp": datetime.now().isoformat(),
                    "description": "Manual visual parent ID transition test with colored notes",
                    "test_type": "manual_snapshot"
                },
                "test_data": self.test_data
            }, f, indent=2)
        print(f"✅ Saved JSON results to: {json_filename}")
        
        # Save as CSV
        csv_filename = f"manual_visual_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
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
        """Create a summary of the manual analysis"""
        summary_filename = f"manual_analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(summary_filename, 'w') as f:
            f.write("# Manual Visual Parent ID Test Analysis Summary\n\n")
            f.write(f"**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Canvas ID:** {self.canvas_id}\n")
            f.write(f"**Test Type:** Manual snapshot analysis\n\n")
            
            f.write("## Test Setup\n\n")
            f.write("- **RED Note 1:** Initial position [1000, 1000]\n")
            f.write("- **GREEN Note 2:** Initial position [1100, 1000]\n")
            f.write("- **BLUE Note 3:** Initial position [1200, 1000]\n\n")
            
            f.write("## Test Sequence\n\n")
            f.write("1. **INITIAL:** All notes with background parent\n")
            f.write("2. **NOTE1_TO_NOTE2:** RED note becomes child of GREEN note\n")
            f.write("3. **NOTE2_TO_NOTE3:** GREEN note becomes child of BLUE note\n\n")
            
            f.write("## Manual Analysis Instructions\n\n")
            f.write("Compare your manual screenshots:\n\n")
            f.write("- **INITIAL screenshot** - All notes in original positions\n")
            f.write("- **NOTE1_TO_NOTE2 screenshot** - After RED note reparented to GREEN\n")
            f.write("- **NOTE2_TO_NOTE3 screenshot** - After GREEN note reparented to BLUE\n\n")
            
            f.write("## Expected Results\n\n")
            f.write("**If coordinates ARE relative to parents:**\n")
            f.write("- RED note should visually move when it becomes child of GREEN note\n")
            f.write("- GREEN note should visually move when it becomes child of BLUE note\n")
            f.write("- API location values may remain the same (since they're relative)\n\n")
            
            f.write("**If coordinates are NOT relative to parents:**\n")
            f.write("- Notes should remain in the same visual positions\n")
            f.write("- API location values should remain the same\n\n")
            
            f.write("## Data Files\n\n")
            f.write("- JSON results: `manual_visual_test_results_*.json`\n")
            f.write("- CSV results: `manual_visual_test_results_*.csv`\n")
            f.write("- Manual screenshots: Your saved screenshots\n\n")
            
        print(f"✅ Created analysis summary: {summary_filename}")
        
    async def cleanup_notes(self):
        """Clean up test notes (optional)"""
        print("🧹 Cleaning up test notes...")
        
        if not self.canvas_id or not self.note_ids:
            return
            
        for note_id in self.note_ids:
            try:
                await self.client.delete_note(self.canvas_id, note_id)
                print(f"✅ Deleted test note: {note_id}")
            except Exception as e:
                print(f"⚠️ Could not delete note {note_id}: {e}")
                
    async def run(self):
        """Run the complete test"""
        try:
            success = await self.setup()
            if not success:
                print("❌ Setup failed, aborting test")
                return
                
            await self.run_test_sequence()
            await self.save_results()
            
            # Ask user if they want to clean up notes
            print("\n🧹 Cleanup Options:")
            print("1. Keep test notes for further analysis")
            print("2. Delete test notes")
            choice = input("Enter choice (1 or 2): ").strip()
            
            if choice == "2":
                await self.cleanup_notes()
            else:
                print("✅ Test notes preserved for further analysis")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """Main function"""
    print("🔬 Manual Visual Parent ID Coordinate Transformation Test")
    print("=" * 70)
    print("This test will pause after each stage for manual snapshots.")
    print("Please have your browser ready to view the canvas.")
    print("=" * 70)
    
    test = ManualVisualParentIDTest()
    await test.run()
    
    print("\n🎯 Manual test completed!")
    print("📁 Check the generated files for results.")
    print("📸 Compare your manual screenshots to analyze visual changes.")


if __name__ == "__main__":
    asyncio.run(main()) 