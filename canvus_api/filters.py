"""
Advanced filtering system for Canvus API widgets and canvases.
"""

from typing import Dict, Any, List, Optional, Union
from enum import Enum
import re
from .geometry import Rectangle, intersects, contains


class FilterOperator(Enum):
    """Supported filter operators."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    IN = "in"
    NOT_IN = "not_in"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"
    SPATIAL_INTERSECTS = "spatial_intersects"
    SPATIAL_CONTAINS = "spatial_contains"
    SPATIAL_WITHIN = "spatial_within"
    WILDCARD_MATCH = "wildcard_match"


class Filter:
    """
    Advanced filter for querying widgets and canvases.
    
    Supports complex filtering with multiple conditions, spatial operations,
    and wildcard matching.
    """
    
    def __init__(self, conditions: Optional[List[Dict[str, Any]]] = None):
        """
        Initialize a filter with optional conditions.
        
        Args:
            conditions: List of filter conditions
        """
        self.conditions = conditions or []
    
    def add_condition(self, field: str, operator: Union[str, FilterOperator], value: Any) -> 'Filter':
        """
        Add a filter condition.
        
        Args:
            field: Field to filter on (supports dot notation for nested fields)
            operator: Filter operator
            value: Value to compare against
            
        Returns:
            Self for chaining
        """
        if isinstance(operator, str):
            operator = FilterOperator(operator)
        
        self.conditions.append({
            "field": field,
            "operator": operator.value,
            "value": value
        })
        return self
    
    def add_spatial_condition(self, operator: str, area: Rectangle) -> 'Filter':
        """
        Add a spatial filter condition.
        
        Args:
            operator: Spatial operator (intersects, contains, within)
            area: Rectangle defining the spatial area
            
        Returns:
            Self for chaining
        """
        self.conditions.append({
            "field": "spatial",
            "operator": f"spatial_{operator}",
            "value": area
        })
        return self
    
    def add_wildcard_condition(self, field: str, pattern: str) -> 'Filter':
        """
        Add a wildcard filter condition.
        
        Args:
            field: Field to filter on
            pattern: Wildcard pattern (* for any sequence, ? for single character)
            
        Returns:
            Self for chaining
        """
        self.conditions.append({
            "field": field,
            "operator": "wildcard_match",
            "value": pattern
        })
        return self
    
    def matches(self, item: Dict[str, Any]) -> bool:
        """
        Check if an item matches all filter conditions.
        
        Args:
            item: Item to check (widget or canvas dict)
            
        Returns:
            True if item matches all conditions
        """
        for condition in self.conditions:
            if not self._matches_condition(item, condition):
                return False
        return True
    
    def _matches_condition(self, item: Dict[str, Any], condition: Dict[str, Any]) -> bool:
        """Check if item matches a single condition."""
        field = condition["field"]
        operator = condition["operator"]
        value = condition["value"]
        
        # Handle spatial conditions
        if field == "spatial" and operator.startswith("spatial_"):
            return self._matches_spatial_condition(item, operator, value)
        
        # Get field value (support dot notation)
        field_value = self._get_nested_value(item, field)
        
        # Handle different operators
        if operator == FilterOperator.EQUALS.value:
            return field_value == value
        elif operator == FilterOperator.NOT_EQUALS.value:
            return field_value != value
        elif operator == FilterOperator.CONTAINS.value:
            return value in field_value if field_value else False
        elif operator == FilterOperator.NOT_CONTAINS.value:
            return value not in field_value if field_value else True
        elif operator == FilterOperator.STARTS_WITH.value:
            return str(field_value).startswith(str(value)) if field_value else False
        elif operator == FilterOperator.ENDS_WITH.value:
            return str(field_value).endswith(str(value)) if field_value else False
        elif operator == FilterOperator.GREATER_THAN.value:
            return field_value > value if field_value is not None else False
        elif operator == FilterOperator.LESS_THAN.value:
            return field_value < value if field_value is not None else False
        elif operator == FilterOperator.GREATER_EQUAL.value:
            return field_value >= value if field_value is not None else False
        elif operator == FilterOperator.LESS_EQUAL.value:
            return field_value <= value if field_value is not None else False
        elif operator == FilterOperator.IN.value:
            return field_value in value if field_value is not None else False
        elif operator == FilterOperator.NOT_IN.value:
            return field_value not in value if field_value is not None else True
        elif operator == FilterOperator.EXISTS.value:
            return field_value is not None
        elif operator == FilterOperator.NOT_EXISTS.value:
            return field_value is None
        elif operator == FilterOperator.WILDCARD_MATCH.value:
            return self._matches_wildcard(field_value, value)
        else:
            return False
    
    def _get_nested_value(self, item: Dict[str, Any], field: str) -> Any:
        """Get nested field value using dot notation."""
        if "." not in field:
            return item.get(field)
        
        parts = field.split(".")
        current = item
        
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
            
            if current is None:
                break
        
        return current
    
    def _matches_spatial_condition(self, item: Dict[str, Any], operator: str, area: Rectangle) -> bool:
        """Check spatial condition."""
        # Get widget location and size
        location = item.get("location")
        size = item.get("size")
        
        if not location or not size:
            return False
        
        # Create widget rectangle
        widget_rect = Rectangle(
            x=location["x"],
            y=location["y"],
            width=size["width"],
            height=size["height"]
        )
        
        if operator == "spatial_intersects":
            return intersects(widget_rect, area)
        elif operator == "spatial_contains":
            return intersects(area, widget_rect)
        elif operator == "spatial_within":
            return contains(area, widget_rect)
        else:
            return False
    
    def _matches_wildcard(self, field_value: Any, pattern: str) -> bool:
        """Check wildcard pattern match."""
        if field_value is None:
            return False
        
        # Convert pattern to regex
        regex_pattern = pattern.replace("*", ".*").replace("?", ".")
        try:
            return bool(re.match(regex_pattern, str(field_value), re.IGNORECASE))
        except re.error:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert filter to dictionary representation."""
        return {
            "conditions": self.conditions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Filter':
        """Create filter from dictionary representation."""
        return cls(conditions=data.get("conditions", []))


def create_filter() -> Filter:
    """
    Create a new empty filter.
    
    Returns:
        New Filter instance
    """
    return Filter()


def create_spatial_filter(area: Rectangle, operator: str = "intersects") -> Filter:
    """
    Create a spatial filter.
    
    Args:
        area: Rectangle defining the spatial area
        operator: Spatial operator (intersects, contains, within)
        
    Returns:
        Filter with spatial condition
    """
    return Filter().add_spatial_condition(operator, area)


def create_widget_type_filter(widget_types: Union[str, List[str]]) -> Filter:
    """
    Create a filter for specific widget types.
    
    Args:
        widget_types: Widget type(s) to filter for
        
    Returns:
        Filter for widget types
    """
    if isinstance(widget_types, str):
        widget_types = [widget_types]
    
    return Filter().add_condition("type", FilterOperator.IN, widget_types)


def create_text_filter(text: str, fields: Optional[List[str]] = None) -> Filter:
    """
    Create a text search filter.
    
    Args:
        text: Text to search for
        fields: Fields to search in (default: title, text, description)
        
    Returns:
        Filter for text search
    """
    if fields is None:
        fields = ["title", "text", "description"]
    
    filter_obj = Filter()
    
    for field in fields:
        filter_obj.add_condition(field, FilterOperator.CONTAINS, text)
    
    return filter_obj


def create_wildcard_filter(pattern: str, field: str = "title") -> Filter:
    """
    Create a wildcard filter.
    
    Args:
        pattern: Wildcard pattern (* for any sequence, ? for single character)
        field: Field to apply pattern to
        
    Returns:
        Filter with wildcard condition
    """
    return Filter().add_wildcard_condition(field, pattern)


def combine_filters(*filters: Filter, operator: str = "AND") -> Filter:
    """
    Combine multiple filters with logical operator.
    
    Args:
        *filters: Filters to combine
        operator: Logical operator (AND, OR)
        
    Returns:
        Combined filter
    """
    if not filters:
        return Filter()
    
    if len(filters) == 1:
        return filters[0]
    
    # For now, we'll use AND logic by combining all conditions
    # In a more advanced implementation, we could support OR logic
    combined = Filter()
    for filter_obj in filters:
        combined.conditions.extend(filter_obj.conditions)
    
    return combined 