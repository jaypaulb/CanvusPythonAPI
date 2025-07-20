"""
Canvus API Client Library
"""

from .client import CanvusClient, CanvusAPIError
from .models import Canvas, CanvasStatus, ServerStatus
from .geometry import Point, Size, Rectangle
from .filters import Filter, filter_list, create_filter, create_spatial_filter, create_widget_type_filter, create_text_filter

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
    "Filter",
    "filter_list",
    "create_filter",
    "create_spatial_filter",
    "create_widget_type_filter",
    "create_text_filter"
]
