"""
Tests for filtering system module.
"""

import pytest
from canvus_api.filters import (
    Filter, filter_list, create_filter, create_spatial_filter,
    create_widget_type_filter, create_text_filter
)


class TestFilter:
    """Test Filter class."""
    
    def test_filter_creation(self):
        """Test Filter creation with criteria."""
        criteria = {"name": "test", "type": "note"}
        filter_obj = Filter(criteria=criteria)
        assert filter_obj.criteria == criteria
    
    def test_filter_match_exact(self):
        """Test exact value matching."""
        filter_obj = Filter(criteria={"name": "test", "type": "note"})
        obj = {"name": "test", "type": "note", "id": "123"}
        assert filter_obj.match(obj) is True
    
    def test_filter_match_partial(self):
        """Test partial matching with wildcards."""
        filter_obj = Filter(criteria={"name": "test*", "type": "*note"})
        obj = {"name": "test123", "type": "mynote", "id": "123"}
        assert filter_obj.match(obj) is True
    
    def test_filter_match_wildcard(self):
        """Test wildcard matching."""
        filter_obj = Filter(criteria={"name": "*", "type": "note"})
        obj = {"name": "anything", "type": "note", "id": "123"}
        assert filter_obj.match(obj) is True
    
    def test_filter_match_contains(self):
        """Test contains matching with wildcards."""
        filter_obj = Filter(criteria={"name": "*mid*", "type": "note"})
        obj = {"name": "prefix_mid_suffix", "type": "note", "id": "123"}
        assert filter_obj.match(obj) is True
    
    def test_filter_match_jsonpath(self):
        """Test JSONPath selector matching."""
        filter_obj = Filter(criteria={"$.location.x": 100.0, "$.size.width": 200.0})
        obj = {
            "location": {"x": 100.0, "y": 50.0},
            "size": {"width": 200.0, "height": 150.0}
        }
        assert filter_obj.match(obj) is True
    
    def test_filter_match_jsonpath_nested(self):
        """Test nested JSONPath selector matching."""
        filter_obj = Filter(criteria={"$.config.settings.enabled": True})
        obj = {
            "config": {
                "settings": {
                    "enabled": True,
                    "timeout": 30
                }
            }
        }
        assert filter_obj.match(obj) is True
    
    def test_filter_no_match(self):
        """Test when object doesn't match filter."""
        filter_obj = Filter(criteria={"name": "test", "type": "note"})
        obj = {"name": "different", "type": "browser", "id": "123"}
        assert filter_obj.match(obj) is False
    
    def test_filter_no_match_jsonpath(self):
        """Test when JSONPath selector doesn't match."""
        filter_obj = Filter(criteria={"$.location.x": 100.0})
        obj = {"location": {"x": 200.0, "y": 50.0}}
        assert filter_obj.match(obj) is False
    
    def test_filter_missing_field(self):
        """Test when object is missing required field."""
        filter_obj = Filter(criteria={"name": "test", "type": "note"})
        obj = {"name": "test"}  # Missing type field
        assert filter_obj.match(obj) is False
    
    def test_filter_missing_jsonpath(self):
        """Test when JSONPath selector points to missing field."""
        filter_obj = Filter(criteria={"$.location.x": 100.0})
        obj = {"location": {"y": 50.0}}  # Missing x field
        assert filter_obj.match(obj) is False
    
    def test_filter_empty_criteria(self):
        """Test filter with empty criteria."""
        filter_obj = Filter(criteria={})
        obj = {"name": "test", "type": "note"}
        assert filter_obj.match(obj) is True  # Empty criteria matches everything
    
    def test_filter_numeric_comparison(self):
        """Test numeric value comparison."""
        filter_obj = Filter(criteria={"count": 5, "price": 10.5})
        obj = {"count": 5, "price": 10.5, "name": "test"}
        assert filter_obj.match(obj) is True
    
    def test_filter_boolean_comparison(self):
        """Test boolean value comparison."""
        filter_obj = Filter(criteria={"enabled": True, "visible": False})
        obj = {"enabled": True, "visible": False, "name": "test"}
        assert filter_obj.match(obj) is True


