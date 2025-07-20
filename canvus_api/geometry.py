"""
Geometry utilities for spatial operations in the Canvus API.

This module provides spatial data classes and utility functions for working with
widget positions, sizes, and spatial relationships in canvases.
"""

from typing import List, Optional, Union
from dataclasses import dataclass
from .models import BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector


@dataclass
class Point:
    """2D point with x, y coordinates."""
    
    x: float
    y: float
    
    def __post_init__(self):
        """Validate coordinates."""
        if not isinstance(self.x, (int, float)) or not isinstance(self.y, (int, float)):
            raise ValueError("Coordinates must be numeric values")


@dataclass
class Size:
    """2D size with width and height."""
    
    width: float
    height: float
    
    def __post_init__(self):
        """Validate dimensions."""
        if not isinstance(self.width, (int, float)) or not isinstance(self.height, (int, float)):
            raise ValueError("Dimensions must be numeric values")
        if self.width < 0 or self.height < 0:
            raise ValueError("Dimensions cannot be negative")


@dataclass
class Rectangle:
    """2D rectangle defined by position and size."""
    
    x: float
    y: float
    width: float
    height: float
    
    def __post_init__(self):
        """Validate rectangle properties."""
        if not all(isinstance(v, (int, float)) for v in [self.x, self.y, self.width, self.height]):
            raise ValueError("All rectangle properties must be numeric values")
        if self.width < 0 or self.height < 0:
            raise ValueError("Rectangle dimensions cannot be negative")
    
    @property
    def left(self) -> float:
        """Left edge of the rectangle."""
        return self.x
    
    @property
    def right(self) -> float:
        """Right edge of the rectangle."""
        return self.x + self.width
    
    @property
    def top(self) -> float:
        """Top edge of the rectangle."""
        return self.y
    
    @property
    def bottom(self) -> float:
        """Bottom edge of the rectangle."""
        return self.y + self.height
    
    @property
    def center(self) -> Point:
        """Center point of the rectangle."""
        return Point(self.x + self.width / 2, self.y + self.height / 2)
    
    @property
    def size(self) -> Size:
        """Size of the rectangle."""
        return Size(self.width, self.height)
    
    @property
    def position(self) -> Point:
        """Top-left position of the rectangle."""
        return Point(self.x, self.y)


def contains(outer: Rectangle, inner: Rectangle) -> bool:
    """
    Check if one rectangle completely contains another.
    
    Args:
        outer: The outer rectangle
        inner: The inner rectangle to check
        
    Returns:
        True if outer completely contains inner, False otherwise
    """
    return (outer.left <= inner.left and 
            outer.right >= inner.right and 
            outer.top <= inner.top and 
            outer.bottom >= inner.bottom)


def touches(rect1: Rectangle, rect2: Rectangle) -> bool:
    """
    Check if two rectangles touch or overlap.
    
    Args:
        rect1: First rectangle
        rect2: Second rectangle
        
    Returns:
        True if rectangles touch or overlap, False otherwise
    """
    return not (rect1.right < rect2.left or 
                rect1.left > rect2.right or 
                rect1.bottom < rect2.top or 
                rect1.top > rect2.bottom)


def intersects(rect1: Rectangle, rect2: Rectangle) -> bool:
    """
    Check if two rectangles intersect (have overlapping area).
    
    Args:
        rect1: First rectangle
        rect2: Second rectangle
        
    Returns:
        True if rectangles have overlapping area, False otherwise
    """
    return not (rect1.right <= rect2.left or 
                rect1.left >= rect2.right or 
                rect1.bottom <= rect2.top or 
                rect1.top >= rect2.bottom)


