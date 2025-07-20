"""
Geometry utilities for spatial operations in the Canvus API.

This module provides spatial data classes and utility functions for working with
widget positions, sizes, and spatial relationships in canvases.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class Point(BaseModel):
    """Represents a 2D point with x and y coordinates."""
    
    x: float = Field(description="X coordinate")
    y: float = Field(description="Y coordinate")


class Size(BaseModel):
    """Represents a 2D size with width and height."""
    
    width: float = Field(description="Width")
    height: float = Field(description="Height")


class Rectangle(BaseModel):
    """Represents a 2D rectangle with position and size."""
    
    x: float = Field(description="X coordinate of top-left corner")
    y: float = Field(description="Y coordinate of top-left corner")
    width: float = Field(description="Width of rectangle")
    height: float = Field(description="Height of rectangle")


def contains(a: Rectangle, b: Rectangle) -> bool:
    """Check if rectangle a fully contains rectangle b.
    
    Args:
        a: The containing rectangle
        b: The rectangle to check if contained
        
    Returns:
        True if rectangle a fully contains rectangle b, False otherwise
        
    Example:
        >>> a = Rectangle(x=0, y=0, width=10, height=10)
        >>> b = Rectangle(x=2, y=2, width=5, height=5)
        >>> contains(a, b)
        True
    """
    return (b.x >= a.x and b.y >= a.y and
            b.x + b.width <= a.x + a.width and
            b.y + b.height <= a.y + a.height)


def touches(a: Rectangle, b: Rectangle) -> bool:
    """Check if rectangles a and b overlap or touch at any edge/corner.
    
    Args:
        a: First rectangle
        b: Second rectangle
        
    Returns:
        True if rectangles overlap or touch, False otherwise
        
    Example:
        >>> a = Rectangle(x=0, y=0, width=10, height=10)
        >>> b = Rectangle(x=9, y=9, width=5, height=5)
        >>> touches(a, b)
        True
    """
    return (a.x <= b.x + b.width and a.x + a.width >= b.x and
            a.y <= b.y + b.height and a.y + a.height >= b.y)


def widget_bounding_box(widget: Dict[str, Any]) -> Rectangle:
    """Get the bounding box (Rectangle) for a widget.
    
    Args:
        widget: Widget dictionary with location and size information
        
    Returns:
        Rectangle representing the widget's bounding box
        
    Example:
        >>> widget = {
        ...     "location": {"x": 1, "y": 2},
        ...     "size": {"width": 3, "height": 4}
        ... }
        >>> rect = widget_bounding_box(widget)
        >>> print(f"Bounding box: {rect.x}, {rect.y}, {rect.width}x{rect.height}")
        Bounding box: 1, 2, 3x4
    """
    x = widget.get("location", {}).get("x", 0.0) if widget.get("location") else 0.0
    y = widget.get("location", {}).get("y", 0.0) if widget.get("location") else 0.0
    width = widget.get("size", {}).get("width", 0.0) if widget.get("size") else 0.0
    height = widget.get("size", {}).get("height", 0.0) if widget.get("size") else 0.0
    
    return Rectangle(x=x, y=y, width=width, height=height)


def widget_contains(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    """Check if widget a fully contains widget b.
    
    Args:
        a: The containing widget
        b: The widget to check if contained
        
    Returns:
        True if widget a fully contains widget b, False otherwise
        
    Example:
        >>> widget_a = {
        ...     "location": {"x": 0, "y": 0},
        ...     "size": {"width": 100, "height": 100}
        ... }
        >>> widget_b = {
        ...     "location": {"x": 10, "y": 10},
        ...     "size": {"width": 50, "height": 50}
        ... }
        >>> widget_contains(widget_a, widget_b)
        True
    """
    return contains(widget_bounding_box(a), widget_bounding_box(b))


def widgets_touch(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    """Check if widgets a and b touch or overlap.
    
    Args:
        a: First widget
        b: Second widget
        
    Returns:
        True if widgets touch or overlap, False otherwise
        
    Example:
        >>> widget_a = {
        ...     "location": {"x": 0, "y": 0},
        ...     "size": {"width": 100, "height": 100}
        ... }
        >>> widget_b = {
        ...     "location": {"x": 90, "y": 90},
        ...     "size": {"width": 50, "height": 50}
        ... }
        >>> widgets_touch(widget_a, widget_b)
        True
    """
    return touches(widget_bounding_box(a), widget_bounding_box(b))


def calculate_distance(point1: Point, point2: Point) -> float:
    """Calculate the Euclidean distance between two points.
    
    Args:
        point1: First point
        point2: Second point
        
    Returns:
        Distance between the points
        
    Example:
        >>> p1 = Point(x=0, y=0)
        >>> p2 = Point(x=3, y=4)
        >>> calculate_distance(p1, p2)
        5.0
    """
    return ((point2.x - point1.x) ** 2 + (point2.y - point1.y) ** 2) ** 0.5


def rectangle_center(rect: Rectangle) -> Point:
    """Get the center point of a rectangle.
    
    Args:
        rect: The rectangle
        
    Returns:
        Point representing the center of the rectangle
        
    Example:
        >>> rect = Rectangle(x=0, y=0, width=100, height=100)
        >>> center = rectangle_center(rect)
        >>> print(f"Center: ({center.x}, {center.y})")
        Center: (50.0, 50.0)
    """
    return Point(x=rect.x + rect.width / 2, y=rect.y + rect.height / 2)


def rectangle_area(rect: Rectangle) -> float:
    """Calculate the area of a rectangle.
    
    Args:
        rect: The rectangle
        
    Returns:
        Area of the rectangle
        
    Example:
        >>> rect = Rectangle(x=0, y=0, width=10, height=5)
        >>> rectangle_area(rect)
        50.0
    """
    return rect.width * rect.height


def rectangle_intersection(a: Rectangle, b: Rectangle) -> Optional[Rectangle]:
    """Calculate the intersection of two rectangles.
    
    Args:
        a: First rectangle
        b: Second rectangle
        
    Returns:
        Rectangle representing the intersection, or None if no intersection
        
    Example:
        >>> a = Rectangle(x=0, y=0, width=10, height=10)
        >>> b = Rectangle(x=5, y=5, width=10, height=10)
        >>> intersection = rectangle_intersection(a, b)
        >>> if intersection:
        ...     print(f"Intersection: {intersection.x}, {intersection.y}, {intersection.width}x{intersection.height}")
        Intersection: 5, 5, 5x5
    """
    x1 = max(a.x, b.x)
    y1 = max(a.y, b.y)
    x2 = min(a.x + a.width, b.x + b.width)
    y2 = min(a.y + a.height, b.y + b.height)
    
    if x1 < x2 and y1 < y2:
        return Rectangle(x=x1, y=y1, width=x2-x1, height=y2-y1)
    return None 