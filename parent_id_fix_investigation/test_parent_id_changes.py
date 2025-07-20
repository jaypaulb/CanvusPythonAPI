#!/usr/bin/env python3
"""
Test script to investigate parent ID changes between widgets.
This test creates three notes and changes their parent relationships to understand
coordinate transformation behavior.
"""

import asyncio
import json
import csv
from datetime import datetime
from typing import Dict, List, Any
import sys
import os

# Add the parent directory to the path to import the API client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_config import TestClient, get_test_config


class ParentIDTest:
    def __init__(self):
        self.config = get_test_config()
        self.test_data = []
        self.canvas_id = None
        self.note_ids = []

    async def setup(self):
        """Set up the test environment"""
        print("🔧 Setting up test environment...")

        # Create test client and authenticate
        async with TestClient(self.config) as test_client:
            self.client = test_client.client

            # Create a new canvas
            canvas_payload = {
                "name": f"Parent ID Test - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test canvas for parent ID coordinate transformation investigation",
            }
            canvas_data = await self.client.create_canvas(canvas_payload)
            self.canvas_id = canvas_data.id
            print(f"✅ Created test canvas: {self.canvas_id}")

            # Create test notes within the same context
            await self.create_test_notes()

    async def create_test_notes(self):
        """Create three notes with known positions and sizes"""
        print("📝 Creating test notes...")

        if not self.canvas_id:
            print("❌ No canvas ID available")
            return

        # Note 1: Top left
        note1_payload = {
            "text": "Note 1 - Top Left",
            "location": {"x": 100, "y": 100},
            "scale": {"x": 1.0, "y": 1.0},
            "size": {"width": 200, "height": 150},
        }
        note1_data = await self.client.create_note(self.canvas_id, note1_payload)
        self.note_ids.append(note1_data.id)
        print(f"✅ Created Note 1: {note1_data.id} at [100, 100]")

        # Note 2: Center
        note2_payload = {
            "text": "Note 2 - Center",
            "location": {"x": 400, "y": 300},
            "scale": {"x": 1.5, "y": 1.5},
            "size": {"width": 250, "height": 200},
        }
        note2_data = await self.client.create_note(self.canvas_id, note2_payload)
        self.note_ids.append(note2_data.id)
        print(f"✅ Created Note 2: {note2_data.id} at [400, 300]")

        # Note 3: Bottom right
        note3_payload = {
            "text": "Note 3 - Bottom Right",
            "location": {"x": 700, "y": 500},
            "scale": {"x": 0.8, "y": 0.8},
            "size": {"width": 180, "height": 120},
        }
        note3_data = await self.client.create_note(self.canvas_id, note3_payload)
        self.note_ids.append(note3_data.id)
        print(f"✅ Created Note 3: {note3_data.id} at [700, 500]")

    async def get_widgets_data(self) -> List[Dict[str, Any]]:
        """Get all widgets data from the canvas"""
        if not self.canvas_id:
            return []
        widgets = await self.client.list_widgets(self.canvas_id)
        # Convert Widget objects to dictionaries
        return [
            widget.model_dump() if hasattr(widget, "model_dump") else dict(widget)
            for widget in widgets
        ]

    async def record_widget_state(self, stage: str, widgets: List[Dict[str, Any]]):
        """Record the current state of all widgets"""
        print(f"📊 Recording widget state for stage: {stage}")

        for widget in widgets:
            if widget.get("type") == "notes" and widget.get("id") in self.note_ids:
                location = widget.get("location", {})
                scale = widget.get("scale", {})
                size = widget.get("size", {})

                widget_data = {
                    "stage": stage,
                    "timestamp": datetime.now().isoformat(),
                    "widget_id": widget["id"],
                    "content": widget.get("text", ""),
                    "parent_id": widget.get("parent_id"),
                    "location_x": location.get("x", 0),
                    "location_y": location.get("y", 0),
                    "scale_x": scale.get("x", 1),
                    "scale_y": scale.get("y", 1),
                    "size_width": size.get("width", 0),
                    "size_height": size.get("height", 0),
                    "rotation": widget.get("rotation", 0),
                    "z_index": widget.get("z_index", 0),
                }
                self.test_data.append(widget_data)
                print(
                    f"  📝 {widget['id']}: pos=[{widget_data['location_x']}, {widget_data['location_y']}], "
                    f"scale=[{widget_data['scale_x']}, {widget_data['scale_y']}], "
                    f"parent={widget_data['parent_id']}"
                )

    async def change_parent_id(self, widget_id: str, new_parent_id: str):
        """Change the parent ID of a widget"""
        print(f"🔄 Changing parent of {widget_id} to {new_parent_id}")

        if not self.canvas_id:
            print("❌ No canvas ID available")
            return None

        # Update the widget with new parent_id
        update_payload = {"parent_id": new_parent_id}

        try:
            updated_widget = await self.client.update_note(
                self.canvas_id, widget_id, update_payload
            )
            print(f"✅ Successfully updated parent of {widget_id}")
            return updated_widget
        except Exception as e:
            print(f"❌ Error updating parent: {e}")
            return None

    async def run_test_sequence(self):
        """Run the complete test sequence"""
        print("🚀 Starting parent ID test sequence...")

        # Step 1: Get initial state
        print("\n📋 Step 1: Initial widget state")
        widgets = await self.get_widgets_data()
        await self.record_widget_state("INITIAL", widgets)

        # Step 2: Change Note 1's parent to Note 2
        print("\n🔄 Step 2: Setting Note 1's parent to Note 2")
        await self.change_parent_id(self.note_ids[0], self.note_ids[1])

        # Get state after first change
        widgets = await self.get_widgets_data()
        await self.record_widget_state("NOTE1_TO_NOTE2", widgets)

        # Step 3: Change Note 2's parent to Note 3
        print("\n🔄 Step 3: Setting Note 2's parent to Note 3")
        await self.change_parent_id(self.note_ids[1], self.note_ids[2])

        # Get state after second change
        widgets = await self.get_widgets_data()
        await self.record_widget_state("NOTE2_TO_NOTE3", widgets)

        print("\n✅ Test sequence completed!")

    async def save_results(self):
        """Save test results to files"""
        print("💾 Saving test results...")

        # Save as JSON
        json_filename = (
            f"parent_id_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(json_filename, "w") as f:
            json.dump(
                {
                    "test_info": {
                        "canvas_id": self.canvas_id,
                        "note_ids": self.note_ids,
                        "timestamp": datetime.now().isoformat(),
                        "description": "Parent ID transition test with three notes",
                    },
                    "test_data": self.test_data,
                },
                f,
                indent=2,
            )
        print(f"✅ Saved JSON results to: {json_filename}")

        # Save as CSV
        csv_filename = (
            f"parent_id_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        if self.test_data:
            fieldnames = self.test_data[0].keys()
            with open(csv_filename, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.test_data)
        print(f"✅ Saved CSV results to: {csv_filename}")

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
    print("🔬 Parent ID Coordinate Transformation Test")
    print("=" * 50)

    test = ParentIDTest()
    await test.run()

    print("\n🎯 Test completed! Check the generated files for results.")


if __name__ == "__main__":
    asyncio.run(main())
