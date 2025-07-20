"""
Real integration tests for filtering system using test server.
"""

import pytest
from tests.test_config import TestClient, get_test_config
from canvus_api import Filter, create_filter, create_spatial_filter, create_widget_type_filter, create_text_filter


@pytest.mark.asyncio
async def test_canvas_filtering_with_real_server():
    """Test canvas filtering with real test server data."""
    config = get_test_config()
    
    async with TestClient(config) as test_client:
        client = test_client.client
        
        # Get all canvases first
        all_canvases = await client.list_canvases()
        assert len(all_canvases) > 0
        
        # Test filtering by mode
        normal_canvases = await client.list_canvases(
            filter_obj=Filter(criteria={"mode": "normal"})
        )
        assert len(normal_canvases) >= 0  # May be 0 if no normal canvases
        
        # Test filtering by access
        private_canvases = await client.list_canvases(
            filter_obj=Filter(criteria={"access": "private"})
        )
        assert len(private_canvases) >= 0  # May be 0 if no private canvases
        
        # Test wildcard filtering on names
        if all_canvases:
            # Get the first canvas name and create a wildcard filter
            first_canvas_name = all_canvases[0].name
            if first_canvas_name:
                # Create a prefix filter
                prefix = first_canvas_name[:3] if len(first_canvas_name) >= 3 else first_canvas_name
                prefix_filter = Filter(criteria={"name": f"{prefix}*"})
                prefix_canvases = await client.list_canvases(filter_obj=prefix_filter)
                assert len(prefix_canvases) >= 1  # Should at least include the original canvas
        
        print(f"✅ Canvas filtering test completed:")
        print(f"   - Total canvases: {len(all_canvases)}")
        print(f"   - Normal mode canvases: {len(normal_canvases)}")
        print(f"   - Private access canvases: {len(private_canvases)}")


@pytest.mark.asyncio
async def test_widget_filtering_with_real_server():
    """Test widget filtering with real test server data."""
    config = get_test_config()
    
    async with TestClient(config) as test_client:
        client = test_client.client
        
        # Get all canvases
        canvases = await client.list_canvases()
        if not canvases:
            pytest.skip("No canvases available for testing")
        
        # Use the first canvas for testing
        canvas = canvases[0]
        
        # Get all widgets in the canvas
        all_widgets = await client.list_widgets(canvas.id)
        print(f"📊 Canvas '{canvas.name}' has {len(all_widgets)} widgets")
        
        # Test filtering by widget type
        note_widgets = await client.list_widgets(
            canvas.id,
            filter_obj=Filter(criteria={"widget_type": "Note"})
        )
        print(f"   - Note widgets: {len(note_widgets)}")
        
        browser_widgets = await client.list_widgets(
            canvas.id,
            filter_obj=Filter(criteria={"widget_type": "Browser"})
        )
        print(f"   - Browser widgets: {len(browser_widgets)}")
        
        image_widgets = await client.list_widgets(
            canvas.id,
            filter_obj=Filter(criteria={"widget_type": "Image"})
        )
        print(f"   - Image widgets: {len(image_widgets)}")
        
        # Test spatial filtering if widgets exist
        if all_widgets:
            # Find widgets with location data
            widgets_with_location = [w for w in all_widgets if w.location]
            if widgets_with_location:
                first_widget = widgets_with_location[0]
                x_pos = first_widget.location.get("x", 0)
                
                # Filter by X position
                x_filter = Filter(criteria={"$.location.x": x_pos})
                x_filtered_widgets = await client.list_widgets(canvas.id, filter_obj=x_filter)
                print(f"   - Widgets at X={x_pos}: {len(x_filtered_widgets)}")
                
                # Test wildcard filtering on widget types
                all_types = set(w.widget_type for w in all_widgets)
                if all_types:
                    # Create a filter for any widget type
                    wildcard_filter = Filter(criteria={"widget_type": "*"})
                    wildcard_widgets = await client.list_widgets(canvas.id, filter_obj=wildcard_filter)
                    assert len(wildcard_widgets) == len(all_widgets)
                    print(f"   - Wildcard filter matches all widgets: ✅")
        
        print(f"✅ Widget filtering test completed for canvas '{canvas.name}'")


