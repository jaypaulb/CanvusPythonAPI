"""
Tests for geometry utilities module.
"""

import pytest
from canvus_api.geometry import (
    Point, Size, Rectangle, contains, touches, widget_bounding_box,
    widget_contains, widgets_touch, calculate_distance, rectangle_center,
    rectangle_area, rectangle_intersection
)


class TestPoint:
    """Test Point class."""
    
    def test_point_creation(self):
        """Test Point creation with x and y coordinates."""
        point = Point(x=10.0, y=20.0)
        assert point.x == 10.0
        assert point.y == 20.0
    
    def test_point_equality(self):
        """Test Point equality."""
        point1 = Point(x=10.0, y=20.0)
        point2 = Point(x=10.0, y=20.0)
        point3 = Point(x=15.0, y=20.0)
        
        assert point1 == point2
        assert point1 != point3


class TestSize:
    """Test Size class."""
    
    def test_size_creation(self):
        """Test Size creation with width and height."""
        size = Size(width=100.0, height=200.0)
        assert size.width == 100.0
        assert size.height == 200.0
    
    def test_size_equality(self):
        """Test Size equality."""
        size1 = Size(width=100.0, height=200.0)
        size2 = Size(width=100.0, height=200.0)
        size3 = Size(width=150.0, height=200.0)
        
        assert size1 == size2
        assert size1 != size3


class TestRectangle:
    """Test Rectangle class."""
    
    def test_rectangle_creation(self):
        """Test Rectangle creation with position and size."""
        rect = Rectangle(x=10.0, y=20.0, width=100.0, height=200.0)
        assert rect.x == 10.0
        assert rect.y == 20.0
        assert rect.width == 100.0
        assert rect.height == 200.0
    
    def test_rectangle_equality(self):
        """Test Rectangle equality."""
        rect1 = Rectangle(x=10.0, y=20.0, width=100.0, height=200.0)
        rect2 = Rectangle(x=10.0, y=20.0, width=100.0, height=200.0)
        rect3 = Rectangle(x=15.0, y=20.0, width=100.0, height=200.0)
        
        assert rect1 == rect2
        assert rect1 != rect3


class TestContains:
    """Test contains function."""
    
    def test_contains_true(self):
        """Test when rectangle a fully contains rectangle b."""
        a = Rectangle(x=0, y=0, width=100, height=100)
        b = Rectangle(x=10, y=10, width=50, height=50)
        assert contains(a, b) is True
    
    def test_contains_false(self):
        """Test when rectangle a does not contain rectangle b."""
        a = Rectangle(x=0, y=0, width=50, height=50)
        b = Rectangle(x=10, y=10, width=50, height=50)
        assert contains(a, b) is False
    
    def test_contains_edge_case(self):
        """Test edge case where rectangles touch but don't overlap."""
        a = Rectangle(x=0, y=0, width=100, height=100)
        b = Rectangle(x=100, y=0, width=50, height=50)
        assert contains(a, b) is False
    
    def test_contains_same_rectangle(self):
        """Test when rectangles are identical."""
        a = Rectangle(x=0, y=0, width=100, height=100)
        assert contains(a, a) is True


class TestTouches:
    """Test touches function."""
    
    def test_touches_overlap(self):
        """Test when rectangles overlap."""
        a = Rectangle(x=0, y=0, width=100, height=100)
        b = Rectangle(x=50, y=50, width=100, height=100)
        assert touches(a, b) is True
    
    def test_touches_edge(self):
        """Test when rectangles touch at edge."""
        a = Rectangle(x=0, y=0, width=100, height=100)
        b = Rectangle(x=100, y=0, width=50, height=50)
        assert touches(a, b) is True
    
    def test_touches_corner(self):
        """Test when rectangles touch at corner."""
        a = Rectangle(x=0, y=0, width=100, height=100)
        b = Rectangle(x=100, y=100, width=50, height=50)
        assert touches(a, b) is True
    
    def test_touches_false(self):
        """Test when rectangles don't touch."""
        a = Rectangle(x=0, y=0, width=100, height=100)
        b = Rectangle(x=200, y=200, width=50, height=50)
        assert touches(a, b) is False


class TestWidgetBoundingBox:
    """Test widget_bounding_box function."""
    
    def test_widget_with_location_and_size(self):
        """Test widget with both location and size."""
        widget = {
            "location": {"x": 10.0, "y": 20.0},
            "size": {"width": 100.0, "height": 200.0}
        }
        rect = widget_bounding_box(widget)
        assert rect.x == 10.0
        assert rect.y == 20.0
        assert rect.width == 100.0
        assert rect.height == 200.0
    
    def test_widget_without_location(self):
        """Test widget without location."""
        widget = {
            "size": {"width": 100.0, "height": 200.0}
        }
        rect = widget_bounding_box(widget)
        assert rect.x == 0.0
        assert rect.y == 0.0
        assert rect.width == 100.0
        assert rect.height == 200.0
    
    def test_widget_without_size(self):
        """Test widget without size."""
        widget = {
            "location": {"x": 10.0, "y": 20.0}
        }
        rect = widget_bounding_box(widget)
        assert rect.x == 10.0
        assert rect.y == 20.0
        assert rect.width == 0.0
        assert rect.height == 0.0
    
    def test_empty_widget(self):
        """Test empty widget."""
        widget = {}
        rect = widget_bounding_box(widget)
        assert rect.x == 0.0
        assert rect.y == 0.0
        assert rect.width == 0.0
        assert rect.height == 0.0


