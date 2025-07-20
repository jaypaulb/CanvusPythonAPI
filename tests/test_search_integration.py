"""
Integration tests for cross-canvas search functionality.
"""

import pytest
import asyncio
from tests.test_config import TestClient
from canvus_api.search import (
    SearchResult, CrossCanvasSearch,
    find_widgets_by_text, find_widgets_by_type, find_widgets_in_area
)
from canvus_api.geometry import Rectangle


class TestSearchIntegration:
    """Integration tests for cross-canvas search functionality."""
    
    @pytest.fixture
    async def client(self):
        """Create a test client."""
        import json
        with open('tests/test_config.json', 'r') as f:
            config = json.load(f)
        client = TestClient(config)
        yield client
        # No cleanup needed for test client
    
    @pytest.fixture
    async def search_engine(self, client):
        """Create a search engine with test client."""
        return CrossCanvasSearch(client)
    
    @pytest.mark.asyncio
    async def test_find_widgets_by_type_integration(self, search_engine):
        """Test finding widgets by type using real server data."""
        print("🔍 Testing find_widgets_by_type with real server data...")
        
        # Search for note widgets across all canvases
        results = await search_engine.find_widgets_by_type("note", max_results=5)
        
        print(f"  📋 Found {len(results)} note widgets")
        
        # Verify results structure
        for result in results:
            assert isinstance(result, SearchResult)
            assert result.widget_type == "note"
            assert result.canvas_id is not None
            assert result.widget_id is not None
            assert result.drill_down_path == f"{result.canvas_id}:{result.widget_id}"
            assert result.match_score == 1.0
            assert result.match_reason == "Exact match on widget_type"
            
            print(f"    ✅ {result.drill_down_path} - {result.canvas_name}")
        
        print("  ✅ find_widgets_by_type integration test passed")
    
    @pytest.mark.asyncio
    async def test_find_widgets_by_text_integration(self, search_engine):
        """Test finding widgets by text using real server data."""
        print("🔍 Testing find_widgets_by_text with real server data...")
        
        # Search for widgets containing "test" text
        results = await search_engine.find_widgets_by_text("test", max_results=5)
        
        print(f"  📋 Found {len(results)} widgets containing 'test'")
        
        # Verify results structure
        for result in results:
            assert isinstance(result, SearchResult)
            assert result.canvas_id is not None
            assert result.widget_id is not None
            assert result.drill_down_path == f"{result.canvas_id}:{result.widget_id}"
            
            print(f"    ✅ {result.drill_down_path} - {result.widget_type}")
        
        print("  ✅ find_widgets_by_text integration test passed")
    
    @pytest.mark.asyncio
    async def test_find_widgets_across_canvases_complex_integration(self, search_engine):
        """Test complex cross-canvas search using real server data."""
        print("🔍 Testing complex cross-canvas search with real server data...")
        
        # Complex query with multiple criteria
        query = {
            "widget_type": "note",
            "state": "normal"
        }
        
        results = await search_engine.find_widgets_across_canvases(
            query, max_results=5
        )
        
        print(f"  📋 Found {len(results)} widgets matching complex query")
        
        # Verify results structure
        for result in results:
            assert isinstance(result, SearchResult)
            assert result.widget_type == "note"
            assert result.widget.state == "normal"
            assert result.canvas_id is not None
            assert result.widget_id is not None
            assert result.match_score == 1.0
            
            print(f"    ✅ {result.drill_down_path} - {result.canvas_name}")
        
        print("  ✅ complex cross-canvas search integration test passed")
    
    @pytest.mark.asyncio
    async def test_find_widgets_in_area_integration(self, search_engine):
        """Test spatial search using real server data."""
        print("🔍 Testing spatial search with real server data...")
        
        # Define a search area
        area = Rectangle(x=0, y=0, width=1000, height=1000)
        
        results = await search_engine.find_widgets_in_area(
            area, max_results=5
        )
        
        print(f"  📋 Found {len(results)} widgets in search area")
        
        # Verify results structure
        for result in results:
            assert isinstance(result, SearchResult)
            assert result.canvas_id is not None
            assert result.widget_id is not None
            
            # Verify widget is within the search area
            widget = result.widget
            if hasattr(widget, 'location') and hasattr(widget, 'size'):
                location = widget.location
                size = widget.size
                if hasattr(location, 'x') and hasattr(location, 'y') and hasattr(size, 'width') and hasattr(size, 'height'):
                    assert location.x >= area.x
                    assert location.y >= area.y
                    assert location.x + size.width <= area.x + area.width
                    assert location.y + size.height <= area.y + area.height
            
            print(f"    ✅ {result.drill_down_path} - {result.widget_type}")
        
        print("  ✅ spatial search integration test passed")
    
    @pytest.mark.asyncio
    async def test_find_widgets_by_property_integration(self, search_engine):
        """Test property-based search using real server data."""
        print("🔍 Testing property-based search with real server data...")
        
        # Search for widgets with specific location
        results = await search_engine.find_widgets_by_property(
            "location.x", 100, max_results=5
        )
        
        print(f"  📋 Found {len(results)} widgets with location.x = 100")
        
        # Verify results structure
        for result in results:
            assert isinstance(result, SearchResult)
            assert result.canvas_id is not None
            assert result.widget_id is not None
            
            # Verify widget has the expected property value
            widget = result.widget
            if hasattr(widget, 'location'):
                location = widget.location
                if hasattr(location, 'x'):
                    assert location.x == 100
            
            print(f"    ✅ {result.drill_down_path} - {result.widget_type}")
        
        print("  ✅ property-based search integration test passed")
    
    @pytest.mark.asyncio
    async def test_convenience_functions_integration(self, client):
        """Test convenience functions using real server data."""
        print("🔍 Testing convenience functions with real server data...")
        
        # Test find_widgets_by_text convenience function
        text_results = await find_widgets_by_text(client, "note", max_results=3)
        print(f"  📋 Convenience function found {len(text_results)} widgets with 'note' text")
        
        # Test find_widgets_by_type convenience function
        type_results = await find_widgets_by_type(client, "image", max_results=3)
        print(f"  📋 Convenience function found {len(type_results)} image widgets")
        
        # Test find_widgets_across_canvases convenience function
        area = Rectangle(x=0, y=0, width=500, height=500)
        area_results = await find_widgets_in_area(client, area, max_results=3)
        print(f"  📋 Convenience function found {len(area_results)} widgets in area")
        
        # Verify all results are SearchResult objects
        for results in [text_results, type_results, area_results]:
            for result in results:
                assert isinstance(result, SearchResult)
                assert result.canvas_id is not None
                assert result.widget_id is not None
        
        print("  ✅ convenience functions integration test passed")
    
    @pytest.mark.asyncio
    async def test_search_result_serialization_integration(self, search_engine):
        """Test SearchResult serialization with real data."""
        print("🔍 Testing SearchResult serialization with real server data...")
        
        # Get some real search results
        results = await search_engine.find_widgets_by_type("note", max_results=2)
        
        if results:
            result = results[0]
            
            # Test to_dict method
            result_dict = result.to_dict()
            
            assert "canvas_id" in result_dict
            assert "canvas_name" in result_dict
            assert "widget_id" in result_dict
            assert "widget_type" in result_dict
            assert "drill_down_path" in result_dict
            assert "match_score" in result_dict
            assert "match_reason" in result_dict
            assert "widget_data" in result_dict
            
            # Verify drill_down_path format
            assert result_dict["drill_down_path"] == f"{result_dict['canvas_id']}:{result_dict['widget_id']}"
            
            print(f"    ✅ Serialized result: {result_dict['drill_down_path']}")
            print(f"    ✅ Widget data keys: {list(result_dict['widget_data'].keys())}")
        
        print("  ✅ SearchResult serialization integration test passed")
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self, search_engine):
        """Test error handling with real server data."""
        print("🔍 Testing error handling with real server data...")
        
        # Test with invalid canvas IDs
        results = await search_engine.find_widgets_across_canvases(
            {}, canvas_ids=["invalid_canvas_id"], max_results=5
        )
        
        # Should return empty list without crashing
        assert isinstance(results, list)
        assert len(results) == 0
        
        print("  ✅ Error handling integration test passed")
    
    @pytest.mark.asyncio
    async def test_wildcard_matching_integration(self, search_engine):
        """Test wildcard matching with real server data."""
        print("🔍 Testing wildcard matching with real server data...")
        
        # Test wildcard matching in text search
        results = await search_engine.find_widgets_by_text("*note*", max_results=5)
        
        print(f"  📋 Found {len(results)} widgets matching '*note*' pattern")
        
        # Verify results
        for result in results:
            assert isinstance(result, SearchResult)
            # The wildcard matching should find widgets with "note" in their text or type
            print(f"    ✅ {result.drill_down_path} - {result.widget_type}")
        
        print("  ✅ wildcard matching integration test passed")


