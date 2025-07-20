"""
Integration tests for filtering system with client.
"""

import pytest
from canvus_api import CanvusClient, Filter, create_filter, create_spatial_filter, create_widget_type_filter


class TestFilterIntegration:
    """Integration tests for filtering with client."""
    
    def test_filter_creation_methods(self):
        """Test filter creation methods work correctly."""
        # Test basic filter creation
        filter_obj = create_filter(name="test", type="note")
        assert filter_obj.criteria == {"name": "test", "type": "note"}
        
        # Test spatial filter creation
        spatial_filter = create_spatial_filter(x=100.0, y=200.0)
        assert spatial_filter.criteria == {"$.location.x": 100.0, "$.location.y": 200.0}
        
        # Test widget type filter creation
        widget_filter = create_widget_type_filter("note")
        assert widget_filter.criteria == {"widget_type": "note"}
        
        # Test multiple widget types
        widget_filter_multi = create_widget_type_filter(["note", "browser"])
        assert widget_filter_multi.criteria == {"widget_type": ["note", "browser"]}
    
    def test_filter_with_mock_data(self):
        """Test filtering with mock canvas and widget data."""
        # Mock canvas data
        canvases = [
            {
                "id": "1", "name": "Project Alpha", "mode": "normal", "access": "private",
                "created_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": "2", "name": "Project Beta", "mode": "demo", "access": "public",
                "created_at": "2024-01-02T00:00:00Z"
            },
            {
                "id": "3", "name": "Dashboard", "mode": "normal", "access": "private",
                "created_at": "2024-01-03T00:00:00Z"
            }
        ]
        
        # Test filtering by name with wildcard
        filter_obj = Filter(criteria={"name": "*Project*"})
        filtered = [c for c in canvases if filter_obj.match(c)]
        assert len(filtered) == 2
        assert filtered[0]["id"] == "1"
        assert filtered[1]["id"] == "2"
        
        # Test filtering by mode
        filter_obj = Filter(criteria={"mode": "demo"})
        filtered = [c for c in canvases if filter_obj.match(c)]
        assert len(filtered) == 1
        assert filtered[0]["id"] == "2"
        
        # Test filtering by access
        filter_obj = Filter(criteria={"access": "private"})
        filtered = [c for c in canvases if filter_obj.match(c)]
        assert len(filtered) == 2
        assert filtered[0]["id"] == "1"
        assert filtered[1]["id"] == "3"
    
    def test_widget_filtering_with_mock_data(self):
        """Test widget filtering with mock widget data."""
        # Mock widget data
        widgets = [
            {
                "id": "1", "widget_type": "Note", "location": {"x": 100, "y": 200},
                "size": {"width": 150, "height": 100}, "text": "Hello World"
            },
            {
                "id": "2", "widget_type": "Browser", "location": {"x": 300, "y": 200},
                "size": {"width": 200, "height": 150}, "url": "https://example.com"
            },
            {
                "id": "3", "widget_type": "Note", "location": {"x": 100, "y": 400},
                "size": {"width": 150, "height": 100}, "text": "Dashboard Note"
            }
        ]
        
        # Test filtering by widget type
        filter_obj = Filter(criteria={"widget_type": "Note"})
        filtered = [w for w in widgets if filter_obj.match(w)]
        assert len(filtered) == 2
        assert filtered[0]["id"] == "1"
        assert filtered[1]["id"] == "3"
        
        # Test filtering by spatial position
        filter_obj = Filter(criteria={"$.location.x": 100})
        filtered = [w for w in widgets if filter_obj.match(w)]
        assert len(filtered) == 2
        assert filtered[0]["id"] == "1"
        assert filtered[1]["id"] == "3"
        
        # Test filtering by text content
        filter_obj = Filter(criteria={"text": "*World*"})
        filtered = [w for w in widgets if filter_obj.match(w)]
        assert len(filtered) == 1
        assert filtered[0]["id"] == "1"
        
        # Test filtering by size
        filter_obj = Filter(criteria={"$.size.width": 200})
        filtered = [w for w in widgets if filter_obj.match(w)]
        assert len(filtered) == 1
        assert filtered[0]["id"] == "2"
    
    def test_complex_filtering_scenarios(self):
        """Test complex filtering scenarios."""
        items = [
            {
                "id": "1", "name": "Project Alpha", "type": "canvas", "status": "active",
                "metadata": {"priority": "high", "tags": ["urgent", "frontend"]}
            },
            {
                "id": "2", "name": "Project Beta", "type": "canvas", "status": "inactive",
                "metadata": {"priority": "medium", "tags": ["backend"]}
            },
            {
                "id": "3", "name": "Dashboard Gamma", "type": "dashboard", "status": "active",
                "metadata": {"priority": "low", "tags": ["monitoring"]}
            }
        ]
        
        # Complex filter with multiple criteria
        filter_obj = Filter(criteria={
            "name": "*Project*",
            "status": "active",
            "$.metadata.priority": "high"
        })
        filtered = [item for item in items if filter_obj.match(item)]
        assert len(filtered) == 1
        assert filtered[0]["id"] == "1"
        
        # Filter with wildcards and nested fields
        filter_obj = Filter(criteria={
            "name": "*Project*",
            "$.metadata.tags": "*frontend*"
        })
        filtered = [item for item in items if filter_obj.match(item)]
        assert len(filtered) == 1
        assert filtered[0]["id"] == "1"
    
    def test_filter_edge_cases(self):
        """Test filter edge cases and boundary conditions."""
        # Test empty filter
        filter_obj = Filter(criteria={})
        obj = {"name": "test", "type": "note"}
        assert filter_obj.match(obj) is True  # Empty criteria matches everything
        
        # Test missing fields
        filter_obj = Filter(criteria={"name": "test", "type": "note"})
        obj = {"name": "test"}  # Missing type field
        assert filter_obj.match(obj) is False
        
        # Test wildcard with empty string
        filter_obj = Filter(criteria={"name": "*"})
        obj = {"name": ""}
        assert filter_obj.match(obj) is True  # Wildcard matches empty string
        
        # Test JSONPath with missing nested field
        filter_obj = Filter(criteria={"$.location.x": 100})
        obj = {"location": {"y": 50}}  # Missing x field
        assert filter_obj.match(obj) is False
        
        # Test list wildcard matching
        filter_obj = Filter(criteria={"tags": "*frontend*"})
        obj = {"tags": ["backend", "frontend", "api"]}
        assert filter_obj.match(obj) is True
        
        obj = {"tags": ["backend", "api"]}
        assert filter_obj.match(obj) is False 