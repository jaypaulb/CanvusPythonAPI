"""
Canvus API Client Library
"""

from .client import CanvusClient, CanvusAPIError
from .models import Canvas, CanvasStatus, ServerStatus
from .geometry import Point, Size, Rectangle, widget_bounding_box, widget_contains, widgets_touch, widgets_intersect
from .search import SearchResult, CrossCanvasSearch, find_widgets_across_canvases, find_widgets_by_text, find_widgets_by_type, find_widgets_in_area
from .export import ExportConfig, ImportConfig, WidgetExporter, WidgetImporter, export_widgets_to_folder, import_widgets_from_folder

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
    "widgets_intersect",
    "SearchResult",
    "CrossCanvasSearch",
    "find_widgets_across_canvases",
    "find_widgets_by_text",
    "find_widgets_by_type",
    "find_widgets_in_area",
    "ExportConfig",
    "ImportConfig",
    "WidgetExporter",
    "WidgetImporter",
    "export_widgets_to_folder",
    "import_widgets_from_folder"
]
