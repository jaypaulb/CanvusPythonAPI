"""
Client-side filtering system for the Canvus API.

This module provides a powerful filtering system that supports arbitrary JSON criteria,
wildcards, and JSONPath-like selectors for filtering canvases, widgets, and other resources.
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field


class Filter(BaseModel):
    """Provides generic, client-side filtering for SDK list/get endpoints.
    
    Supports arbitrary JSON criteria, wildcards ("*"), and JSONPath-like selectors ("$").
    
    Example:
        >>> filter = Filter({
        ...     "widget_type": "browser",
        ...     "url": "*12345",  # Wildcard suffix
        ...     "$.location.x": 100.0,  # JSONPath selector
        ... })
        >>> widgets = await client.list_widgets(canvas_id, filter=filter)
    """
    
    criteria: Dict[str, Any] = Field(
        description="Arbitrary filter criteria with support for wildcards and JSONPath selectors"
    )
    
    def match(self, obj: Dict[str, Any]) -> bool:
        """Check if the given object matches the filter criteria.
        
        Supports wildcards ("*"), prefix/suffix wildcards (e.g., "*123", "abc*"), 
        and JSONPath-like selectors ("$.field").
        
        Args:
            obj: Object to check against the filter criteria
            
        Returns:
            True if the object matches all criteria, False otherwise
            
        Example:
            >>> filter = Filter({"name": "My Canvas", "widget_type": "*"})
            >>> widget = {"name": "My Canvas", "widget_type": "note"}
            >>> filter.match(widget)
            True
        """
        for key, value in self.criteria.items():
            actual_value = self._get_value_by_path(obj, key)
            if not self._matches_value(actual_value, value):
                return False
        return True
    
    def _get_value_by_path(self, obj: Dict[str, Any], path: str) -> Any:
        """Get a value from a nested object using JSONPath-like selector.
        
        Args:
            obj: Object to search in
            path: Path to the value (e.g., "name", "$.location.x")
            
        Returns:
            Value at the specified path, or None if not found
        """
        if path.startswith("$."):
            # JSONPath-like selector
            return self._get_by_json_path(obj, path[2:])
        else:
            # Direct key access
            return obj.get(path)
    
    def _get_by_json_path(self, obj: Dict[str, Any], path: str) -> Any:
        """Get a value from a nested object using dot notation.
        
        Args:
            obj: Object to search in
            path: Dot-separated path (e.g., "location.x")
            
        Returns:
            Value at the specified path, or None if not found
        """
        parts = path.split(".")
        current = obj
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current
    
    def _matches_value(self, actual: Any, expected: Any) -> bool:
        """Check if actual value matches expected value with wildcard support.
        
        Args:
            actual: Actual value from the object
            expected: Expected value from filter criteria
            
        Returns:
            True if values match, False otherwise
        """
        # Handle wildcard matching
        if expected == "*":
            return True  # Wildcard matches any value
        
        # Handle string wildcards
        if isinstance(expected, str) and isinstance(actual, str):
            if expected.startswith("*") and expected.endswith("*"):
                # Contains match: "*mid*"
                needle = expected[1:-1]
                return needle in actual
            elif expected.startswith("*"):
                # Suffix match: "*123"
                needle = expected[1:]
                return actual.endswith(needle)
            elif expected.endswith("*"):
                # Prefix match: "abc*"
                needle = expected[:-1]
                return actual.startswith(needle)
        
        # Handle list wildcards
        if isinstance(expected, str) and isinstance(actual, list):
            if expected.startswith("*") and expected.endswith("*"):
                # Contains match: "*mid*"
                needle = expected[1:-1]
                return any(needle in str(item) for item in actual)
            elif expected.startswith("*"):
                # Suffix match: "*123"
                needle = expected[1:]
                return any(str(item).endswith(needle) for item in actual)
            elif expected.endswith("*"):
                # Prefix match: "abc*"
                needle = expected[:-1]
                return any(str(item).startswith(needle) for item in actual)
        
        # Exact match
        return actual == expected


def filter_list(items: List[Dict[str, Any]], filter_obj: Optional[Filter]) -> List[Dict[str, Any]]:
    """Filter a list of items using the provided filter.
    
    Args:
        items: List of items to filter
        filter_obj: Filter to apply, or None to return all items
        
    Returns:
        Filtered list of items
        
    Example:
        >>> widgets = [
        ...     {"id": "1", "widget_type": "note", "text": "Hello"},
        ...     {"id": "2", "widget_type": "browser", "url": "https://example.com"},
        ... ]
        >>> filter_obj = Filter({"widget_type": "note"})
        >>> filtered = filter_list(widgets, filter_obj)
        >>> len(filtered)
        1
    """
    if filter_obj is None:
        return items
    
    return [item for item in items if filter_obj.match(item)]


def create_filter(**criteria) -> Filter:
    """Create a Filter object from keyword arguments.
    
    Args:
        **criteria: Filter criteria as keyword arguments
        
    Returns:
        Filter object
        
    Example:
        >>> filter_obj = create_filter(
        ...     widget_type="browser",
        ...     url="*dashboard*"
        ... )
        >>> print(filter_obj.criteria)
        {'widget_type': 'browser', 'url': '*dashboard*'}
    """
    return Filter(criteria=criteria)


def create_spatial_filter(
    x: Optional[float] = None,
    y: Optional[float] = None,
    width: Optional[float] = None,
    height: Optional[float] = None
) -> Filter:
    """Create a filter for spatial properties.
    
    Args:
        x: X coordinate filter
        y: Y coordinate filter
        width: Width filter
        height: Height filter
        
    Returns:
        Filter object for spatial properties
        
    Example:
        >>> filter_obj = create_spatial_filter(x=100.0, width="*")
        >>> print(filter_obj.criteria)
        {'$.location.x': 100.0, '$.size.width': '*'}
    """
    criteria = {}
    
    if x is not None:
        criteria["$.location.x"] = x
    if y is not None:
        criteria["$.location.y"] = y
    if width is not None:
        criteria["$.size.width"] = width
    if height is not None:
        criteria["$.size.height"] = height
    
    return Filter(criteria=criteria)


def create_widget_type_filter(widget_types: Union[str, List[str]]) -> Filter:
    """Create a filter for widget types.
    
    Args:
        widget_types: Single widget type or list of widget types
        
    Returns:
        Filter object for widget types
        
    Example:
        >>> filter_obj = create_widget_type_filter(["note", "browser"])
        >>> print(filter_obj.criteria)
        {'widget_type': ['note', 'browser']}
    """
    if isinstance(widget_types, str):
        return Filter(criteria={"widget_type": widget_types})
    
    return Filter(criteria={"widget_type": widget_types})


def create_text_filter(text: str, fields: Optional[List[str]] = None) -> Filter:
    """Create a filter for text content in specified fields.
    
    Args:
        text: Text to search for
        fields: Fields to search in (default: ["text", "title", "name"])
        
    Returns:
        Filter object for text search
        
    Example:
        >>> filter_obj = create_text_filter("dashboard", ["text", "title"])
        >>> print(filter_obj.criteria)
        {'text': '*dashboard*', 'title': '*dashboard*'}
    """
    if fields is None:
        fields = ["text", "title", "name"]
    
    criteria = {}
    for field in fields:
        criteria[field] = f"*{text}*"
    
    return Filter(criteria=criteria) 