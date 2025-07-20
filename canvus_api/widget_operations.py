"""
Advanced widget operations for spatial grouping, batch operations, and zone management.

This module provides advanced functionality for working with widgets in spatial contexts,
including zone-based operations, batch processing, and spatial tolerance management.
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from .models import (
    BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector, WidgetZone
)
from .geometry import (
    Rectangle, contains, touches, intersects, 
    widget_bounding_box, widget_contains, widgets_touch
)


@dataclass
class SpatialTolerance:
    """Configuration for spatial tolerance in widget operations."""
    
    position_tolerance: float = 5.0  # Tolerance for position-based operations
    size_tolerance: float = 2.0  # Tolerance for size-based operations
    overlap_tolerance: float = 1.0  # Minimum overlap for intersection operations
    distance_tolerance: float = 10.0  # Tolerance for distance-based operations


class WidgetZoneManager:
    """Manager for widget zone operations and spatial grouping."""
    
    def __init__(self, tolerance: Optional[SpatialTolerance] = None):
        """Initialize the zone manager.
        
        Args:
            tolerance: Spatial tolerance configuration
        """
        self.tolerance = tolerance or SpatialTolerance()
    
    def create_zone_from_widgets(
        self, 
        widgets: List[Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]],
        name: str,
        description: Optional[str] = None,
        padding: float = 20.0
    ) -> WidgetZone:
        """Create a widget zone that encompasses a group of widgets.
        
        Args:
            widgets: List of widgets to include in the zone
            name: Name for the new zone
            description: Optional description
            padding: Padding around the widget bounds
            
        Returns:
            WidgetZone encompassing all widgets
            
        Raises:
            ValueError: If widgets list is empty
        """
        if not widgets:
            raise ValueError("Cannot create zone from empty widget list")
        
        # Calculate bounding box for all widgets
        bounds = self._calculate_widget_bounds(widgets)
        
        # Add padding
        padded_bounds = Rectangle(
            x=bounds.x - padding,
            y=bounds.y - padding,
            width=bounds.width + 2 * padding,
            height=bounds.height + 2 * padding
        )
        
        return WidgetZone(
            id=f"zone_{len(widgets)}_{hash(name)}",  # Simple ID generation
            name=name,
            description=description,
            location={"x": padded_bounds.x, "y": padded_bounds.y},
            size={"width": padded_bounds.width, "height": padded_bounds.height}
        )
    
    def widgets_in_zone(
        self,
        widgets: List[Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]],
        zone: WidgetZone
    ) -> List[Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]]:
        """Find all widgets that are contained within a zone.
        
        Args:
            widgets: List of widgets to check
            zone: The zone to check against
            
        Returns:
            List of widgets contained within the zone
        """
        zone_rect = Rectangle(
            x=zone.location["x"],
            y=zone.location["y"],
            width=zone.size["width"],
            height=zone.size["height"]
        )
        
        result = []
        for widget in widgets:
            try:
                widget_rect = widget_bounding_box(widget)
                if contains(zone_rect, widget_rect):
                    result.append(widget)
            except (ValueError, AttributeError):
                # Skip widgets that can't be processed
                continue
        
        return result
    
    def widgets_touching_zone(
        self,
        widgets: List[Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]],
        zone: WidgetZone
    ) -> List[Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]]:
        """Find all widgets that touch or overlap with a zone.
        
        Args:
            widgets: List of widgets to check
            zone: The zone to check against
            
        Returns:
            List of widgets that touch or overlap the zone
        """
        zone_rect = Rectangle(
            x=zone.location["x"],
            y=zone.location["y"],
            width=zone.size["width"],
            height=zone.size["height"]
        )
        
        result = []
        for widget in widgets:
            try:
                widget_rect = widget_bounding_box(widget)
                if touches(zone_rect, widget_rect):
                    result.append(widget)
            except (ValueError, AttributeError):
                # Skip widgets that can't be processed
                continue
        
        return result
    
    def _calculate_widget_bounds(
        self,
        widgets: List[Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]]
    ) -> Rectangle:
        """Calculate the bounding box that contains all widgets.
        
        Args:
            widgets: List of widgets
            
        Returns:
            Rectangle containing all widgets
        """
        if not widgets:
            raise ValueError("Cannot calculate bounds for empty widget list")
        
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')
        
        for widget in widgets:
            try:
                rect = widget_bounding_box(widget)
                min_x = min(min_x, rect.x)
                min_y = min(min_y, rect.y)
                max_x = max(max_x, rect.x + rect.width)
                max_y = max(max_y, rect.y + rect.height)
            except (ValueError, AttributeError):
                # Skip widgets that can't be processed
                continue
        
        if min_x == float('inf'):
            raise ValueError("No valid widgets found for bounds calculation")
        
        return Rectangle(
            x=min_x,
            y=min_y,
            width=max_x - min_x,
            height=max_y - min_y
        )


class BatchWidgetOperations:
    """Batch operations for multiple widgets."""
    
    def __init__(self, tolerance: Optional[SpatialTolerance] = None):
        """Initialize batch operations.
        
        Args:
            tolerance: Spatial tolerance configuration
        """
        self.tolerance = tolerance or SpatialTolerance()
    
    def move_widgets(
        self,
        widgets: List[Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]],
        offset_x: float,
        offset_y: float
    ) -> List[Dict[str, Any]]:
        """Generate move operations for multiple widgets.
        
        Args:
            widgets: List of widgets to move
            offset_x: X offset to apply
            offset_y: Y offset to apply
            
        Returns:
            List of update payloads for moving widgets
        """
        operations = []
        
        for widget in widgets:
            # Handle Connector objects specially
            if isinstance(widget, Connector):
                # Connectors have src and dst endpoints that need to be moved
                if hasattr(widget, 'src') and hasattr(widget, 'dst'):
                    src_location = widget.src.rel_location
                    dst_location = widget.dst.rel_location
                    
                    new_src_location = {
                        'x': src_location.get('x', 0.0) + offset_x,
                        'y': src_location.get('y', 0.0) + offset_y
                    }
                    new_dst_location = {
                        'x': dst_location.get('x', 0.0) + offset_x,
                        'y': dst_location.get('y', 0.0) + offset_y
                    }
                    
                    operations.append({
                        'widget_id': widget.id,
                        'operation': 'move',
                        'payload': {
                            'src': {'rel_location': new_src_location},
                            'dst': {'rel_location': new_dst_location}
                        }
                    })
                continue
            
            # Handle regular widgets with location
            if not hasattr(widget, 'location') or not isinstance(widget.location, dict):
                continue
            
            current_x = widget.location.get('x', 0.0)
            current_y = widget.location.get('y', 0.0)
            
            new_location = {
                'x': current_x + offset_x,
                'y': current_y + offset_y
            }
            
            operations.append({
                'widget_id': widget.id,
                'operation': 'move',
                'payload': {'location': new_location}
            })
        
        return operations
    
    def resize_widgets(
        self,
        widgets: List[Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]],
        scale_factor: float
    ) -> List[Dict[str, Any]]:
        """Generate resize operations for multiple widgets.
        
        Args:
            widgets: List of widgets to resize
            scale_factor: Scale factor to apply (1.0 = no change)
            
        Returns:
            List of update payloads for resizing widgets
        """
        operations = []
        
        for widget in widgets:
            # Handle Connector objects specially
            if isinstance(widget, Connector):
                # Connectors don't have size, but we can scale their line width
                if hasattr(widget, 'line_width'):
                    new_line_width = widget.line_width * scale_factor
                    operations.append({
                        'widget_id': widget.id,
                        'operation': 'resize',
                        'payload': {'line_width': new_line_width}
                    })
                continue
            
            # Handle regular widgets with size
            if not hasattr(widget, 'size') or not isinstance(widget.size, dict):
                continue
            
            current_width = widget.size.get('width', 100.0)
            current_height = widget.size.get('height', 100.0)
            
            new_size = {
                'width': current_width * scale_factor,
                'height': current_height * scale_factor
            }
            
            operations.append({
                'widget_id': widget.id,
                'operation': 'resize',
                'payload': {'size': new_size}
            })
        
        return operations
    
    def widgets_contain_id(
        self,
        widgets: List[Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]],
        target_id: str
    ) -> List[Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]]:
        """Find widgets that contain a widget with the specified ID.
        
        Args:
            widgets: List of widgets to check
            target_id: ID of the widget to find containers for
            
        Returns:
            List of widgets that contain the target widget
        """
        # Find the target widget
        target_widget = None
        for widget in widgets:
            if widget.id == target_id:
                target_widget = widget
                break
        
        if not target_widget:
            return []
        
        # Find widgets that contain the target
        containers = []
        for widget in widgets:
            if widget.id == target_id:
                continue
            
            try:
                if widget_contains(widget, target_widget):
                    containers.append(widget)
            except (ValueError, AttributeError):
                continue
        
        return containers
    
    def widgets_touch_id(
        self,
        widgets: List[Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]],
        target_id: str
    ) -> List[Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]]:
        """Find widgets that touch a widget with the specified ID.
        
        Args:
            widgets: List of widgets to check
            target_id: ID of the widget to find touching widgets for
            
        Returns:
            List of widgets that touch the target widget
        """
        # Find the target widget
        target_widget = None
        for widget in widgets:
            if widget.id == target_id:
                target_widget = widget
                break
        
        if not target_widget:
            return []
        
        # Find widgets that touch the target
        touching = []
        for widget in widgets:
            if widget.id == target_id:
                continue
            
            try:
                if widgets_touch(widget, target_widget):
                    touching.append(widget)
            except (ValueError, AttributeError):
                continue
        
        return touching


def create_spatial_group(
    widgets: List[Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]],
    tolerance: float = 10.0
) -> List[List[Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]]]:
    """Group widgets based on spatial proximity.
    
    Args:
        widgets: List of widgets to group
        tolerance: Distance tolerance for grouping
        
    Returns:
        List of widget groups
    """
    if not widgets:
        return []
    
    groups = []
    processed = set()
    
    for widget in widgets:
        if widget.id in processed:
            continue
        
        # Start a new group with this widget
        group = [widget]
        processed.add(widget.id)
        
        # Find all widgets that are close to this group
        changed = True
        while changed:
            changed = False
            for other_widget in widgets:
                if other_widget.id in processed:
                    continue
                
                # Check if this widget is close to any widget in the current group
                for group_widget in group:
                    try:
                        rect1 = widget_bounding_box(group_widget)
                        rect2 = widget_bounding_box(other_widget)
                        
                        # Check if widgets are within tolerance distance
                        if (abs(rect1.x - rect2.x) <= tolerance and 
                            abs(rect1.y - rect2.y) <= tolerance):
                            group.append(other_widget)
                            processed.add(other_widget.id)
                            changed = True
                            break
                    except (ValueError, AttributeError):
                        continue
        
        groups.append(group)
    
    return groups


def find_widget_clusters(
    widgets: List[Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]],
    min_cluster_size: int = 2,
    tolerance: float = 20.0
) -> List[List[Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]]]:
    """Find clusters of widgets that are spatially close to each other.
    
    Args:
        widgets: List of widgets to analyze
        min_cluster_size: Minimum number of widgets to form a cluster
        tolerance: Distance tolerance for clustering
        
    Returns:
        List of widget clusters
    """
    groups = create_spatial_group(widgets, tolerance)
    return [group for group in groups if len(group) >= min_cluster_size]


def calculate_widget_density(
    widgets: List[Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]],
    area: Rectangle
) -> float:
    """Calculate the density of widgets in a given area.
    
    Args:
        widgets: List of widgets to analyze
        area: Area to calculate density for
        
    Returns:
        Widget density (widgets per square unit)
    """
    if area.width <= 0 or area.height <= 0:
        return 0.0
    
    area_size = area.width * area.height
    widgets_in_area = 0
    
    for widget in widgets:
        try:
            widget_rect = widget_bounding_box(widget)
            if intersects(area, widget_rect):
                widgets_in_area += 1
        except (ValueError, AttributeError):
            continue
    
    return widgets_in_area / area_size if area_size > 0 else 0.0 