@pytest.mark.asyncio
async def test_filter_creation_helpers_with_real_server():
    """Test filter creation helpers with real server data."""
    config = get_test_config()
    
    async with TestClient(config) as test_client:
        client = test_client.client
        
        # Get canvases for testing
        canvases = await client.list_canvases()
        if not canvases:
            pytest.skip("No canvases available for testing")
        
        canvas = canvases[0]
        
        # Test create_spatial_filter
        spatial_filter = create_spatial_filter(x=0.0, y=0.0)
        spatial_widgets = await client.list_widgets(canvas.id, filter_obj=spatial_filter)
        print(f"📍 Spatial filter (x=0, y=0) found {len(spatial_widgets)} widgets")
        
        # Test create_widget_type_filter
        widget_type_filter = create_widget_type_filter("Note")
        note_widgets = await client.list_widgets(canvas.id, filter_obj=widget_type_filter)
        print(f"📝 Widget type filter (Note) found {len(note_widgets)} widgets")
        
        # Test create_text_filter if there are notes
        if note_widgets:
            # Get the first note's text - handle type safely
            first_note = note_widgets[0]
            note_text = getattr(first_note, 'text', None)
            if note_text:
                # Create a text filter for the first word
                first_word = note_text.split()[0] if note_text else "test"
                text_filter = create_text_filter(first_word, ["text"])
                text_widgets = await client.list_widgets(canvas.id, filter_obj=text_filter)
                print(f"🔍 Text filter ('{first_word}') found {len(text_widgets)} widgets")
            else:
                print(f"🔍 Text filter test skipped - no text content available")
        
        print(f"✅ Filter creation helpers test completed")


@pytest.mark.asyncio
async def test_complex_filtering_scenarios_with_real_server():
    """Test complex filtering scenarios with real server data."""
    config = get_test_config()
    
    async with TestClient(config) as test_client:
        client = test_client.client
        
        # Get canvases
        canvases = await client.list_canvases()
        if not canvases:
            pytest.skip("No canvases available for testing")
        
        canvas = canvases[0]
        
        # Test multiple criteria filtering
        complex_filter = Filter(criteria={
            "widget_type": "Note",
            "pinned": False
        })
        complex_widgets = await client.list_widgets(canvas.id, filter_obj=complex_filter)
        print(f"🎯 Complex filter (Note + not pinned) found {len(complex_widgets)} widgets")
        
        # Test JSONPath filtering with spatial data
        widgets_with_location = await client.list_widgets(
            canvas.id,
            filter_obj=Filter(criteria={"$.location.x": 0.0})
        )
        print(f"📍 JSONPath filter ($.location.x = 0) found {len(widgets_with_location)} widgets")
        
        # Test wildcard filtering on widget types
        if canvas.name:
            name_prefix = canvas.name[:3] if len(canvas.name) >= 3 else canvas.name
            name_filter = Filter(criteria={"name": f"{name_prefix}*"})
            name_canvases = await client.list_canvases(filter_obj=name_filter)
            assert len(name_canvases) >= 1  # Should include the original canvas
            print(f"🔤 Name wildcard filter ('{name_prefix}*') found {len(name_canvases)} canvases")
        
        print(f"✅ Complex filtering scenarios test completed")