class TestFilterList:
    """Test filter_list function."""
    
    def test_filter_list_with_filter(self):
        """Test filtering a list with a filter."""
        items = [
            {"id": "1", "name": "test1", "type": "note"},
            {"id": "2", "name": "test2", "type": "browser"},
            {"id": "3", "name": "other", "type": "note"}
        ]
        filter_obj = Filter(criteria={"type": "note"})
        filtered = filter_list(items, filter_obj)
        assert len(filtered) == 2
        assert filtered[0]["id"] == "1"
        assert filtered[1]["id"] == "3"
    
    def test_filter_list_without_filter(self):
        """Test filtering a list without a filter."""
        items = [
            {"id": "1", "name": "test1"},
            {"id": "2", "name": "test2"}
        ]
        filtered = filter_list(items, None)
        assert filtered == items
    
    def test_filter_list_empty_result(self):
        """Test filtering that results in empty list."""
        items = [
            {"id": "1", "name": "test1", "type": "note"},
            {"id": "2", "name": "test2", "type": "browser"}
        ]
        filter_obj = Filter(criteria={"type": "image"})
        filtered = filter_list(items, filter_obj)
        assert len(filtered) == 0
    
    def test_filter_list_wildcard(self):
        """Test filtering with wildcards."""
        items = [
            {"id": "1", "name": "test123", "type": "note"},
            {"id": "2", "name": "other456", "type": "browser"},
            {"id": "3", "name": "test789", "type": "image"}
        ]
        filter_obj = Filter(criteria={"name": "test*"})
        filtered = filter_list(items, filter_obj)
        assert len(filtered) == 2
        assert filtered[0]["id"] == "1"
        assert filtered[1]["id"] == "3"


class TestCreateFilter:
    """Test create_filter function."""
    
    def test_create_filter_basic(self):
        """Test basic filter creation."""
        filter_obj = create_filter(name="test", type="note")
        assert filter_obj.criteria == {"name": "test", "type": "note"}
    
    def test_create_filter_with_wildcards(self):
        """Test filter creation with wildcards."""
        filter_obj = create_filter(name="test*", type="*note")
        assert filter_obj.criteria == {"name": "test*", "type": "*note"}
    
    def test_create_filter_empty(self):
        """Test filter creation with no criteria."""
        filter_obj = create_filter()
        assert filter_obj.criteria == {}


class TestCreateSpatialFilter:
    """Test create_spatial_filter function."""
    
    def test_create_spatial_filter_all_params(self):
        """Test spatial filter creation with all parameters."""
        filter_obj = create_spatial_filter(x=100.0, y=200.0, width=300.0, height=400.0)
        expected = {
            "$.location.x": 100.0,
            "$.location.y": 200.0,
            "$.size.width": 300.0,
            "$.size.height": 400.0
        }
        assert filter_obj.criteria == expected
    
    def test_create_spatial_filter_partial_params(self):
        """Test spatial filter creation with partial parameters."""
        filter_obj = create_spatial_filter(x=100.0, width=300.0)
        expected = {
            "$.location.x": 100.0,
            "$.size.width": 300.0
        }
        assert filter_obj.criteria == expected
    
    def test_create_spatial_filter_no_params(self):
        """Test spatial filter creation with no parameters."""
        filter_obj = create_spatial_filter()
        assert filter_obj.criteria == {}


class TestCreateWidgetTypeFilter:
    """Test create_widget_type_filter function."""
    
    def test_create_widget_type_filter_single(self):
        """Test widget type filter creation with single type."""
        filter_obj = create_widget_type_filter("note")
        assert filter_obj.criteria == {"widget_type": "note"}
    
    def test_create_widget_type_filter_multiple(self):
        """Test widget type filter creation with multiple types."""
        filter_obj = create_widget_type_filter(["note", "browser", "image"])
        assert filter_obj.criteria == {"widget_type": ["note", "browser", "image"]}


