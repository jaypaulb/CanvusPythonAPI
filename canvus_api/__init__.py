"""
Canvus API Client Library
"""

from .client import CanvusClient, CanvusAPIError
from .models import Canvas, CanvasStatus, ServerStatus
from .geometry import Point, Size, Rectangle, widget_bounding_box, widget_contains, widgets_touch, widgets_intersect
from .search import SearchResult, CrossCanvasSearch, find_widgets_across_canvases, find_widgets_by_text, find_widgets_by_type, find_widgets_in_area
from .export import ExportConfig, ImportConfig, WidgetExporter, WidgetImporter, export_widgets_to_folder, import_widgets_from_folder
from .widget_operations import WidgetZoneManager, BatchWidgetOperations, SpatialTolerance, create_spatial_group, find_widget_clusters, calculate_widget_density
from .filters import Filter, create_filter, create_spatial_filter, create_widget_type_filter, create_text_filter, create_wildcard_filter, combine_filters

__version__ = "1.0.0"
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
    "import_widgets_from_folder",
    "WidgetZoneManager",
    "BatchWidgetOperations",
    "SpatialTolerance",
    "create_spatial_group",
    "find_widget_clusters",
    "calculate_widget_density",
    "Filter",
    "create_filter",
    "create_spatial_filter",
    "create_widget_type_filter",
    "create_text_filter",
    "create_wildcard_filter",
    "combine_filters"
]
