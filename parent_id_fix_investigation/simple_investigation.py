#!/usr/bin/env python3
"""
Simple Parent ID Widget Position Bug Investigation Script

This script investigates the behavior of widget position changes when parent_id is modified.
It uses direct client connection without TestClient setup to avoid conflicts.
"""

import asyncio
import csv
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import os

# Add the parent directory to the path to import the client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from canvus_api import CanvusClient


class SimpleParentIDInvestigator:
    """Simple investigator class for parent ID widget position bug."""

    def __init__(self):
        # Use test server configuration directly
        self.base_url = "https://canvusserver"
        self.api_key = "wZ5ltFx8Rrs7BKS-UrjlpoHkFv1uIAx-uAjWtPsQ8e0"
        self.client = CanvusClient(self.base_url, self.api_key, verify_ssl=False)
        self.test_data = []
        self.canvas = None
        self.parent_widgets = {}
        self.test_notes = {}

    async def authenticate(self):
        """Authenticate with the server to get a fresh token."""
        print("🔐 Authenticating with server...")
        try:
            # Login with admin credentials
            login_response = await self.client.login("admin@test.local", "loBbR5rOur")
            print(f"✅ Authenticated as: {login_response['user']['email']}")
            # Update the client's API key with the fresh token
            self.client.api_key = login_response["token"]
            return True
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False

    async def setup_test_environment(self):
        """Create test canvas and parent widgets."""
        print("🔧 Setting up test environment...")

        # Create test canvas
        self.canvas = await self.client.create_canvas(
            {
                "name": f"Parent ID Investigation - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test canvas for parent ID bug investigation",
            }
        )
        print(f"✅ Created test canvas: {self.canvas.id}")

        # Create parent widgets at different locations
        parent_locations = [
            {"name": "Parent A", "x": 100, "y": 100, "width": 300, "height": 200},
            {"name": "Parent B", "x": 500, "y": 100, "width": 300, "height": 200},
            {"name": "Parent C", "x": 100, "y": 400, "width": 300, "height": 200},
            {"name": "Parent D", "x": 500, "y": 400, "width": 300, "height": 200},
        ]

        for i, parent_info in enumerate(parent_locations):
            parent = await self.client.create_note(
                self.canvas.id,
                {
                    "content": parent_info["name"],
                    "location": {"x": parent_info["x"], "y": parent_info["y"]},
                    "size": {
                        "width": parent_info["width"],
                        "height": parent_info["height"],
                    },
                },
            )
            self.parent_widgets[parent_info["name"]] = parent
            print(f"✅ Created {parent_info['name']}: {parent.id}")

        # Create a nested parent (child of Parent A)
        if "Parent A" in self.parent_widgets:
            nested_parent = await self.client.create_note(
                self.canvas.id,
                {
                    "content": "Nested Parent",
                    "location": {"x": 50, "y": 50},
                    "size": {"width": 200, "height": 100},
                    "parent_id": self.parent_widgets["Parent A"].id,
                },
            )
            self.parent_widgets["Nested Parent"] = nested_parent
            print(f"✅ Created Nested Parent: {nested_parent.id}")

    async def create_test_notes(self):
        """Create test notes at specific locations."""
        print("📝 Creating test notes...")

        # Test note locations (relative to canvas)
        test_locations = [
            {"name": "Root Note 1", "x": 200, "y": 200, "parent_id": None},
            {"name": "Root Note 2", "x": 600, "y": 200, "parent_id": None},
            {"name": "Root Note 3", "x": 200, "y": 500, "parent_id": None},
            {"name": "Root Note 4", "x": 600, "y": 500, "parent_id": None},
        ]

        for note_info in test_locations:
            note = await self.client.create_note(
                self.canvas.id,
                {
                    "content": note_info["name"],
                    "location": {"x": note_info["x"], "y": note_info["y"]},
                    "size": {"width": 150, "height": 100},
                    "parent_id": note_info["parent_id"],
                },
            )
            self.test_notes[note_info["name"]] = note
            print(f"✅ Created {note_info['name']}: {note.id}")

    async def record_widget_state(
        self, widget_id: str, description: str
    ) -> Dict[str, Any]:
        """Record the current state of a widget."""
        widget = await self.client.get_widget(self.canvas.id, widget_id)
        return {
            "description": description,
            "widget_id": widget_id,
            "parent_id": widget.parent_id,
            "loc": widget.location,
            "scale": widget.scale,
            "x": widget.location["x"],
            "y": widget.location["y"],
            "width": widget.size["width"],
            "height": widget.size["height"],
            "timestamp": datetime.now().isoformat(),
        }

    async def change_parent_and_record(
        self, widget_id: str, new_parent_id: Optional[str], test_id: str
    ):
        """Change parent_id and record before/after states."""
        print(f"🔄 Testing {test_id}: Changing parent_id to {new_parent_id}")

        # Record initial state
        initial_state = await self.record_widget_state(
            widget_id, f"{test_id} - Initial"
        )

        # Change parent_id
        updated_widget = await self.client.update_note(
            self.canvas.id, widget_id, {"parent_id": new_parent_id}
        )

        # Record final state
        final_state = await self.record_widget_state(widget_id, f"{test_id} - Final")

        # Calculate changes
        loc_change = [
            final_state["loc"]["x"] - initial_state["loc"]["x"],
            final_state["loc"]["y"] - initial_state["loc"]["y"],
        ]
        scale_change = [
            final_state["scale"] - initial_state["scale"],
            final_state["scale"] - initial_state["scale"],  # Scale is a single value
        ]

        # Store test data
        test_record = {
            "test_id": test_id,
            "widget_id": widget_id,
            "initial_parent_id": initial_state["parent_id"],
            "final_parent_id": final_state["parent_id"],
            "initial_loc": initial_state["loc"],
            "final_loc": final_state["loc"],
            "initial_scale": initial_state["scale"],
            "final_scale": final_state["scale"],
            "loc_change": loc_change,
            "scale_change": scale_change,
            "initial_x": initial_state["x"],
            "initial_y": initial_state["y"],
            "final_x": final_state["x"],
            "final_y": final_state["y"],
            "x_change": final_state["x"] - initial_state["x"],
            "y_change": final_state["y"] - initial_state["y"],
            "timestamp": datetime.now().isoformat(),
        }

        self.test_data.append(test_record)
        print(f"✅ Recorded data for {test_id}")

        return test_record

    async def run_test_scenarios(self):
        """Run all test scenarios."""
        print("🧪 Running test scenarios...")

        # Scenario 1: Root to Parent
        for i, (note_name, note) in enumerate(self.test_notes.items()):
            if note and note.parent_id is None:  # Only test root notes
                parent_a = self.parent_widgets.get("Parent A")
                if parent_a:
                    await self.change_parent_and_record(
                        note.id, parent_a.id, f"T001_{i+1}_RootToParent"
                    )

        # Scenario 2: Parent to Parent
        for i, (note_name, note) in enumerate(self.test_notes.items()):
            if note and note.parent_id == self.parent_widgets["Parent A"].id:
                parent_b = self.parent_widgets["Parent B"]
                await self.change_parent_and_record(
                    note.id, parent_b.id, f"T002_{i+1}_ParentToParent"
                )

        # Scenario 3: Parent to Root
        for i, (note_name, note) in enumerate(self.test_notes.items()):
            if note and note.parent_id is not None:
                await self.change_parent_and_record(
                    note.id, None, f"T003_{i+1}_ParentToRoot"
                )

        # Scenario 4: Nested Hierarchy
        for i, (note_name, note) in enumerate(self.test_notes.items()):
            if note and note.parent_id == self.parent_widgets["Parent A"].id:
                nested_parent = self.parent_widgets["Nested Parent"]
                await self.change_parent_and_record(
                    note.id, nested_parent.id, f"T004_{i+1}_NestedHierarchy"
                )

    def save_results(self):
        """Save investigation results to files."""
        print("💾 Saving results...")

        # Save as CSV
        csv_filename = "simple_data_collection_results.csv"
        with open(csv_filename, "w", newline="") as csvfile:
            fieldnames = [
                "test_id",
                "widget_id",
                "initial_parent_id",
                "final_parent_id",
                "initial_loc_x",
                "initial_loc_y",
                "final_loc_x",
                "final_loc_y",
                "initial_scale_x",
                "initial_scale_y",
                "final_scale_x",
                "final_scale_y",
                "loc_change_x",
                "loc_change_y",
                "scale_change_x",
                "scale_change_y",
                "initial_x",
                "initial_y",
                "final_x",
                "final_y",
                "x_change",
                "y_change",
                "timestamp",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for record in self.test_data:
                writer.writerow(
                    {
                        "test_id": record["test_id"],
                        "widget_id": record["widget_id"],
                        "initial_parent_id": record["initial_parent_id"],
                        "final_parent_id": record["final_parent_id"],
                        "initial_loc_x": record["initial_loc"]["x"],
                        "initial_loc_y": record["initial_loc"]["y"],
                        "final_loc_x": record["final_loc"]["x"],
                        "final_loc_y": record["final_loc"]["y"],
                        "initial_scale_x": record["initial_scale"],
                        "initial_scale_y": record["initial_scale"],
                        "final_scale_x": record["final_scale"],
                        "final_scale_y": record["final_scale"],
                        "loc_change_x": record["loc_change"][0],
                        "loc_change_y": record["loc_change"][1],
                        "scale_change_x": record["scale_change"][0],
                        "scale_change_y": record["scale_change"][1],
                        "initial_x": record["initial_x"],
                        "initial_y": record["initial_y"],
                        "final_x": record["final_x"],
                        "final_y": record["final_y"],
                        "x_change": record["x_change"],
                        "y_change": record["y_change"],
                        "timestamp": record["timestamp"],
                    }
                )

        # Save as JSON for detailed analysis
        json_filename = "simple_data_collection_results.json"
        with open(json_filename, "w") as jsonfile:
            json.dump(
                {
                    "canvas_id": self.canvas.id if self.canvas else None,
                    "parent_widgets": {
                        name: widget.id for name, widget in self.parent_widgets.items()
                    },
                    "test_notes": {
                        name: note.id for name, note in self.test_notes.items()
                    },
                    "test_data": self.test_data,
                    "investigation_date": datetime.now().isoformat(),
                },
                jsonfile,
                indent=2,
            )

        print(f"✅ Saved results to {csv_filename} and {json_filename}")
        print(f"📊 Collected {len(self.test_data)} test records")

    async def cleanup(self):
        """Clean up test canvas."""
        if self.canvas:
            print(f"🧹 Cleaning up test canvas: {self.canvas.id}")
            await self.client.delete_canvas(self.canvas.id)
            print("✅ Test canvas deleted")


async def main():
    """Main investigation function."""
    print("🔍 Starting Simple Parent ID Widget Position Bug Investigation")
    print("=" * 70)

    investigator = SimpleParentIDInvestigator()

    try:
        # Authenticate
        await investigator.authenticate()

        # Setup test environment
        await investigator.setup_test_environment()

        # Create test notes
        await investigator.create_test_notes()

        # Run test scenarios
        await investigator.run_test_scenarios()

        # Save results
        investigator.save_results()

        print("\n🎉 Investigation completed successfully!")
        print("📁 Check the generated files for detailed results:")
        print("   - simple_data_collection_results.csv")
        print("   - simple_data_collection_results.json")

    except Exception as e:
        print(f"❌ Investigation failed: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # Cleanup
        await investigator.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
