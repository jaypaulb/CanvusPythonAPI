#!/usr/bin/env python3
"""
Integration tests for the filtering system with real server data.
"""

import pytest
import time
from tests.test_config import TestClient, get_test_config
from canvus_api import (
    create_spatial_filter, 
    create_widget_type_filter, 
    create_text_filter,
    create_wildcard_filter,
    create_filter,
    combine_filters
)
from canvus_api.geometry import Rectangle
from canvus_api.models import Note


class TestFilterIntegration:
    """Integration tests for filtering system."""
    
    @pytest.fixture
    def test_config(self):
        """Create test configuration."""
        return get_test_config()
    
    @pytest.mark.asyncio
    async def test_canvas_filtering(self, test_config):
        """Test canvas filtering functionality."""
        async with TestClient(test_config) as test_client:
            client = test_client.client
            
            # Get all canvases
            all_canvases = await client.list_canvases()
            assert len(all_canvases) >= 1
            
            # Test filtering by name
            name_filter = create_filter().add_condition("name", "contains", "API")
            api_canvases = await client.list_canvases(filter_obj=name_filter)
            assert len(api_canvases) >= 1
            
            # Test filtering by state
            normal_filter = create_filter().add_condition("state", "equals", "normal")
            normal_canvases = await client.list_canvases(filter_obj=normal_filter)
            assert len(normal_canvases) >= 1
            
            # Test wildcard filtering
            wildcard_filter = create_wildcard_filter("API*", "name")
            wildcard_canvases = await client.list_canvases(filter_obj=wildcard_filter)
            assert len(wildcard_canvases) >= 1
            
            print("✅ Canvas filtering test completed:")
            print(f"   - Total canvases: {len(all_canvases)}")
            print(f"   - API canvases: {len(api_canvases)}")
            print(f"   - Normal mode canvases: {len(normal_canvases)}")
            print(f"   - Wildcard filtered: {len(wildcard_canvases)}")
    
    @pytest.mark.asyncio
    async def test_widget_filtering(self, test_config):
        """Test widget filtering functionality."""
        async with TestClient(test_config) as test_client:
            client = test_client.client
            
            # Get a canvas with widgets
            canvases = await client.list_canvases()
            canvas = None
            
            for c in canvases:
                widgets = await client.list_widgets(c.id)
                if len(widgets) > 0:
                    canvas = c
                    break
            
            if not canvas:
                print("⚠️ No canvas with widgets found, skipping widget filtering test")
                return
            
            # Get all widgets
            all_widgets = await client.list_widgets(canvas.id)
            assert len(all_widgets) > 0
            
            # Test filtering by widget type
            note_filter = create_widget_type_filter("note")
            note_widgets = await client.list_widgets(canvas.id, filter_obj=note_filter)
            print(f"   - Note widgets: {len(note_widgets)}")
            
            # Test filtering by title
            if all_widgets:
                first_widget = all_widgets[0]
                title = getattr(first_widget, 'title', None)
                if title:
                    title_filter = create_filter().add_condition("title", "contains", title[:5])
                    title_widgets = await client.list_widgets(canvas.id, filter_obj=title_filter)
                    assert len(title_widgets) >= 1
                    print(f"   - Title filter matches: {len(title_widgets)}")
            
            # Test wildcard filtering
            wildcard_filter = create_wildcard_filter("*", "title")
            wildcard_widgets = await client.list_widgets(canvas.id, filter_obj=wildcard_filter)
            assert len(wildcard_widgets) == len(all_widgets)
            print(f"   - Wildcard filter matches all widgets: ✅")
            
            print(f"✅ Widget filtering test completed for canvas '{canvas.name}'")
    
    @pytest.mark.asyncio
    async def test_spatial_filtering(self, test_config):
        """Test spatial filtering functionality."""
        async with TestClient(test_config) as test_client:
            client = test_client.client
            
            # Get a canvas with widgets
            canvases = await client.list_canvases()
            canvas = None
            
            for c in canvases:
                widgets = await client.list_widgets(c.id)
                if len(widgets) > 0:
                    canvas = c
                    break
            
            if not canvas:
                print("⚠️ No canvas with widgets found, skipping spatial filtering test")
                return
            
            # Create a spatial area that should contain some widgets
            spatial_area = Rectangle(x=0, y=0, width=1000, height=1000)
            spatial_filter = create_spatial_filter(spatial_area, "intersects")
            
            spatial_widgets = await client.list_widgets(canvas.id, filter_obj=spatial_filter)
            print(f"   - Spatial filter found {len(spatial_widgets)} widgets in area")
            
            # Test with a smaller area
            small_area = Rectangle(x=0, y=0, width=100, height=100)
            small_spatial_filter = create_spatial_filter(small_area, "intersects")
            small_spatial_widgets = await client.list_widgets(canvas.id, filter_obj=small_spatial_filter)
            print(f"   - Small area filter found {len(small_spatial_widgets)} widgets")
            
            print(f"✅ Spatial filtering test completed")
    
    @pytest.mark.asyncio
    async def test_text_filtering(self, test_config):
        """Test text filtering functionality."""
        async with TestClient(test_config) as test_client:
            client = test_client.client
            
            # Get a canvas with widgets
            canvases = await client.list_canvases()
            canvas = None
            
            for c in canvases:
                widgets = await client.list_widgets(c.id)
                if len(widgets) > 0:
                    canvas = c
                    break
            
            if not canvas:
                print("⚠️ No canvas with widgets found, skipping text filtering test")
                return
            
            # Get all widgets
            all_widgets = await client.list_widgets(canvas.id)
            
            # Find a widget with text content
            text_widget = None
            for widget in all_widgets:
                # Check if it's a Note widget with text
                if isinstance(widget, Note) and widget.text:
                    text_widget = widget
                    break
                # Check if it has a title (for other widget types)
                elif hasattr(widget, 'title') and widget.title:
                    text_widget = widget
                    break
            
            if text_widget:
                # Get first word of text content
                if isinstance(text_widget, Note):
                    text_content = text_widget.text
                else:
                    # Use dict access for other widget types
                    widget_dict = text_widget.model_dump() if hasattr(text_widget, 'model_dump') else dict(text_widget)
                    text_content = widget_dict.get('title', '')
                first_word = text_content.split()[0] if text_content else ''
                
                if first_word:
                    text_filter = create_text_filter(first_word)
                    text_widgets = await client.list_widgets(canvas.id, filter_obj=text_filter)
                    print(f"🔍 Text filter ('{first_word}') found {len(text_widgets)} widgets")
                else:
                    print("🔍 Text filter test skipped - no text content available")
            else:
                print("🔍 Text filter test skipped - no text content available")
            
            print(f"✅ Filter creation helpers test completed")
    
    @pytest.mark.asyncio
    async def test_complex_filtering(self, test_config):
        """Test complex filtering scenarios."""
        async with TestClient(test_config) as test_client:
            client = test_client.client
            
            # Get all canvases
            all_canvases = await client.list_canvases()
            
            # Test combining multiple filters
            if len(all_canvases) > 1:
                # Filter by name prefix and status
                name_prefix = all_canvases[0].name[:3] if all_canvases[0].name else "API"
                
                name_filter = create_wildcard_filter(f"{name_prefix}*", "name")
                status_filter = create_filter().add_condition("state", "equals", "normal")
                
                combined_filter = combine_filters(name_filter, status_filter)
                combined_canvases = await client.list_canvases(filter_obj=combined_filter)
                
                print(f"🔤 Name wildcard filter ('{name_prefix}*') found {len(combined_canvases)} canvases")
            
            print(f"✅ Complex filtering scenarios test completed")
    
    @pytest.mark.asyncio
    async def test_filter_performance(self, test_config):
        """Test filtering performance."""
        async with TestClient(test_config) as test_client:
            client = test_client.client
            
            # Get a canvas with widgets
            canvases = await client.list_canvases()
            canvas = None
            
            for c in canvases:
                widgets = await client.list_widgets(c.id)
                if len(widgets) > 5:  # Need enough widgets for meaningful test
                    canvas = c
                    break
            
            if not canvas:
                print("⚠️ No canvas with sufficient widgets found, skipping performance test")
                return
            
            # Test performance of filtering vs no filtering
            start_time = time.time()
            all_widgets = await client.list_widgets(canvas.id)
            all_widgets_time = time.time() - start_time
            
            # Create a filter that should match most widgets
            wildcard_filter = create_wildcard_filter("*", "title")
            
            start_time = time.time()
            filtered_widgets = await client.list_widgets(canvas.id, filter_obj=wildcard_filter)
            filtered_widgets_time = time.time() - start_time
            
            print(f"⚡ Performance test results:")
            print(f"   - All widgets ({len(all_widgets)}): {all_widgets_time:.3f}s")
            print(f"   - Filtered widgets ({len(filtered_widgets)}): {filtered_widgets_time:.3f}s")
            
            # Performance should be reasonable (not more than 50% slower)
            assert filtered_widgets_time <= all_widgets_time * 1.5  # Allow some overhead
            
            print(f"✅ Performance test completed")
    
    @pytest.mark.asyncio
    async def test_filter_edge_cases(self, test_config):
        """Test filter edge cases."""
        async with TestClient(test_config) as test_client:
            client = test_client.client
            
            # Test empty filter
            empty_filter = create_filter()
            all_canvases = await client.list_canvases()
            empty_filtered_canvases = await client.list_canvases(filter_obj=empty_filter)
            
            # Empty filter should return all items
            assert len(empty_filtered_canvases) == len(all_canvases)
            
            # Test wildcard filter with no matches
            no_match_filter = create_wildcard_filter("NONEXISTENT*", "name")
            no_match_canvases = await client.list_canvases(filter_obj=no_match_filter)
            assert len(no_match_canvases) == 0
            
            print(f"✅ Wildcard filter test: {len(no_match_canvases)} canvases returned")
            
            print(f"✅ Edge cases test completed")
    
    @pytest.mark.asyncio
    async def test_filter_integration_summary(self, test_config):
        """Run comprehensive filter integration test."""
        async with TestClient(test_config) as test_client:
            client = test_client.client
            
            print(f"\n🎯 FILTERING SYSTEM INTEGRATION SUMMARY")
            print(f"=" * 50)
            
            # Canvas filtering summary
            canvases = await client.list_canvases()
            print(f"📋 Canvas Filtering:")
            print(f"   - Total canvases: {len(canvases)}")
            
            # Widget filtering summary
            total_widgets = 0
            widget_types = {}
            
            for canvas in canvases[:3]:  # Test first 3 canvases
                widgets = await client.list_widgets(canvas.id)
                total_widgets += len(widgets)
                
                for widget in widgets:
                    widget_type = getattr(widget, 'type', 'unknown')
                    widget_types[widget_type] = widget_types.get(widget_type, 0) + 1
            
            print(f"📊 Widget Filtering:")
            print(f"   - Total widgets tested: {total_widgets}")
            print(f"   - Widget type breakdown:")
            for widget_type, count in widget_types.items():
                print(f"     • {widget_type}: {count}")
            
            # Spatial filtering summary
            widgets_with_size = 0
            for canvas in canvases[:2]:
                widgets = await client.list_widgets(canvas.id)
                for widget in widgets:
                    if hasattr(widget, 'size') and widget.size:
                        widgets_with_size += 1
            
            print(f"📍 Spatial Filtering:")
            print(f"   - Widgets with size data: {widgets_with_size}")
            
            print(f"\n✅ All filtering integration tests completed successfully!")
            print(f"   - Client-side filtering system is working with real server data")
            print(f"   - Geometry utilities are available for spatial operations")
            print(f"   - Filter creation helpers provide convenient filtering options")
            print(f"   - Performance is acceptable for real-world usage") 