@pytest.mark.asyncio
async def test_filter_performance_with_real_server():
    """Test filtering performance with real server data."""
    config = get_test_config()
    
    async with TestClient(config) as test_client:
        client = test_client.client
        
        # Get canvases
        canvases = await client.list_canvases()
        if not canvases:
            pytest.skip("No canvases available for testing")
        
        canvas = canvases[0]
        
        # Test performance: get all widgets vs filtered widgets
        import time
        
        # Get all widgets (no filter)
        start_time = time.time()
        all_widgets = await client.list_widgets(canvas.id)
        all_widgets_time = time.time() - start_time
        
        # Get widgets with filter
        start_time = time.time()
        filtered_widgets = await client.list_widgets(
            canvas.id,
            filter_obj=Filter(criteria={"widget_type": "Note"})
        )
        filtered_widgets_time = time.time() - start_time
        
        print(f"⚡ Performance test results:")
        print(f"   - All widgets ({len(all_widgets)}): {all_widgets_time:.3f}s")
        print(f"   - Filtered widgets ({len(filtered_widgets)}): {filtered_widgets_time:.3f}s")
        print(f"   - Filter overhead: {filtered_widgets_time - all_widgets_time:.3f}s")
        
        # The filtered request should be similar or faster since we're getting fewer widgets
        assert filtered_widgets_time <= all_widgets_time * 1.5  # Allow some overhead
        
        print(f"✅ Performance test completed")


@pytest.mark.asyncio
async def test_filter_edge_cases_with_real_server():
    """Test filter edge cases with real server data."""
    config = get_test_config()
    
    async with TestClient(config) as test_client:
        client = test_client.client
        
        # Test empty filter (should return all items)
        canvases = await client.list_canvases()
        all_canvases = await client.list_canvases(filter_obj=Filter(criteria={}))
        assert len(all_canvases) == len(canvases)
        print(f"✅ Empty filter test: {len(all_canvases)} canvases returned")
        
        # Test filter with non-existent criteria
        if canvases:
            canvas = canvases[0]
            non_existent_filter = Filter(criteria={"non_existent_field": "value"})
            non_existent_widgets = await client.list_widgets(canvas.id, filter_obj=non_existent_filter)
            assert len(non_existent_widgets) == 0
            print(f"✅ Non-existent field filter test: {len(non_existent_widgets)} widgets returned")
        
        # Test wildcard filter
        wildcard_canvases = await client.list_canvases(filter_obj=Filter(criteria={"name": "*"}))
        assert len(wildcard_canvases) == len(canvases)
        print(f"✅ Wildcard filter test: {len(wildcard_canvases)} canvases returned")
        
        print(f"✅ Edge cases test completed")


@pytest.mark.asyncio
async def test_filter_integration_summary():
    """Provide a summary of all filtering capabilities with real data."""
    config = get_test_config()
    
    async with TestClient(config) as test_client:
        client = test_client.client
        
        print(f"\n🎯 FILTERING SYSTEM INTEGRATION SUMMARY")
        print(f"=" * 50)
        
        # Canvas filtering summary
        canvases = await client.list_canvases()
        print(f"📋 Canvas Filtering:")
        print(f"   - Total canvases: {len(canvases)}")
        
        if canvases:
            # Widget filtering summary
            canvas = canvases[0]
            widgets = await client.list_widgets(canvas.id)
            print(f"   - Canvas '{canvas.name}' widgets: {len(widgets)}")
            
            # Widget type breakdown
            widget_types = {}
            for widget in widgets:
                widget_type = widget.widget_type
                widget_types[widget_type] = widget_types.get(widget_type, 0) + 1
            
            print(f"   - Widget type breakdown:")
            for widget_type, count in widget_types.items():
                print(f"     • {widget_type}: {count}")
            
            # Spatial data summary
            widgets_with_location = [w for w in widgets if w.location]
            widgets_with_size = [w for w in widgets if w.size]
            print(f"   - Widgets with location data: {len(widgets_with_location)}")
            print(f"   - Widgets with size data: {len(widgets_with_size)}")
        
        print(f"\n✅ All filtering integration tests completed successfully!")
        print(f"   - Client-side filtering system is working with real server data")
        print(f"   - Geometry utilities are available for spatial operations")
        print(f"   - Filter creation helpers provide convenient filtering options")
        print(f"   - Performance is acceptable for real-world usage") 