if __name__ == "__main__":
    # Run integration tests
    async def run_integration_tests():
        """Run all integration tests."""
        print("🚀 Starting cross-canvas search integration tests...")
        
        client = TestClient()
        search_engine = CrossCanvasSearch(client)
        
        # Test 1: Find widgets by type
        print("\n1️⃣ Testing find_widgets_by_type...")
        results = await search_engine.find_widgets_by_type("note", max_results=3)
        print(f"   Found {len(results)} note widgets")
        for result in results:
            print(f"   - {result.drill_down_path}: {result.canvas_name}")
        
        # Test 2: Find widgets by text
        print("\n2️⃣ Testing find_widgets_by_text...")
        results = await search_engine.find_widgets_by_text("test", max_results=3)
        print(f"   Found {len(results)} widgets with 'test' text")
        for result in results:
            print(f"   - {result.drill_down_path}: {result.widget_type}")
        
        # Test 3: Complex search
        print("\n3️⃣ Testing complex search...")
        query = {"widget_type": "note", "state": "normal"}
        results = await search_engine.find_widgets_across_canvases(query, max_results=3)
        print(f"   Found {len(results)} widgets matching complex query")
        for result in results:
            print(f"   - {result.drill_down_path}: {result.canvas_name}")
        
        # Test 4: Spatial search
        print("\n4️⃣ Testing spatial search...")
        area = Rectangle(x=0, y=0, width=1000, height=1000)
        results = await search_engine.find_widgets_in_area(area, max_results=3)
        print(f"   Found {len(results)} widgets in search area")
        for result in results:
            print(f"   - {result.drill_down_path}: {result.widget_type}")
        
        print("\n✅ All integration tests completed successfully!")
    
    # Run the tests
    asyncio.run(run_integration_tests()) 