class TestWidgetContains:
    """Test widget_contains function."""
    
    def test_widget_contains_true(self):
        """Test when widget a contains widget b."""
        widget_a = {
            "location": {"x": 0, "y": 0},
            "size": {"width": 100, "height": 100}
        }
        widget_b = {
            "location": {"x": 10, "y": 10},
            "size": {"width": 50, "height": 50}
        }
        assert widget_contains(widget_a, widget_b) is True
    
    def test_widget_contains_false(self):
        """Test when widget a does not contain widget b."""
        widget_a = {
            "location": {"x": 0, "y": 0},
            "size": {"width": 50, "height": 50}
        }
        widget_b = {
            "location": {"x": 10, "y": 10},
            "size": {"width": 50, "height": 50}
        }
        assert widget_contains(widget_a, widget_b) is False


class TestWidgetsTouch:
    """Test widgets_touch function."""
    
    def test_widgets_touch_overlap(self):
        """Test when widgets overlap."""
        widget_a = {
            "location": {"x": 0, "y": 0},
            "size": {"width": 100, "height": 100}
        }
        widget_b = {
            "location": {"x": 50, "y": 50},
            "size": {"width": 100, "height": 100}
        }
        assert widgets_touch(widget_a, widget_b) is True
    
    def test_widgets_touch_edge(self):
        """Test when widgets touch at edge."""
        widget_a = {
            "location": {"x": 0, "y": 0},
            "size": {"width": 100, "height": 100}
        }
        widget_b = {
            "location": {"x": 100, "y": 0},
            "size": {"width": 50, "height": 50}
        }
        assert widgets_touch(widget_a, widget_b) is True
    
    def test_widgets_dont_touch(self):
        """Test when widgets don't touch."""
        widget_a = {
            "location": {"x": 0, "y": 0},
            "size": {"width": 100, "height": 100}
        }
        widget_b = {
            "location": {"x": 200, "y": 200},
            "size": {"width": 50, "height": 50}
        }
        assert widgets_touch(widget_a, widget_b) is False


class TestCalculateDistance:
    """Test calculate_distance function."""
    
    def test_distance_between_points(self):
        """Test distance calculation between two points."""
        p1 = Point(x=0, y=0)
        p2 = Point(x=3, y=4)
        distance = calculate_distance(p1, p2)
        assert distance == 5.0
    
    def test_distance_same_point(self):
        """Test distance between same point."""
        p1 = Point(x=10, y=20)
        distance = calculate_distance(p1, p1)
        assert distance == 0.0
    
    def test_distance_negative_coordinates(self):
        """Test distance with negative coordinates."""
        p1 = Point(x=-3, y=-4)
        p2 = Point(x=0, y=0)
        distance = calculate_distance(p1, p2)
        assert distance == 5.0


class TestRectangleCenter:
    """Test rectangle_center function."""
    
    def test_rectangle_center(self):
        """Test center point calculation."""
        rect = Rectangle(x=0, y=0, width=100, height=100)
        center = rectangle_center(rect)
        assert center.x == 50.0
        assert center.y == 50.0
    
    def test_rectangle_center_offset(self):
        """Test center point with offset rectangle."""
        rect = Rectangle(x=10, y=20, width=100, height=100)
        center = rectangle_center(rect)
        assert center.x == 60.0
        assert center.y == 70.0


class TestRectangleArea:
    """Test rectangle_area function."""
    
    def test_rectangle_area(self):
        """Test area calculation."""
        rect = Rectangle(x=0, y=0, width=10, height=5)
        area = rectangle_area(rect)
        assert area == 50.0
    
    def test_rectangle_area_zero(self):
        """Test area with zero dimensions."""
        rect = Rectangle(x=0, y=0, width=0, height=0)
        area = rectangle_area(rect)
        assert area == 0.0


class TestRectangleIntersection:
    """Test rectangle_intersection function."""
    
    def test_rectangle_intersection_overlap(self):
        """Test intersection of overlapping rectangles."""
        a = Rectangle(x=0, y=0, width=100, height=100)
        b = Rectangle(x=50, y=50, width=100, height=100)
        intersection = rectangle_intersection(a, b)
        assert intersection is not None
        assert intersection.x == 50
        assert intersection.y == 50
        assert intersection.width == 50
        assert intersection.height == 50
    
    def test_rectangle_intersection_no_overlap(self):
        """Test intersection of non-overlapping rectangles."""
        a = Rectangle(x=0, y=0, width=50, height=50)
        b = Rectangle(x=100, y=100, width=50, height=50)
        intersection = rectangle_intersection(a, b)
        assert intersection is None
    
    def test_rectangle_intersection_edge_touch(self):
        """Test intersection of rectangles that touch at edge."""
        a = Rectangle(x=0, y=0, width=100, height=100)
        b = Rectangle(x=100, y=0, width=50, height=50)
        intersection = rectangle_intersection(a, b)
        assert intersection is None  # Edge touch is not considered intersection 