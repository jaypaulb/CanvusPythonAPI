"""
Canvus API Client Library
"""

from .client import CanvusClient, CanvusAPIError
from .models import Canvas, CanvasStatus, ServerStatus
from .geometry import Point, Size, Rectangle, widget_bounding_box, widget_contains, widgets_touch, widgets_intersect

__version__ = "0.1.0"
__all__ = [
    "CanvusClient", 
    "Canvas", 
    "CanvasStatus", 
    "ServerStatus", 
    "CanvusAPIError",
    "Point",
    "Size", 
    "Rectangle",
    "widget_bounding_box",
    "widget_contains",
    "widgets_touch",
    "widgets_intersect"
]
