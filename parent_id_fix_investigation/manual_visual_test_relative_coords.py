#!/usr/bin/env python3
"""
Manual visual test script for parent ID changes with relative coordinate adjustment.
This test adjusts widget positions relative to their new parent before applying parent changes.
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


class ManualVisualRelativeCoordTest:
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
        """Create three colored notes with randomized positions and sizes"""
        print("📝 Creating colored test notes with randomized positions...")
        
        if not self.canvas_id:
            print("❌ No canvas ID available")
            return
        
        # Import random for reproducible results
        import random
        random.seed(42)  # For reproducible results
        
        # Generate randomized positions
        note1_x = random.randint(500, 1500)
        note1_y = random.randint(500, 1500)
        note2_x = random.randint(1600, 2600)
        note2_y = random.randint(500, 1500)
        note3_x = random.randint(2700, 3700)
        note3_y = random.randint(500, 1500)
        
        # Note 1: Red - Randomized position
        note1_payload = {
            "location": {"x": note1_x, "y": note1_y},
            "size": {"width": 600, "height": 600},
            "scale": 1.0,
            "background_color": "#ff0000"
        }
        note1_data = await self.client.create_note(self.canvas_id, note1_payload)
        self.note_ids.append(note1_data.id)
        print(f"✅ Created RED Note 1: {note1_data.id} at [{note1_x}, {note1_y}] (600x600)")
        
        # Note 2: Green - Randomized position
        note2_payload = {
            "location": {"x": note2_x, "y": note2_y},
            "size": {"width": 600, "height": 600},
            "scale": 1.0,
            "background_color": "#00ff00"
        }
        note2_data = await self.client.create_note(self.canvas_id, note2_payload)
        self.note_ids.append(note2_data.id)
        print(f"✅ Created GREEN Note 2: {note2_data.id} at [{note2_x}, {note2_y}] (600x600)")
        
        # Note 3: Blue - Randomized position
        note3_payload = {
            "location": {"x": note3_x, "y": note3_y},
            "size": {"width": 600, "height": 600},
            "scale": 1.0,
            "background_color": "#0000ff"
        }
        note3_data = await self.client.create_note(self.canvas_id, note3_payload)
        self.note_ids.append(note3_data.id)
        print(f"✅ Created BLUE Note 3: {note3_data.id} at [{note3_x}, {note3_y}] (600x600)")
        
    async def get_widgets_data(self) -> List[Dict[str, Any]]:
        """Get all widgets data from the canvas"""
        if not self.canvas_id:
            return []
        widgets = await self.client.list_widgets(self.canvas_id)
        # Convert Widget objects to dictionaries
        return [widget.model_dump() if hasattr(widget, 'model_dump') else dict(widget) for widget in widgets]
        
    async def get_widget_by_id(self, widget_id: str) -> Dict[str, Any] | None:
        """Get a specific widget by ID"""
        widgets = await self.get_widgets_data()
        for widget in widgets:
            if widget.get("id") == widget_id:
                return widget
        return None
        
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
        
    async def change_parent_id_with_discovered_formula(self, widget_id: str, new_parent_id: str):
        """Change the parent ID of a widget using the discovered formula: -(width) - location - 30"""
        print(f"🔄 Changing parent of {widget_id} to {new_parent_id} using discovered formula")
        
        if not self.canvas_id:
            print("❌ No canvas ID available")
            return None
            
        # Get current widget data
        current_widget = await self.get_widget_by_id(widget_id)
        if not current_widget:
            print(f"❌ Could not find widget {widget_id}")
            return None
            
        # Get new parent widget data
        parent_widget = await self.get_widget_by_id(new_parent_id)
        if not parent_widget:
            print(f"❌ Could not find parent widget {new_parent_id}")
            return None
            
        # Calculate current positions
        current_location = current_widget.get("location", {})
        parent_location = parent_widget.get("location", {})
        parent_size = parent_widget.get("size", {})
        
        current_x = current_location.get("x", 0)
        current_y = current_location.get("y", 0)
        parent_x = parent_location.get("x", 0)
        parent_y = parent_location.get("y", 0)
        parent_width = parent_size.get("width", 100)
        parent_height = parent_size.get("height", 100)
        
        print(f"📊 Position calculation:")
        print(f"  Current widget position: [{current_x}, {current_y}]")
        print(f"  New parent position: [{parent_x}, {parent_y}]")
        print(f"  Parent size: [{parent_width}, {parent_height}]")
        
        # Calculate widget size
        current_size = current_widget.get("size", {})
        current_width = current_size.get("width", 600)
        current_height = current_size.get("height", 600)
        
        # Apply the discovered formula: current_location - parent_location - 30
        calculated_offset_x = current_x - parent_x - 30
        calculated_offset_y = current_y - parent_y - 30
        
        print(f"\n🎯 APPLYING DISCOVERED FORMULA")
        print(f"  Widget position: [{current_x}, {current_y}]")
        print(f"  Parent position: [{parent_x}, {parent_y}]")
        print(f"  Calculated offset: [{calculated_offset_x}, {calculated_offset_y}]")
        print(f"  Formula: current_location - parent_location - 30")
        print(f"  X calculation: {current_x} - {parent_x} - 30 = {calculated_offset_x}")
        print(f"  Y calculation: {current_y} - {parent_y} - 30 = {calculated_offset_y}")
        
        # Update the widget with calculated offset
        update_payload = {
            "parent_id": new_parent_id,
            "location": {"x": calculated_offset_x, "y": calculated_offset_y}
        }
        
        try:
            updated_widget = await self.client.update_note(self.canvas_id, widget_id, update_payload)
            print(f"✅ Successfully applied formula-based offset: [{calculated_offset_x}, {calculated_offset_y}]")
            return updated_widget
        except Exception as e:
            print(f"❌ Error applying formula-based offset: {e}")
            return None
            
    async def wait_for_user_input(self, stage: str):
        """Auto-advance for automated testing"""
        print(f"\n⏱️  Auto-advancing to next stage: {stage}")
        import asyncio
        await asyncio.sleep(2)  # Brief pause for visibility
        print("✅ Continuing to next stage...\n")
            
    async def run_test_sequence(self):
        """Run the complete test sequence automatically"""
        print("🚀 Starting automated visual relative coordinate test sequence...")
        print("This test will run automatically with brief pauses between stages.")
        print("Each parent change includes relative coordinate adjustment.")
        
        # Step 1: Get initial state and wait for snapshot
        print("\n📋 Step 1: Initial widget state")
        widgets = await self.get_widgets_data()
        await self.record_widget_state("INITIAL", widgets)
        await self.wait_for_user_input("INITIAL")
        
        # Step 2: Change Note 1's parent to Note 2 using discovered formula
        print("\n🔄 Step 2: Setting Note 1's parent to Note 2 (using discovered formula)")
        await self.change_parent_id_with_discovered_formula(self.note_ids[0], self.note_ids[1])
        
        # Get state after first change
        widgets = await self.get_widgets_data()
        await self.record_widget_state("NOTE1_TO_NOTE2_FORMULA", widgets)
        await self.wait_for_user_input("NOTE1_TO_NOTE2_FORMULA")
        
        # Step 3: Change Note 2's parent to Note 3 using discovered formula
        print("\n🔄 Step 3: Setting Note 2's parent to Note 3 (using discovered formula)")
        await self.change_parent_id_with_discovered_formula(self.note_ids[1], self.note_ids[2])
        
        # Get state after second change
        widgets = await self.get_widgets_data()
        await self.record_widget_state("NOTE2_TO_NOTE3_FORMULA", widgets)
        await self.wait_for_user_input("NOTE2_TO_NOTE3_FORMULA")
        
        # Step 4: Change Note 3's parent to Note 1 (circular parenting test)
        print("\n🔄 Step 4: Setting Note 3's parent to Note 1 (circular parenting test)")
        await self.change_parent_id_with_discovered_formula(self.note_ids[2], self.note_ids[0])
        
        # Get state after circular parenting change
        widgets = await self.get_widgets_data()
        await self.record_widget_state("NOTE3_TO_NOTE1_CIRCULAR", widgets)
        await self.wait_for_user_input("NOTE3_TO_NOTE1_CIRCULAR")
        
        print("\n✅ Manual relative coordinate test sequence completed!")
        
    async def save_results(self):
        """Save test results to files"""
        print("💾 Saving test results...")
        
        # Save as JSON
        json_filename = f"manual_visual_relative_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_filename, 'w') as f:
            json.dump({
                "test_info": {
                    "canvas_id": self.canvas_id,
                    "note_ids": self.note_ids,
                    "timestamp": datetime.now().isoformat(),
                    "description": "Manual visual parent ID transition test with relative coordinate adjustment",
                    "test_type": "manual_snapshot_relative_coords"
                },
                "test_data": self.test_data
            }, f, indent=2)
        print(f"✅ Saved JSON results to: {json_filename}")
        
        # Save as CSV
        csv_filename = f"manual_visual_relative_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
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
        summary_filename = f"manual_relative_analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(summary_filename, 'w') as f:
            f.write("# Manual Visual Relative Coordinate Test Analysis Summary\n\n")
            f.write(f"**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Canvas ID:** {self.canvas_id}\n")
            f.write(f"**Test Type:** Manual snapshot analysis with relative coordinate adjustment\n\n")
            
            f.write("## Test Setup\n\n")
            f.write("- **RED Note 1:** Initial position [randomized]\n")
            f.write("- **GREEN Note 2:** Initial position [randomized]\n")
            f.write("- **BLUE Note 3:** Initial position [randomized]\n")
            f.write("- **All notes:** 600x600 size, randomized positions for non-cohesive testing\n\n")
            
            f.write("## Test Sequence with Relative Adjustment\n\n")
            f.write("1. **INITIAL:** All notes with background parent\n")
            f.write("2. **NOTE1_TO_NOTE2_FORMULA:** RED note becomes child of GREEN note\n")
            f.write("   - RED note position adjusted using formula: current_location - parent_location - 30\n")
            f.write("3. **NOTE2_TO_NOTE3_FORMULA:** GREEN note becomes child of BLUE note\n")
            f.write("   - GREEN note position adjusted using formula: current_location - parent_location - 30\n")
            f.write("   - RED note (child of GREEN) position remains relative to GREEN\n")
            f.write("4. **NOTE3_TO_NOTE1_CIRCULAR:** BLUE note becomes child of RED note (circular parenting)\n")
            f.write("   - BLUE note position adjusted using formula: current_location - parent_location - 30\n")
            f.write("   - Creates circular reference: RED → GREEN → BLUE → RED\n\n")
            
            f.write("## Manual Analysis Instructions\n\n")
            f.write("Compare your manual screenshots:\n\n")
            f.write("- **INITIAL screenshot** - All notes in original positions\n")
            f.write("- **NOTE1_TO_NOTE2_FORMULA screenshot** - After RED note reparented to GREEN with formula adjustment\n")
            f.write("- **NOTE2_TO_NOTE3_FORMULA screenshot** - After GREEN note reparented to BLUE with formula adjustment\n")
            f.write("- **NOTE3_TO_NOTE1_CIRCULAR screenshot** - After BLUE note reparented to RED (circular parenting)\n\n")
            
            f.write("## Expected Results with Relative Adjustment\n\n")
            f.write("**If the API properly handles relative coordinates:**\n")
            f.write("- RED note should maintain its visual position relative to GREEN note\n")
            f.write("- GREEN note should maintain its visual position relative to BLUE note\n")
            f.write("- The overall visual arrangement should remain stable\n\n")
            
            f.write("**If the API doesn't handle relative coordinates properly:**\n")
            f.write("- Notes may still move or behave unexpectedly\n")
            f.write("- The relative adjustment may not prevent visual shifts\n\n")
            f.write("**Circular Parenting Test:**\n")
            f.write("- Tests if the API handles circular parent-child relationships\n")
            f.write("- May reveal rendering issues or infinite loop prevention\n")
            f.write("- Could show how the system resolves circular references\n\n")
            
            f.write("## Key Differences from Original Test\n\n")
            f.write("- **Original test:** Changed parent_id only, causing visual shifts\n")
            f.write("- **This test:** Calculates relative position and adjusts location before parent change\n")
            f.write("- **Goal:** Determine if relative coordinate adjustment prevents visual movement\n\n")
            
            f.write("## Data Files\n\n")
            f.write("- JSON results: `manual_visual_relative_test_results_*.json`\n")
            f.write("- CSV results: `manual_visual_relative_test_results_*.csv`\n")
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
            
            # Auto-cleanup notes
            print("\n🧹 Auto-cleaning up test notes...")
            await self.cleanup_notes()
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """Main function"""
    print("🔬 Automated Visual Relative Coordinate Parent ID Test")
    print("=" * 70)
    print("This test adjusts widget positions relative to new parents before")
    print("applying parent changes to prevent visual shifts.")
    print("=" * 70)
    
    test = ManualVisualRelativeCoordTest()
    await test.run()
    
    print("\n🎯 Automated relative coordinate test completed!")
    print("📁 Check the generated files for results.")
    print("📊 Analysis will be performed automatically.")


if __name__ == "__main__":
    asyncio.run(main()) 