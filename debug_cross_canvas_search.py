#!/usr/bin/env python3
"""Debug script to investigate cross-canvas search issues."""

import asyncio
import json
from tests.test_config import TestClient, TestConfig
from canvus_api.search import CrossCanvasSearch


async def debug_cross_canvas_search():
    """Debug cross-canvas search functionality."""
    
    print("🔍 Debugging cross-canvas search...")
    
    # Create test configuration
    config = TestConfig('tests/test_config.json')
    
    # Target canvas ID
    canvas_id = '30b6d41a-05bf-4e41-b002-9d85ea295fa4'
    print(f"📋 Target canvas: {canvas_id}")
    
    # Use async context manager
    async with TestClient(config) as test_client:
        client = test_client.client
        
        try:
            # Step 1: Get canvas info
            canvas = await client.get_canvas(canvas_id)
            print(f"✅ Canvas: {canvas.name} (ID: {canvas.id})")
            
            # Step 2: Get all widgets in the canvas
            widgets = await client.list_widgets(canvas_id)
            print(f"📋 Total widgets in canvas: {len(widgets)}")
            
            # Step 3: Find note widgets specifically
            note_widgets = [w for w in widgets if w.widget_type == 'Note']
            print(f"📝 Note widgets found: {len(note_widgets)}")
            
            for i, note in enumerate(note_widgets):
                print(f"   Note {i+1}: ID={note.id}, Title='{getattr(note, 'title', 'N/A')}', Location={getattr(note, 'location', 'N/A')}")
            
            # Step 4: Test search engine directly
            search_engine = CrossCanvasSearch(client)
            
            print("\n🔍 Testing search engine...")
            
            # Test 1: Search for notes in the specific canvas
            print("\n1️⃣ Testing find_widgets_by_type for notes in specific canvas...")
            results = await search_engine.find_widgets_by_type('note', [canvas_id], max_results=10)
            print(f"   Search engine found {len(results)} note widgets:")
            for result in results:
                print(f"   - {result.drill_down_path}: {result.canvas_name}")
                print(f"     Widget ID: {result.widget_id}, Type: {result.widget_type}")
            
            # Test 2: Get all canvases and search across them
            print("\n2️⃣ Getting all canvases...")
            all_canvases = await client.list_canvases()
            print(f"   Total canvases available: {len(all_canvases)}")
            
            # Show first few canvases
            for i, c in enumerate(all_canvases[:5]):
                print(f"   Canvas {i+1}: {c.name} (ID: {c.id})")
            
            # Test 3: Search across first 3 canvases
            canvas_ids = [c.id for c in all_canvases[:3]]
            print(f"\n3️⃣ Searching across {len(canvas_ids)} canvases: {canvas_ids}")
            
            results = await search_engine.find_widgets_by_type('note', canvas_ids, max_results=20)
            print(f"   Cross-canvas search found {len(results)} note widgets:")
            for result in results:
                print(f"   - {result.drill_down_path}: {result.canvas_name}")
                print(f"     Widget ID: {result.widget_id}, Type: {result.widget_type}")
            
            # Test 4: Debug the search process step by step
            print("\n4️⃣ Debugging search process...")
            for canvas_id in canvas_ids:
                print(f"\n   Checking canvas: {canvas_id}")
                try:
                    canvas_obj = await client.get_canvas(canvas_id)
                    print(f"     Canvas name: {canvas_obj.name}")
                    
                    widgets_in_canvas = await client.list_widgets(canvas_id)
                    print(f"     Total widgets: {len(widgets_in_canvas)}")
                    
                    note_widgets_in_canvas = [w for w in widgets_in_canvas if w.widget_type == 'Note']
                    print(f"     Note widgets: {len(note_widgets_in_canvas)}")
                    
                    for note in note_widgets_in_canvas:
                        print(f"       Note: {note.id} - '{getattr(note, 'title', 'N/A')}'")
                        
                except Exception as e:
                    print(f"     Error: {e}")
            
            print("\n✅ Debug complete!")
            
        except Exception as e:
            print(f"❌ Error during debug: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_cross_canvas_search()) 