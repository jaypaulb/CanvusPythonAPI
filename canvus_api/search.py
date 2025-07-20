"""
Cross-canvas widget search functionality.

This module provides advanced search capabilities across multiple canvases,
leveraging the geometry utilities for comprehensive widget discovery.
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from .client import CanvusClient
from .geometry import Rectangle
from .models import BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector


@dataclass
class SearchResult:
    """Result of a cross-canvas widget search."""
    
    canvas_id: str
    canvas_name: str
    widget_id: str
    widget_type: str
    widget: Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector]
    match_score: float = 1.0
    match_reason: str = ""
    
    @property
    def drill_down_path(self) -> str:
        """Get the full drill-down path for this result."""
        return f"{self.canvas_id}:{self.widget_id}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert search result to dictionary."""
        return {
            "canvas_id": self.canvas_id,
            "canvas_name": self.canvas_name,
            "widget_id": self.widget_id,
            "widget_type": self.widget_type,
            "drill_down_path": self.drill_down_path,
            "match_score": self.match_score,
            "match_reason": self.match_reason,
            "widget_data": self.widget.model_dump() if hasattr(self.widget, 'model_dump') else dict(self.widget)
        }


class CrossCanvasSearch:
    """Cross-canvas widget search functionality."""
    
    def __init__(self, client: CanvusClient):
        """Initialize the search engine with a client.
        
        Args:
            client: CanvusClient instance for API access
        """
        self.client = client
    
    async def find_widgets_across_canvases(
        self,
        query: Union[str, Dict[str, Any]],
        canvas_ids: Optional[List[str]] = None,
        widget_types: Optional[List[str]] = None,
        spatial_filter: Optional[Rectangle] = None,
        max_results: int = 100,
        include_deleted: bool = False
    ) -> List[SearchResult]:
        """
        Find widgets across multiple canvases using complex queries.
        
        Args:
            query: Search query as string or dictionary
            canvas_ids: List of canvas IDs to search (None for all accessible canvases)
            widget_types: List of widget types to include (None for all types)
            spatial_filter: Optional spatial filter to limit search area
            max_results: Maximum number of results to return
            include_deleted: Whether to include deleted widgets
            
        Returns:
            List of SearchResult objects with full drill-down paths
            
        Raises:
            ValueError: If query is invalid
            CanvusAPIError: If API request fails
        """
        # Parse and validate query
        filter_criteria = self._parse_query(query)
        
        # Get canvases to search
        canvases = await self._get_canvases_to_search(canvas_ids)
        
        results = []
        
        for canvas in canvases:
            try:
                # Get widgets from this canvas
                widgets = await self.client.list_widgets(canvas.id)
                
                # Apply filters
                filtered_widgets = self._apply_filters(
                    widgets, filter_criteria, widget_types, spatial_filter, include_deleted
                )
                
                # Convert to search results
                for widget in filtered_widgets:
                    result = SearchResult(
                        canvas_id=canvas.id,
                        canvas_name=canvas.name,
                        widget_id=widget.id,
                        widget_type=widget.widget_type,
                        widget=widget,
                        match_score=self._calculate_match_score(widget, filter_criteria),
                        match_reason=self._get_match_reason(widget, filter_criteria)
                    )
                    results.append(result)
                    
                    # Check if we've reached max results
                    if len(results) >= max_results:
                        break
                
                if len(results) >= max_results:
                    break
                    
            except Exception as e:
                # Log error but continue with other canvases
                print(f"Error searching canvas {canvas.id}: {e}")
                continue
        
        # Sort by match score (highest first)
        results.sort(key=lambda r: r.match_score, reverse=True)
        
        return results[:max_results]
    
    async def find_widgets_by_text(
        self,
        text: str,
        canvas_ids: Optional[List[str]] = None,
        case_sensitive: bool = False,
        max_results: int = 100
    ) -> List[SearchResult]:
        """
        Find widgets containing specific text across canvases.
        
        Args:
            text: Text to search for
            canvas_ids: List of canvas IDs to search (None for all accessible canvases)
            case_sensitive: Whether search should be case sensitive
            max_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects
        """
        # Create text filter
        if case_sensitive:
            filter_criteria = {"text": text}
        else:
            filter_criteria = {"text": f"*{text}*"}
        
        return await self.find_widgets_across_canvases(
            filter_criteria, canvas_ids, max_results=max_results
        )
    
    async def find_widgets_by_type(
        self,
        widget_type: str,
        canvas_ids: Optional[List[str]] = None,
        max_results: int = 100
    ) -> List[SearchResult]:
        """
        Find widgets of a specific type across canvases.
        
        Args:
            widget_type: Type of widget to search for
            canvas_ids: List of canvas IDs to search (None for all accessible canvases)
            max_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects
        """
        filter_criteria = {"widget_type": widget_type}
        
        return await self.find_widgets_across_canvases(
            filter_criteria, canvas_ids, max_results=max_results
        )
    
    async def find_widgets_in_area(
        self,
        area: Rectangle,
        canvas_ids: Optional[List[str]] = None,
        widget_types: Optional[List[str]] = None,
        max_results: int = 100
    ) -> List[SearchResult]:
        """
        Find widgets in a specific spatial area across canvases.
        
        Args:
            area: Rectangle defining the search area
            canvas_ids: List of canvas IDs to search (None for all accessible canvases)
            widget_types: List of widget types to include (None for all types)
            max_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects
        """
        return await self.find_widgets_across_canvases(
            {}, canvas_ids, widget_types, area, max_results
        )
    
    async def find_widgets_by_property(
        self,
        property_path: str,
        value: Any,
        canvas_ids: Optional[List[str]] = None,
        max_results: int = 100
    ) -> List[SearchResult]:
        """
        Find widgets with specific property values across canvases.
        
        Args:
            property_path: JSONPath-like property path (e.g., "location.x", "size.width")
            value: Value to search for
            canvas_ids: List of canvas IDs to search (None for all accessible canvases)
            max_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects
        """
        filter_criteria = {property_path: value}
        
        return await self.find_widgets_across_canvases(
            filter_criteria, canvas_ids, max_results=max_results
        )
    
    def _parse_query(self, query: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Parse and validate search query.
        
        Args:
            query: Query as string or dictionary
            
        Returns:
            Dictionary of filter criteria
            
        Raises:
            ValueError: If query is invalid
        """
        if isinstance(query, dict):
            return query
        elif isinstance(query, str):
            # Try to parse as JSON or create simple text filter
            try:
                import json
                query_dict = json.loads(query)
                return query_dict
            except (json.JSONDecodeError, ValueError):
                # Treat as text search
                return {"text": f"*{query}*"}
        else:
            raise ValueError(f"Invalid query type: {type(query)}")
    
    async def _get_canvases_to_search(self, canvas_ids: Optional[List[str]]) -> List[Any]:
        """Get list of canvases to search.
        
        Args:
            canvas_ids: List of canvas IDs or None for all accessible canvases
            
        Returns:
            List of canvas objects
        """
        if canvas_ids:
            # Get specific canvases
            canvases = []
            for canvas_id in canvas_ids:
                try:
                    canvas = await self.client.get_canvas(canvas_id)
                    canvases.append(canvas)
                except Exception as e:
                    print(f"Error getting canvas {canvas_id}: {e}")
                    continue
            return canvases
        else:
            # Get all accessible canvases
            return await self.client.list_canvases()
    
    def _apply_filters(
        self,
        widgets: List[Any],
        filter_criteria: Dict[str, Any],
        widget_types: Optional[List[str]],
        spatial_filter: Optional[Rectangle],
        include_deleted: bool
    ) -> List[Any]:
        """Apply all filters to widget list.
        
        Args:
            widgets: List of widgets to filter
            filter_criteria: Dictionary of filter criteria to apply
            widget_types: List of allowed widget types
            spatial_filter: Optional spatial filter
            include_deleted: Whether to include deleted widgets
            
        Returns:
            Filtered list of widgets
        """
        filtered_widgets = []
        
        for widget in widgets:
            # Skip deleted widgets unless requested
            if not include_deleted and getattr(widget, 'state', 'normal') == 'deleted':
                continue
            
            # Apply widget type filter
            if widget_types:
                widget_type_lower = widget.widget_type.lower()
                widget_types_lower = [wt.lower() for wt in widget_types]
                if widget_type_lower not in widget_types_lower:
                    continue
            
            # Apply spatial filter
            if spatial_filter:
                try:
                    from .geometry import widget_bounding_box, intersects
                    widget_rect = widget_bounding_box(widget)
                    if not intersects(widget_rect, spatial_filter):
                        continue
                except Exception:
                    # Skip widgets that can't be spatially filtered
                    continue
            
            # Apply query filter
            if filter_criteria and not self._matches_criteria(widget, filter_criteria):
                continue
            
            filtered_widgets.append(widget)
        
        return filtered_widgets
    
    def _matches_criteria(
        self,
        widget: Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector],
        criteria: Dict[str, Any]
    ) -> bool:
        """Check if widget matches the given criteria.
        
        Args:
            widget: Widget to check
            criteria: Dictionary of criteria to match against
            
        Returns:
            True if widget matches criteria, False otherwise
        """
        try:
            widget_dict = widget.model_dump() if hasattr(widget, 'model_dump') else dict(widget)
            
            for key, value in criteria.items():
                # Handle nested properties (e.g., "location.x")
                if '.' in key:
                    parts = key.split('.')
                    current = widget_dict
                    for part in parts:
                        if isinstance(current, dict) and part in current:
                            current = current[part]
                        else:
                            return False
                    widget_value = current
                else:
                    if key not in widget_dict:
                        return False
                    widget_value = widget_dict[key]
                
                # Handle wildcard matching
                if isinstance(value, str) and '*' in value:
                    if not self._wildcard_match(str(widget_value), value):
                        return False
                elif str(widget_value) != str(value):
                    # Special case: widget_type should be case-insensitive
                    if key == "widget_type":
                        if str(widget_value).lower() != str(value).lower():
                            return False
                    else:
                        # Try numeric comparison for numbers
                        try:
                            widget_float = float(widget_value) if isinstance(widget_value, (int, float, str)) else None
                            value_float = float(value) if isinstance(value, (int, float, str)) else None
                            if widget_float is not None and value_float is not None:
                                if widget_float != value_float:
                                    return False
                            else:
                                return False
                        except (ValueError, TypeError):
                            return False
            
            return True
        except Exception:
            return False
    
    def _wildcard_match(self, text: str, pattern: str) -> bool:
        """Check if text matches wildcard pattern.
        
        Args:
            text: Text to check
            pattern: Wildcard pattern (supports * for any characters)
            
        Returns:
            True if text matches pattern, False otherwise
        """
        import re
        
        # Convert wildcard pattern to regex
        regex_pattern = pattern.replace('*', '.*')
        return re.search(regex_pattern, text, re.IGNORECASE) is not None
    
    def _calculate_match_score(
        self,
        widget: Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector],
        filter_criteria: Dict[str, Any]
    ) -> float:
        """Calculate match score for a widget.
        
        Args:
            widget: Widget to score
            filter_criteria: Filter criteria used for matching
            
        Returns:
            Match score between 0.0 and 1.0
        """
        if not filter_criteria:
            return 1.0
        
        # For now, return 1.0 for exact matches, 0.5 for partial matches
        # This can be enhanced with more sophisticated scoring
        try:
            if self._matches_criteria(widget, filter_criteria):
                return 1.0
            else:
                return 0.0
        except Exception:
            return 0.0
    
    def _get_match_reason(
        self,
        widget: Union[BaseWidget, Widget, Note, Image, Browser, Video, PDF, Anchor, Connector],
        filter_criteria: Dict[str, Any]
    ) -> str:
        """Get reason why widget matched the filter.
        
        Args:
            widget: Widget that matched
            filter_criteria: Filter criteria used for matching
            
        Returns:
            Human-readable match reason
        """
        if not filter_criteria:
            return "No filter applied"
        
        try:
            # Try to identify which part of the filter matched
            widget_dict = widget.model_dump() if hasattr(widget, 'model_dump') else dict(widget)
            
            for key, value in filter_criteria.items():
                if key in widget_dict:
                    if str(widget_dict[key]) == str(value):
                        return f"Exact match on {key}"
                    elif str(value) in str(widget_dict[key]):
                        return f"Partial match on {key}"
            
            return "Filter criteria matched"
        except Exception:
            return "Unknown match reason"


# Convenience functions for easy access
async def find_widgets_across_canvases(
    client: CanvusClient,
    query: Union[str, Dict[str, Any]],
    canvas_ids: Optional[List[str]] = None,
    widget_types: Optional[List[str]] = None,
    spatial_filter: Optional[Rectangle] = None,
    max_results: int = 100,
    include_deleted: bool = False
) -> List[SearchResult]:
    """
    Convenience function for cross-canvas widget search.
    
    Args:
        client: CanvusClient instance
        query: Search query as string or dictionary
        canvas_ids: List of canvas IDs to search (None for all accessible canvases)
        widget_types: List of widget types to include (None for all types)
        spatial_filter: Optional spatial filter to limit search area
        max_results: Maximum number of results to return
        include_deleted: Whether to include deleted widgets
        
    Returns:
        List of SearchResult objects
    """
    search_engine = CrossCanvasSearch(client)
    return await search_engine.find_widgets_across_canvases(
        query, canvas_ids, widget_types, spatial_filter, max_results, include_deleted
    )


async def find_widgets_by_text(
    client: CanvusClient,
    text: str,
    canvas_ids: Optional[List[str]] = None,
    case_sensitive: bool = False,
    max_results: int = 100
) -> List[SearchResult]:
    """
    Convenience function for text-based widget search.
    
    Args:
        client: CanvusClient instance
        text: Text to search for
        canvas_ids: List of canvas IDs to search (None for all accessible canvases)
        case_sensitive: Whether search should be case sensitive
        max_results: Maximum number of results to return
        
    Returns:
        List of SearchResult objects
    """
    search_engine = CrossCanvasSearch(client)
    return await search_engine.find_widgets_by_text(
        text, canvas_ids, case_sensitive, max_results
    )


async def find_widgets_by_type(
    client: CanvusClient,
    widget_type: str,
    canvas_ids: Optional[List[str]] = None,
    max_results: int = 100
) -> List[SearchResult]:
    """
    Convenience function for type-based widget search.
    
    Args:
        client: CanvusClient instance
        widget_type: Type of widget to search for
        canvas_ids: List of canvas IDs to search (None for all accessible canvases)
        max_results: Maximum number of results to return
        
    Returns:
        List of SearchResult objects
    """
    search_engine = CrossCanvasSearch(client)
    return await search_engine.find_widgets_by_type(
        widget_type, canvas_ids, max_results
    )


async def find_widgets_in_area(
    client: CanvusClient,
    area: Rectangle,
    canvas_ids: Optional[List[str]] = None,
    widget_types: Optional[List[str]] = None,
    max_results: int = 100
) -> List[SearchResult]:
    """
    Convenience function for spatial widget search.
    
    Args:
        client: CanvusClient instance
        area: Rectangle defining the search area
        canvas_ids: List of canvas IDs to search (None for all accessible canvases)
        widget_types: List of widget types to include (None for all types)
        max_results: Maximum number of results to return
        
    Returns:
        List of SearchResult objects
    """
    search_engine = CrossCanvasSearch(client)
    return await search_engine.find_widgets_in_area(
        area, canvas_ids, widget_types, max_results
    ) 