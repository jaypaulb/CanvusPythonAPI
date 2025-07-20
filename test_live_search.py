#!/usr/bin/env python3
"""Live server test for cross-canvas search functionality."""

import asyncio
from tests.test_config import TestClient, TestConfig
from canvus_api.search import CrossCanvasSearch, find_widgets_by_type
from canvus_api.geometry import Rectangle


async def test_live_search():
    """Test cross-canvas search with live server."""
    
    print("🚀 Starting focused live server cross-canvas search tests...")
    
    # Create test configuration
    config = TestConfig('tests/test_config.json')
    
    # Target canvas ID
    canvas_id = '30b6d41a-05bf-4e41-b002-9d85ea295fa4'
    print(f"📋 Using canvas: {canvas_id}")
    
    # Use async context manager to properly initialize the client session
    async with TestClient(config) as test_client:
        client = test_client.client
        
        try:
            # Step 1: Create specific target notes with known properties
            print("\n📝 Creating target notes for search testing...")
            
            # Note 1: Specific title and background color
            note1_payload = {
                "title": "SEARCH_TARGET_RED_NOTE",
                "text": "This is a red note for testing search functionality",
                "background_color": "#FF0000",
                "location": {"x": 100, "y": 100},
                "size": {"width": 200, "height": 150}
            }
            note1 = await client.create_note(canvas_id, note1_payload)
            print(f"✅ Created Note 1: {note1.title} (ID: {note1.id})")
            
            # Note 2: Specific title and different background color
            note2_payload = {
                "title": "SEARCH_TARGET_BLUE_NOTE", 
                "text": "This is a blue note with different content for testing",
                "background_color": "#0000FF",
                "location": {"x": 350, "y": 100},
                "size": {"width": 200, "height": 150}
            }
            note2 = await client.create_note(canvas_id, note2_payload)
            print(f"✅ Created Note 2: {note2.title} (ID: {note2.id})")
            
            # Note 3: Specific title and text content
            note3_payload = {
                "title": "SEARCH_TARGET_TEXT_NOTE",
                "text": "This note contains the word UNIQUE_TEXT_PATTERN for testing text search",
                "background_color": "#00FF00",
                "location": {"x": 100, "y": 300},
                "size": {"width": 200, "height": 150}
            }
            note3 = await client.create_note(canvas_id, note3_payload)
            print(f"✅ Created Note 3: {note3.title} (ID: {note3.id})")
            
            # Note 4: Specific location for spatial search
            note4_payload = {
                "title": "SEARCH_TARGET_SPATIAL_NOTE",
                "text": "This note is positioned at a specific location for spatial search testing",
                "background_color": "#FFFF00",
                "location": {"x": 500, "y": 300},
                "size": {"width": 200, "height": 150}
            }
            note4 = await client.create_note(canvas_id, note4_payload)
            print(f"✅ Created Note 4: {note4.title} (ID: {note4.id})")
            
            # Wait a moment for the notes to be fully created
            await asyncio.sleep(2)
            
            # Step 2: Test individual search criteria
            print("\n🔍 Testing individual search criteria...")
            
            # Initialize search
            search = CrossCanvasSearch(client)
            
            # Test 1: Search by exact title
            print("\n📋 Test 1: Search by exact title")
            results = await search.find_widgets_across_canvases(
                {'title': 'SEARCH_TARGET_RED_NOTE'},
                widget_types=['note']
            )
            print(f"Found {len(results)} widgets with title 'SEARCH_TARGET_RED_NOTE'")
            for result in results:
                widget_data = result.widget.model_dump() if hasattr(result.widget, 'model_dump') else dict(result.widget)
                title = widget_data.get('title', 'No title')
                print(f"  - {title} (Canvas: {result.canvas_name})")
            
            # Test 2: Search by background color
            print("\n📋 Test 2: Search by background color")
            results = await search.find_widgets_across_canvases(
                {'background_color': '#FF0000'},
                widget_types=['note']
            )
            print(f"Found {len(results)} widgets with red background")
            for result in results:
                widget_data = result.widget.model_dump() if hasattr(result.widget, 'model_dump') else dict(result.widget)
                title = widget_data.get('title', 'No title')
                print(f"  - {title} (Canvas: {result.canvas_name})")
            
            # Test 3: Search by text content (fuzzy match)
            print("\n📋 Test 3: Search by text content (fuzzy match)")
            results = await search.find_widgets_across_canvases(
                {'text': 'UNIQUE_TEXT_PATTERN'},
                widget_types=['note']
            )
            print(f"Found {len(results)} widgets containing 'UNIQUE_TEXT_PATTERN'")
            for result in results:
                widget_data = result.widget.model_dump() if hasattr(result.widget, 'model_dump') else dict(result.widget)
                title = widget_data.get('title', 'No title')
                print(f"  - {title} (Canvas: {result.canvas_name})")
            
            # Test 4: Search by location (spatial)
            print("\n📋 Test 4: Search by location (spatial)")
            results = await search.find_widgets_across_canvases(
                {'location.x': 500},
                widget_types=['note']
            )
            print(f"Found {len(results)} widgets at x=500")
            for result in results:
                widget_data = result.widget.model_dump() if hasattr(result.widget, 'model_dump') else dict(result.widget)
                title = widget_data.get('title', 'No title')
                print(f"  - {title} (Canvas: {result.canvas_name})")
            
            # Test 5: Search by size
            print("\n📋 Test 5: Search by size")
            results = await search.find_widgets_across_canvases(
                {'size.width': 200},
                widget_types=['note']
            )
            print(f"Found {len(results)} widgets with width=200")
            for result in results:
                widget_data = result.widget.model_dump() if hasattr(result.widget, 'model_dump') else dict(result.widget)
                title = widget_data.get('title', 'No title')
                print(f"  - {title} (Canvas: {result.canvas_name})")
            
            # Test 6: Search by partial title (wildcard)
            print("\n📋 Test 6: Search by partial title (wildcard)")
            results = await search.find_widgets_across_canvases(
                {'title': 'SEARCH_TARGET_*'},
                widget_types=['note']
            )
            print(f"Found {len(results)} widgets with title matching 'SEARCH_TARGET_*'")
            for result in results:
                widget_data = result.widget.model_dump() if hasattr(result.widget, 'model_dump') else dict(result.widget)
                title = widget_data.get('title', 'No title')
                print(f"  - {title} (Canvas: {result.canvas_name})")
            
            # Test 7: Search by multiple criteria
            print("\n📋 Test 7: Search by multiple criteria")
            results = await search.find_widgets_across_canvases(
                {
                    'background_color': '#0000FF',
                    'size.height': 150
                },
                widget_types=['note']
            )
            print(f"Found {len(results)} widgets with blue background and height=150")
            for result in results:
                widget_data = result.widget.model_dump() if hasattr(result.widget, 'model_dump') else dict(result.widget)
                title = widget_data.get('title', 'No title')
                print(f"  - {title} (Canvas: {result.canvas_name})")
            
            # Test 8: Search in specific area
            print("\n📋 Test 8: Search in specific area")
            area = Rectangle(x=400, y=200, width=300, height=300)
            results = await search.find_widgets_in_area(
                area=area,
                widget_types=['note']
            )
            print(f"Found {len(results)} widgets in the specified area")
            for result in results:
                widget_data = result.widget.model_dump() if hasattr(result.widget, 'model_dump') else dict(result.widget)
                title = widget_data.get('title', 'No title')
                print(f"  - {title} (Canvas: {result.canvas_name})")
            
            # Test 9: Use convenience function
            print("\n📋 Test 9: Use convenience function")
            results = await find_widgets_by_type(client, 'note')
            print(f"Found {len(results)} widgets using convenience function")
            for result in results:
                widget_data = result.widget.model_dump() if hasattr(result.widget, 'model_dump') else dict(result.widget)
                title = widget_data.get('title', 'No title')
                print(f"  - {title} (Canvas: {result.canvas_name})")
            
            print("\n✅ All individual search criteria tests completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during live search test: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_live_search()) 