def get_intersection(rect1: Rectangle, rect2: Rectangle) -> Optional[Rectangle]:
    """
    Get the intersection rectangle of two rectangles.
    
    Args:
        rect1: First rectangle
        rect2: Second rectangle
        
    Returns:
        Intersection rectangle if rectangles overlap, None otherwise
    """
    if not intersects(rect1, rect2):
        return None
    
    left = max(rect1.left, rect2.left)
    top = max(rect1.top, rect2.top)
    right = min(rect1.right, rect2.right)
    bottom = min(rect1.bottom, rect2.bottom)
    
    return Rectangle(left, top, right - left, bottom - top)


def get_union(rect1: Rectangle, rect2: Rectangle) -> Rectangle:
    """
    Get the union rectangle that contains both rectangles.
    
    Args:
        rect1: First rectangle
        rect2: Second rectangle
        
    Returns:
        Union rectangle containing both input rectangles
    """
    left = min(rect1.left, rect2.left)
    top = min(rect1.top, rect2.top)
    right = max(rect1.right, rect2.right)
    bottom = max(rect1.bottom, rect2.bottom)
    
    return Rectangle(left, top, right - left, bottom - top)


def widget_bounding_box(widget: Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]) -> Rectangle:
    """
    Get the bounding box rectangle for a widget.
    
    Args:
        widget: Any widget object with location and size properties, or Connector with endpoints
        
    Returns:
        Rectangle representing the widget's bounding box
        
    Raises:
        ValueError: If widget doesn't have required properties
    """
    # Handle Connector objects specially
    if isinstance(widget, Connector):
        if not hasattr(widget, 'src') or not hasattr(widget, 'dst'):
            raise ValueError("Connector must have src and dst properties")
        
        # Get source and destination locations
        src_location = widget.src.rel_location
        dst_location = widget.dst.rel_location
        
        if not isinstance(src_location, dict) or not isinstance(dst_location, dict):
            raise ValueError("Connector endpoints must have rel_location dictionaries")
        
        if 'x' not in src_location or 'y' not in src_location or 'x' not in dst_location or 'y' not in dst_location:
            raise ValueError("Connector endpoint locations must have 'x' and 'y' keys")
        
        # Calculate bounding box from endpoints
        x_coords = [src_location['x'], dst_location['x']]
        y_coords = [src_location['y'], dst_location['y']]
        
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        
        # Add some padding for the connector line
        padding = 10.0
        return Rectangle(
            x=min_x - padding,
            y=min_y - padding,
            width=(max_x - min_x) + 2 * padding,
            height=(max_y - min_y) + 2 * padding
        )
    
    # Handle regular widgets with location and size
    if not hasattr(widget, 'location') or not hasattr(widget, 'size'):
        raise ValueError("Widget must have location and size properties")
    
    location = widget.location
    size = widget.size
    
    if not isinstance(location, dict) or not isinstance(size, dict):
        raise ValueError("Widget location and size must be dictionaries")
    
    if 'x' not in location or 'y' not in location:
        raise ValueError("Widget location must have 'x' and 'y' keys")
    
    if 'width' not in size or 'height' not in size:
        raise ValueError("Widget size must have 'width' and 'height' keys")
    
    return Rectangle(
        x=float(location['x']),
        y=float(location['y']),
        width=float(size['width']),
        height=float(size['height'])
    )


def widget_contains(widget1: Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector], 
                   widget2: Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]) -> bool:
    """
    Check if one widget completely contains another widget.
    
    Args:
        widget1: The outer widget
        widget2: The inner widget to check
        
    Returns:
        True if widget1 completely contains widget2, False otherwise
    """
    rect1 = widget_bounding_box(widget1)
    rect2 = widget_bounding_box(widget2)
    return contains(rect1, rect2)


def widgets_touch(widget1: Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector], 
                 widget2: Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]) -> bool:
    """
    Check if two widgets touch or overlap.
    
    Args:
        widget1: First widget
        widget2: Second widget
        
    Returns:
        True if widgets touch or overlap, False otherwise
    """
    rect1 = widget_bounding_box(widget1)
    rect2 = widget_bounding_box(widget2)
    return touches(rect1, rect2)


