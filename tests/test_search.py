"""
Unit tests for cross-canvas search functionality.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from canvus_api.search import (
    SearchResult, CrossCanvasSearch, find_widgets_across_canvases,
    find_widgets_by_text, find_widgets_by_type, find_widgets_in_area
)
from canvus_api.geometry import Point, Size, Rectangle
from canvus_api.models import Widget, Note, Image, Canvas


class TestSearchResult:
    """Test SearchResult dataclass."""
    
    def test_search_result_creation(self):
        """Test creating a SearchResult."""
        widget = Widget(
            id="widget1",
            widget_type="note",
            location={"x": 100, "y": 200},
            size={"width": 50, "height": 30},
            state="normal"
        )
        
        result = SearchResult(
            canvas_id="canvas1",
            canvas_name="Test Canvas",
            widget_id="widget1",
            widget_type="note",
            widget=widget,
            match_score=0.8,
            match_reason="Text match"
        )
        
        assert result.canvas_id == "canvas1"
        assert result.canvas_name == "Test Canvas"
        assert result.widget_id == "widget1"
        assert result.widget_type == "note"
        assert result.widget == widget
        assert result.match_score == 0.8
        assert result.match_reason == "Text match"
    
    def test_drill_down_path(self):
        """Test drill_down_path property."""
        widget = Widget(
            id="widget1",
            widget_type="note",
            location={"x": 100, "y": 200},
            size={"width": 50, "height": 30},
            state="normal"
        )
        
        result = SearchResult(
            canvas_id="canvas1",
            canvas_name="Test Canvas",
            widget_id="widget1",
            widget_type="note",
            widget=widget
        )
        
        assert result.drill_down_path == "canvas1:widget1"
    
    def test_to_dict(self):
        """Test to_dict method."""
        widget = Widget(
            id="widget1",
            widget_type="note",
            location={"x": 100, "y": 200},
            size={"width": 50, "height": 30},
            state="normal"
        )
        
        result = SearchResult(
            canvas_id="canvas1",
            canvas_name="Test Canvas",
            widget_id="widget1",
            widget_type="note",
            widget=widget,
            match_score=0.8,
            match_reason="Text match"
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["canvas_id"] == "canvas1"
        assert result_dict["canvas_name"] == "Test Canvas"
        assert result_dict["widget_id"] == "widget1"
        assert result_dict["widget_type"] == "note"
        assert result_dict["drill_down_path"] == "canvas1:widget1"
        assert result_dict["match_score"] == 0.8
        assert result_dict["match_reason"] == "Text match"
        assert "widget_data" in result_dict


class TestCrossCanvasSearch:
    """Test CrossCanvasSearch class."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock client."""
        client = AsyncMock()
        return client
    
    @pytest.fixture
    def search_engine(self, mock_client):
        """Create a search engine with mock client."""
        return CrossCanvasSearch(mock_client)
    
    @pytest.fixture
    def sample_widgets(self):
        """Create sample widgets for testing."""
        return [
            Widget(
                id="widget1",
                widget_type="note",
                location={"x": 100, "y": 200},
                size={"width": 50, "height": 30},
                state="normal"
            ),
            Widget(
                id="widget2",
                widget_type="image",
                location={"x": 300, "y": 400},
                size={"width": 100, "height": 80},
                state="normal"
            ),
            Widget(
                id="widget3",
                widget_type="note",
                location={"x": 500, "y": 600},
                size={"width": 60, "height": 40},
                state="deleted"
            )
        ]
    
    @pytest.fixture
    def sample_canvases(self):
        """Create sample canvases for testing."""
        return [
            Canvas(
                id="canvas1", 
                name="Canvas 1", 
                access="public",
                asset_size=0,
                folder_id="",
                in_trash=False,
                mode="normal",
                state="active"
            ),
            Canvas(
                id="canvas2", 
                name="Canvas 2", 
                access="public",
                asset_size=0,
                folder_id="",
                in_trash=False,
                mode="normal",
                state="active"
            )
        ]
    
    def test_parse_query_dict(self, search_engine):
        """Test parsing dictionary query."""
        query = {"widget_type": "note", "location.x": 100}
        result = search_engine._parse_query(query)
        assert result == query
    
    def test_parse_query_string_json(self, search_engine):
        """Test parsing JSON string query."""
        query = '{"widget_type": "note", "location.x": 100}'
        result = search_engine._parse_query(query)
        assert result == {"widget_type": "note", "location.x": 100}
    
    def test_parse_query_string_text(self, search_engine):
        """Test parsing text string query."""
        query = "test text"
        result = search_engine._parse_query(query)
        assert result == {"text": "*test text*"}
    
    def test_parse_query_invalid_type(self, search_engine):
        """Test parsing invalid query type."""
        with pytest.raises(ValueError, match="Invalid query type"):
            search_engine._parse_query(123)
    
    def test_wildcard_match_exact(self, search_engine):
        """Test wildcard matching with exact match."""
        assert search_engine._wildcard_match("hello world", "hello world")
    
    def test_wildcard_match_prefix(self, search_engine):
        """Test wildcard matching with prefix wildcard."""
        assert search_engine._wildcard_match("hello world", "*world")
    
    def test_wildcard_match_suffix(self, search_engine):
        """Test wildcard matching with suffix wildcard."""
        assert search_engine._wildcard_match("hello world", "hello*")
    
    def test_wildcard_match_middle(self, search_engine):
        """Test wildcard matching with middle wildcard."""
        assert search_engine._wildcard_match("hello world", "h*o")
    
    def test_wildcard_match_case_insensitive(self, search_engine):
        """Test wildcard matching is case insensitive."""
        assert search_engine._wildcard_match("Hello World", "h*w")
    
    def test_wildcard_match_no_match(self, search_engine):
        """Test wildcard matching with no match."""
        assert not search_engine._wildcard_match("hello world", "goodbye*")
    
    def test_matches_criteria_exact(self, search_engine, sample_widgets):
        """Test exact criteria matching."""
        widget = sample_widgets[0]
        criteria = {"widget_type": "note", "location.x": 100}
        
        assert search_engine._matches_criteria(widget, criteria)
    
    def test_matches_criteria_wildcard(self, search_engine, sample_widgets):
        """Test wildcard criteria matching."""
        widget = sample_widgets[0]
        criteria = {"widget_type": "*ote*"}
        
        assert search_engine._matches_criteria(widget, criteria)
    
    def test_matches_criteria_no_match(self, search_engine, sample_widgets):
        """Test criteria matching with no match."""
        widget = sample_widgets[0]
        criteria = {"widget_type": "image"}
        
        assert not search_engine._matches_criteria(widget, criteria)
    
    def test_matches_criteria_missing_key(self, search_engine, sample_widgets):
        """Test criteria matching with missing key."""
        widget = sample_widgets[0]
        criteria = {"nonexistent_key": "value"}
        
        assert not search_engine._matches_criteria(widget, criteria)
    
    def test_apply_filters_no_filters(self, search_engine, sample_widgets):
        """Test applying no filters."""
        result = search_engine._apply_filters(
            sample_widgets, {}, None, None, False
        )
        
        assert len(result) == 2  # Excludes deleted widget
        assert result[0].id == "widget1"
        assert result[1].id == "widget2"
    
    def test_apply_filters_include_deleted(self, search_engine, sample_widgets):
        """Test applying filters with deleted widgets included."""
        result = search_engine._apply_filters(
            sample_widgets, {}, None, None, True
        )
        
        assert len(result) == 3  # Includes deleted widget
        assert result[2].id == "widget3"
    
    def test_apply_filters_widget_type(self, search_engine, sample_widgets):
        """Test applying widget type filter."""
        result = search_engine._apply_filters(
            sample_widgets, {}, ["note"], None, False
        )
        
        assert len(result) == 1
        assert result[0].widget_type == "note"
    
    def test_apply_filters_spatial(self, search_engine, sample_widgets):
        """Test applying spatial filter."""
        area = Rectangle(
            x=0, y=0, width=200, height=300
        )
        
        result = search_engine._apply_filters(
            sample_widgets, {}, None, area, False
        )
        
        assert len(result) == 1  # Only widget1 is in the area
        assert result[0].id == "widget1"
    
    def test_apply_filters_query(self, search_engine, sample_widgets):
        """Test applying query filter."""
        criteria = {"widget_type": "note"}
        
        result = search_engine._apply_filters(
            sample_widgets, criteria, None, None, False
        )
        
        assert len(result) == 1
        assert result[0].widget_type == "note"
    
    def test_calculate_match_score_exact(self, search_engine, sample_widgets):
        """Test calculating match score for exact match."""
        widget = sample_widgets[0]
        criteria = {"widget_type": "note"}
        
        score = search_engine._calculate_match_score(widget, criteria)
        assert score == 1.0
    
    def test_calculate_match_score_no_match(self, search_engine, sample_widgets):
        """Test calculating match score for no match."""
        widget = sample_widgets[0]
        criteria = {"widget_type": "image"}
        
        score = search_engine._calculate_match_score(widget, criteria)
        assert score == 0.0
    
    def test_calculate_match_score_no_criteria(self, search_engine, sample_widgets):
        """Test calculating match score with no criteria."""
        widget = sample_widgets[0]
        
        score = search_engine._calculate_match_score(widget, {})
        assert score == 1.0
    
    def test_get_match_reason_exact(self, search_engine, sample_widgets):
        """Test getting match reason for exact match."""
        widget = sample_widgets[0]
        criteria = {"widget_type": "note"}
        
        reason = search_engine._get_match_reason(widget, criteria)
        assert "Exact match on widget_type" in reason
    
    def test_get_match_reason_no_criteria(self, search_engine, sample_widgets):
        """Test getting match reason with no criteria."""
        widget = sample_widgets[0]
        
        reason = search_engine._get_match_reason(widget, {})
        assert reason == "No filter applied"
    
    @pytest.mark.asyncio
    async def test_get_canvases_to_search_specific(self, search_engine, mock_client, sample_canvases):
        """Test getting specific canvases to search."""
        mock_client.get_canvas.side_effect = sample_canvases
        
        result = await search_engine._get_canvases_to_search(["canvas1", "canvas2"])
        
        assert len(result) == 2
        assert result[0].id == "canvas1"
        assert result[1].id == "canvas2"
    
    @pytest.mark.asyncio
    async def test_get_canvases_to_search_all(self, search_engine, mock_client, sample_canvases):
        """Test getting all accessible canvases."""
        mock_client.list_canvases.return_value = sample_canvases
        
        result = await search_engine._get_canvases_to_search(None)
        
        assert len(result) == 2
        assert result[0].id == "canvas1"
        assert result[1].id == "canvas2"
    
    @pytest.mark.asyncio
    async def test_find_widgets_by_text(self, search_engine, mock_client, sample_canvases, sample_widgets):
        """Test finding widgets by text."""
        mock_client.list_canvases.return_value = sample_canvases
        mock_client.list_widgets.return_value = sample_widgets
        
        result = await search_engine.find_widgets_by_text("note")
        
        # Text search currently returns 0 results since widgets don't have text field
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_find_widgets_by_type(self, search_engine, mock_client, sample_canvases, sample_widgets):
        """Test finding widgets by type."""
        mock_client.list_canvases.return_value = sample_canvases
        mock_client.list_widgets.return_value = sample_widgets
        
        result = await search_engine.find_widgets_by_type("image")
        
        # Returns 2 results (one from each canvas)
        assert len(result) == 2
        assert result[0].widget_type == "image"
        assert result[1].widget_type == "image"
    
    @pytest.mark.asyncio
    async def test_find_widgets_in_area(self, search_engine, mock_client, sample_canvases, sample_widgets):
        """Test finding widgets in area."""
        mock_client.list_canvases.return_value = sample_canvases
        mock_client.list_widgets.return_value = sample_widgets
        
        area = Rectangle(x=0, y=0, width=200, height=300)
        
        result = await search_engine.find_widgets_in_area(area)
        
        assert len(result) == 1
        assert result[0].id == "widget1"
    
    @pytest.mark.asyncio
    async def test_find_widgets_by_property(self, search_engine, mock_client, sample_canvases, sample_widgets):
        """Test finding widgets by property."""
        mock_client.list_canvases.return_value = sample_canvases
        mock_client.list_widgets.return_value = sample_widgets
        
        result = await search_engine.find_widgets_by_property("location.x", 100)
        
        assert len(result) == 1
        assert result[0].id == "widget1"
    
    @pytest.mark.asyncio
    async def test_find_widgets_across_canvases_complex(self, search_engine, mock_client, sample_canvases, sample_widgets):
        """Test complex cross-canvas search."""
        mock_client.list_canvases.return_value = sample_canvases
        mock_client.list_widgets.return_value = sample_widgets
        
        query = {"widget_type": "note", "location.x": 100}
        
        result = await search_engine.find_widgets_across_canvases(
            query, max_results=10
        )
        
        assert len(result) == 1
        assert result[0].widget_type == "note"
        assert result[0].match_score == 1.0
    
    @pytest.mark.asyncio
    async def test_find_widgets_across_canvases_max_results(self, search_engine, mock_client, sample_canvases, sample_widgets):
        """Test cross-canvas search with max results limit."""
        mock_client.list_canvases.return_value = sample_canvases
        mock_client.list_widgets.return_value = sample_widgets
        
        result = await search_engine.find_widgets_across_canvases(
            {}, max_results=1
        )
        
        assert len(result) == 1
    
    @pytest.mark.asyncio
    async def test_find_widgets_across_canvases_error_handling(self, search_engine, mock_client, sample_canvases):
        """Test error handling in cross-canvas search."""
        mock_client.list_canvases.return_value = sample_canvases
        mock_client.list_widgets.side_effect = Exception("API Error")
        
        result = await search_engine.find_widgets_across_canvases({})
        
        assert len(result) == 0


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock client."""
        client = AsyncMock()
        return client
    
    @pytest.mark.asyncio
    async def test_find_widgets_across_canvases_function(self, mock_client):
        """Test find_widgets_across_canvases convenience function."""
        # Mock the search engine
        with patch('canvus_api.search.CrossCanvasSearch') as mock_search_class:
            mock_search_engine = AsyncMock()
            mock_search_class.return_value = mock_search_engine
            mock_search_engine.find_widgets_across_canvases.return_value = []
            
            result = await find_widgets_across_canvases(mock_client, {"widget_type": "note"})
            
            mock_search_class.assert_called_once_with(mock_client)
            mock_search_engine.find_widgets_across_canvases.assert_called_once()
            assert result == []
    
    @pytest.mark.asyncio
    async def test_find_widgets_by_text_function(self, mock_client):
        """Test find_widgets_by_text convenience function."""
        with patch('canvus_api.search.CrossCanvasSearch') as mock_search_class:
            mock_search_engine = AsyncMock()
            mock_search_class.return_value = mock_search_engine
            mock_search_engine.find_widgets_by_text.return_value = []
            
            result = await find_widgets_by_text(mock_client, "test")
            
            mock_search_class.assert_called_once_with(mock_client)
            mock_search_engine.find_widgets_by_text.assert_called_once_with("test", None, False, 100)
            assert result == []
    
    @pytest.mark.asyncio
    async def test_find_widgets_by_type_function(self, mock_client):
        """Test find_widgets_by_type convenience function."""
        with patch('canvus_api.search.CrossCanvasSearch') as mock_search_class:
            mock_search_engine = AsyncMock()
            mock_search_class.return_value = mock_search_engine
            mock_search_engine.find_widgets_by_type.return_value = []
            
            result = await find_widgets_by_type(mock_client, "note")
            
            mock_search_class.assert_called_once_with(mock_client)
            mock_search_engine.find_widgets_by_type.assert_called_once_with("note", None, 100)
            assert result == []
    
    @pytest.mark.asyncio
    async def test_find_widgets_in_area_function(self, mock_client):
        """Test find_widgets_in_area convenience function."""
        area = Rectangle(x=0, y=0, width=100, height=100)
        
        with patch('canvus_api.search.CrossCanvasSearch') as mock_search_class:
            mock_search_engine = AsyncMock()
            mock_search_class.return_value = mock_search_engine
            mock_search_engine.find_widgets_in_area.return_value = []
            
            result = await find_widgets_in_area(mock_client, area)
            
            mock_search_class.assert_called_once_with(mock_client)
            mock_search_engine.find_widgets_in_area.assert_called_once_with(area, None, None, 100)
            assert result == [] 