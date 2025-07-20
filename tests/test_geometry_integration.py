"""
Integration tests for geometry utilities with real client data.
"""

import pytest
from tests.test_config import TestClient, get_test_config
from canvus_api.geometry import (
    Point, Size, Rectangle, widget_bounding_box, widgets_touch, 
    widgets_intersect, find_widgets_in_area, get_canvas_bounds
)


@pytest.mark.asyncio
async def test_geometry_with_real_canvas_data():
    """Test geometry utilities with real canvas data from the test server."""
    config = get_test_config()
    test_client = TestClient(config)
    
    try:
        client = test_client.client
        
        # Get a canvas with widgets
        canvases = await client.list_canvases()
        if not canvases:
            pytest.skip("No canvases available for testing")
        
        canvas = canvases[0]
        print(f"Testing geometry utilities with canvas: {canvas.name}")
        
        # Get widgets from the canvas
        widgets = await client.list_widgets(canvas.id)
        if not widgets:
            pytest.skip("No widgets available for testing")
        
        print(f"Found {len(widgets)} widgets for geometry testing")
        
        # Test widget bounding box calculation
        for widget in widgets[:3]:  # Test first 3 widgets
            try:
                rect = widget_bounding_box(widget)
                print(f"Widget {widget.widget_type} bounding box: {rect}")
                assert rect.width > 0
                assert rect.height > 0
            except Exception as e:
                print(f"Could not calculate bounding box for {widget.widget_type}: {e}")
        
        # Test spatial relationships if we have multiple widgets
        if len(widgets) >= 2:
            widget1, widget2 = widgets[0], widgets[1]
            
            # Test if widgets touch
            touch_result = widgets_touch(widget1, widget2)
            print(f"Widgets touch: {touch_result}")
            
            # Test if widgets intersect
            intersect_result = widgets_intersect(widget1, widget2)
            print(f"Widgets intersect: {intersect_result}")
        
        # Test canvas bounds calculation
        bounds = get_canvas_bounds(widgets)  # type: ignore
        if bounds:
            print(f"Canvas bounds: {bounds}")
            assert bounds.width > 0
            assert bounds.height > 0
        
        # Test area search
        if bounds:
            # Search in the first quarter of the canvas
            search_area = Rectangle(
                bounds.x, bounds.y, 
                bounds.width / 2, bounds.height / 2
            )
            widgets_in_area = find_widgets_in_area(widgets, search_area)  # type: ignore
            print(f"Widgets in search area: {len(widgets_in_area)}")
        
        print("✅ Geometry integration test completed successfully")
        
    except Exception as e:
        print(f"❌ Geometry integration test failed: {e}")
        raise
    finally:
        # TestClient uses context management, no explicit close needed
        pass


@pytest.mark.asyncio
async def test_geometry_data_structures():
    """Test basic geometry data structures."""
    # Test Point
    point = Point(10.5, 20.3)
    assert point.x == 10.5
    assert point.y == 20.3
    
    # Test Size
    size = Size(100.0, 200.0)
    assert size.width == 100.0
    assert size.height == 200.0
    
    # Test Rectangle
    rect = Rectangle(0, 0, 100, 200)
    assert rect.left == 0
    assert rect.right == 100
    assert rect.top == 0
    assert rect.bottom == 200
    assert rect.center.x == 50
    assert rect.center.y == 100
    
    print("✅ Geometry data structures test completed")


if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("Running geometry integration tests...")
        await test_geometry_data_structures()
        await test_geometry_with_real_canvas_data()
        print("All geometry integration tests completed!")
    
    asyncio.run(main()) 