class TestCreateTextFilter:
    """Test create_text_filter function."""
    
    def test_create_text_filter_default_fields(self):
        """Test text filter creation with default fields."""
        filter_obj = create_text_filter("dashboard")
        expected = {
            "text": "*dashboard*",
            "title": "*dashboard*",
            "name": "*dashboard*"
        }
        assert filter_obj.criteria == expected
    
    def test_create_text_filter_custom_fields(self):
        """Test text filter creation with custom fields."""
        filter_obj = create_text_filter("dashboard", ["text", "title"])
        expected = {
            "text": "*dashboard*",
            "title": "*dashboard*"
        }
        assert filter_obj.criteria == expected
    
    def test_create_text_filter_single_field(self):
        """Test text filter creation with single field."""
        filter_obj = create_text_filter("dashboard", ["text"])
        expected = {
            "text": "*dashboard*"
        }
        assert filter_obj.criteria == expected


class TestFilterIntegration:
    """Integration tests for filtering system."""
    
    def test_canvas_filtering_integration(self):
        """Test filtering canvases with various criteria."""
        canvases = [
            {
                "id": "1", "name": "Project A", "mode": "normal", "access": "private",
                "created_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": "2", "name": "Project B", "mode": "demo", "access": "public",
                "created_at": "2024-01-02T00:00:00Z"
            },
            {
                "id": "3", "name": "Dashboard", "mode": "normal", "access": "private",
                "created_at": "2024-01-03T00:00:00Z"
            }
        ]
        
        # Filter by name with wildcard
        filter_obj = Filter(criteria={"name": "*Project*"})
        filtered = filter_list(canvases, filter_obj)
        assert len(filtered) == 2
        assert filtered[0]["id"] == "1"
        assert filtered[1]["id"] == "2"
        
        # Filter by mode
        filter_obj = Filter(criteria={"mode": "demo"})
        filtered = filter_list(canvases, filter_obj)
        assert len(filtered) == 1
        assert filtered[0]["id"] == "2"
        
        # Filter by access
        filter_obj = Filter(criteria={"access": "private"})
        filtered = filter_list(canvases, filter_obj)
        assert len(filtered) == 2
        assert filtered[0]["id"] == "1"
        assert filtered[1]["id"] == "3"
    
    def test_widget_filtering_integration(self):
        """Test filtering widgets with spatial and type criteria."""
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
        
        # Filter by widget type
        filter_obj = Filter(criteria={"widget_type": "Note"})
        filtered = filter_list(widgets, filter_obj)
        assert len(filtered) == 2
        assert filtered[0]["id"] == "1"
        assert filtered[1]["id"] == "3"
        
        # Filter by spatial position
        filter_obj = Filter(criteria={"$.location.x": 100})
        filtered = filter_list(widgets, filter_obj)
        assert len(filtered) == 2
        assert filtered[0]["id"] == "1"
        assert filtered[1]["id"] == "3"
        
        # Filter by text content
        filter_obj = Filter(criteria={"text": "*World*"})
        filtered = filter_list(widgets, filter_obj)
        assert len(filtered) == 1
        assert filtered[0]["id"] == "1"
        
        # Filter by size
        filter_obj = Filter(criteria={"$.size.width": 200})
        filtered = filter_list(widgets, filter_obj)
        assert len(filtered) == 1
        assert filtered[0]["id"] == "2"
    
    def test_complex_filtering_scenarios(self):
        """Test complex filtering scenarios with multiple criteria."""
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
        filtered = filter_list(items, filter_obj)
        assert len(filtered) == 1
        assert filtered[0]["id"] == "1"
        
        # Filter with wildcards and nested fields
        filter_obj = Filter(criteria={
            "name": "*Project*",
            "$.metadata.tags": "*frontend*"
        })
        filtered = filter_list(items, filter_obj)
        assert len(filtered) == 1
        assert filtered[0]["id"] == "1" 