#!/usr/bin/env python3
"""Debug script for search functionality."""

from canvus_api.models import Widget
from canvus_api.search import CrossCanvasSearch
from canvus_api.geometry import Point, Size, Rectangle

def test_widget_matching():
    """Test widget matching functionality."""
    
    # Create a test widget
    widget = Widget(
        id="widget1",
        widget_type="note",
        location={"x": 100, "y": 200},
        size={"width": 50, "height": 30},
        state="normal"
    )
    
    print("Widget created successfully")
    print(f"Widget dict: {widget.model_dump()}")
    print(f"Location: {widget.location}")
    print(f"Location type: {type(widget.location)}")
    
    # Create a search engine (without client for testing)
    search_engine = CrossCanvasSearch(None)
    
    # Test different criteria
    test_criteria = [
        {"widget_type": "note"},
        {"location.x": 100},
        {"widget_type": "note", "location.x": 100},
        {"widget_type": "image"},  # Should not match
    ]
    
    for i, criteria in enumerate(test_criteria):
        result = search_engine._matches_criteria(widget, criteria)
        print(f"Test {i+1}: {criteria} -> {result}")

if __name__ == "__main__":
    test_widget_matching() 