def widgets_intersect(widget1: Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector], 
                     widget2: Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]) -> bool:
    """
    Check if two widgets intersect (have overlapping area).
    
    Args:
        widget1: First widget
        widget2: Second widget
        
    Returns:
        True if widgets have overlapping area, False otherwise
    """
    rect1 = widget_bounding_box(widget1)
    rect2 = widget_bounding_box(widget2)
    return intersects(rect1, rect2)


def get_widget_intersection(widget1: Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector], 
                           widget2: Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]) -> Optional[Rectangle]:
    """
    Get the intersection rectangle of two widgets.
    
    Args:
        widget1: First widget
        widget2: Second widget
        
    Returns:
        Intersection rectangle if widgets overlap, None otherwise
    """
    rect1 = widget_bounding_box(widget1)
    rect2 = widget_bounding_box(widget2)
    return get_intersection(rect1, rect2)


def get_widget_union(widget1: Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector], 
                    widget2: Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]) -> Rectangle:
    """
    Get the union rectangle that contains both widgets.
    
    Args:
        widget1: First widget
        widget2: Second widget
        
    Returns:
        Union rectangle containing both widgets
    """
    rect1 = widget_bounding_box(widget1)
    rect2 = widget_bounding_box(widget2)
    return get_union(rect1, rect2)


def distance_between_widgets(widget1: Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector], 
                           widget2: Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]) -> float:
    """
    Calculate the minimum distance between two widgets.
    
    Args:
        widget1: First widget
        widget2: Second widget
        
    Returns:
        Minimum distance between the widgets (0 if they overlap)
    """
    rect1 = widget_bounding_box(widget1)
    rect2 = widget_bounding_box(widget2)
    
    # If widgets overlap, distance is 0
    if intersects(rect1, rect2):
        return 0.0
    
    # Calculate horizontal and vertical distances
    horizontal_distance = max(0, max(rect1.left - rect2.right, rect2.left - rect1.right))
    vertical_distance = max(0, max(rect1.top - rect2.bottom, rect2.top - rect1.bottom))
    
    # Return the minimum distance
    return min(horizontal_distance, vertical_distance) if horizontal_distance > 0 and vertical_distance > 0 else max(horizontal_distance, vertical_distance)


def find_widgets_in_area(widgets: List[Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]], 
                        area: Rectangle) -> List[Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]]:
    """
    Find all widgets that intersect with a given area.
    
    Args:
        widgets: List of widgets to search
        area: Rectangle defining the search area
        
    Returns:
        List of widgets that intersect with the area
    """
    result = []
    for widget in widgets:
        widget_rect = widget_bounding_box(widget)
        if intersects(widget_rect, area):
            result.append(widget)
    return result


def find_widgets_containing_point(widgets: List[Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]], 
                                 point: Point) -> List[Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]]:
    """
    Find all widgets that contain a given point.
    
    Args:
        widgets: List of widgets to search
        point: Point to check
        
    Returns:
        List of widgets that contain the point
    """
    result = []
    for widget in widgets:
        widget_rect = widget_bounding_box(widget)
        if (widget_rect.left <= point.x <= widget_rect.right and 
            widget_rect.top <= point.y <= widget_rect.bottom):
            result.append(widget)
    return result


def get_canvas_bounds(widgets: List[Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]]) -> Optional[Rectangle]:
    """
    Calculate the bounding rectangle that contains all widgets.
    
    Args:
        widgets: List of widgets
        
    Returns:
        Bounding rectangle containing all widgets, or None if no widgets
    """
    if not widgets:
        return None
    
    # Start with the first widget's bounds
    bounds = widget_bounding_box(widgets[0])
    
    # Expand bounds to include all other widgets
    for widget in widgets[1:]:
        widget_rect = widget_bounding_box(widget)
        bounds = get_union(bounds, widget_rect)
    
    return bounds 