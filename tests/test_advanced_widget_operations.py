"""
Tests for advanced widget operations including spatial grouping, batch operations, and zone management.
"""

import pytest
from canvus_api.widget_operations import (
    WidgetZoneManager, BatchWidgetOperations, SpatialTolerance,
    create_spatial_group, find_widget_clusters, calculate_widget_density
)
from canvus_api.models import (
    Note, Image, Browser, Connector, WidgetZone
)
from canvus_api.geometry import Rectangle


class TestAdvancedWidgetOperations:
    """Test advanced widget operations functionality."""

    @pytest.fixture
    def sample_widgets(self):
        """Create sample widgets for testing."""
        return [
            Note(
                id="note1",
                state="normal",
                widget_type="Note",
                location={"x": 100, "y": 100},
                size={"width": 200, "height": 150},
                text="Test note 1"
            ),
            Note(
                id="note2",
                state="normal",
                widget_type="Note",
                location={"x": 350, "y": 100},
                size={"width": 200, "height": 150},
                text="Test note 2"
            ),
            Image(
                id="image1",
                state="normal",
                widget_type="Image",
                location={"x": 100, "y": 300},
                size={"width": 300, "height": 200},
                hash="test_hash_1"
            ),
            Browser(
                id="browser1",
                state="normal",
                widget_type="Browser",
                location={"x": 450, "y": 300},
                size={"width": 400, "height": 300},
                url="https://example.com"
            )
        ]

    @pytest.fixture
    def sample_connector(self):
        """Create a sample connector for testing."""
        from canvus_api.models import ConnectorEndpoint
        
        return Connector(
            id="connector1",
            state="normal",
            widget_type="Connector",
            src=ConnectorEndpoint(
                auto_location=False,
                id="note1",
                rel_location={"x": 200, "y": 175},
                tip="none"
            ),
            dst=ConnectorEndpoint(
                auto_location=False,
                id="note2",
                rel_location={"x": 450, "y": 175},
                tip="solid-equilateral-triangle"
            ),
            line_color="#e7e7f2ff",
            line_width=5.0,
            type="curve"
        )

    def test_spatial_tolerance_initialization(self):
        """Test SpatialTolerance initialization."""
        tolerance = SpatialTolerance()
        assert tolerance.position_tolerance == 5.0
        assert tolerance.size_tolerance == 2.0
        assert tolerance.overlap_tolerance == 1.0
        assert tolerance.distance_tolerance == 10.0

        # Test custom values
        custom_tolerance = SpatialTolerance(
            position_tolerance=10.0,
            size_tolerance=5.0,
            overlap_tolerance=2.0,
            distance_tolerance=20.0
        )
        assert custom_tolerance.position_tolerance == 10.0
        assert custom_tolerance.size_tolerance == 5.0
        assert custom_tolerance.overlap_tolerance == 2.0
        assert custom_tolerance.distance_tolerance == 20.0

    def test_widget_zone_manager_initialization(self):
        """Test WidgetZoneManager initialization."""
        manager = WidgetZoneManager()
        assert isinstance(manager.tolerance, SpatialTolerance)

        custom_tolerance = SpatialTolerance(position_tolerance=15.0)
        manager = WidgetZoneManager(tolerance=custom_tolerance)
        assert manager.tolerance.position_tolerance == 15.0

    def test_create_zone_from_widgets(self, sample_widgets):
        """Test creating a zone from widgets."""
        manager = WidgetZoneManager()
        
        zone = manager.create_zone_from_widgets(
            sample_widgets, 
            name="Test Zone",
            description="A test zone",
            padding=10.0
        )
        
        assert isinstance(zone, WidgetZone)
        assert zone.name == "Test Zone"
        assert zone.description == "A test zone"
        assert "x" in zone.location
        assert "y" in zone.location
        assert "width" in zone.size
        assert "height" in zone.size
        assert zone.size["width"] > 0
        assert zone.size["height"] > 0

    def test_create_zone_from_empty_widgets(self):
        """Test creating a zone from empty widget list."""
        manager = WidgetZoneManager()
        
        with pytest.raises(ValueError, match="Cannot create zone from empty widget list"):
            manager.create_zone_from_widgets([], "Test Zone")

    def test_widgets_in_zone(self, sample_widgets):
        """Test finding widgets in a zone."""
        manager = WidgetZoneManager()
        
        # Create a zone that contains some widgets
        zone = WidgetZone(
            id="test_zone",
            name="Test Zone",
            location={"x": 50, "y": 50},
            size={"width": 400, "height": 400}
        )
        
        widgets_in_zone = manager.widgets_in_zone(sample_widgets, zone)
        
        # Should find widgets that are completely within the zone
        assert len(widgets_in_zone) > 0
        for widget in widgets_in_zone:
            # Skip Connector objects which don't have location
            if not isinstance(widget, Connector) and hasattr(widget, 'location'):
                assert widget.location["x"] >= zone.location["x"]
                assert widget.location["y"] >= zone.location["y"]

    def test_widgets_touching_zone(self, sample_widgets):
        """Test finding widgets that touch a zone."""
        manager = WidgetZoneManager()
        
        # Create a zone
        zone = WidgetZone(
            id="test_zone",
            name="Test Zone",
            location={"x": 200, "y": 200},
            size={"width": 100, "height": 100}
        )
        
        touching_widgets = manager.widgets_touching_zone(sample_widgets, zone)
        
        # Should find widgets that touch or overlap the zone
        assert isinstance(touching_widgets, list)

    def test_batch_widget_operations_initialization(self):
        """Test BatchWidgetOperations initialization."""
        operations = BatchWidgetOperations()
        assert isinstance(operations.tolerance, SpatialTolerance)

        custom_tolerance = SpatialTolerance(distance_tolerance=25.0)
        operations = BatchWidgetOperations(tolerance=custom_tolerance)
        assert operations.tolerance.distance_tolerance == 25.0

    def test_move_widgets(self, sample_widgets):
        """Test generating move operations for widgets."""
        operations = BatchWidgetOperations()
        
        move_ops = operations.move_widgets(sample_widgets, offset_x=50, offset_y=25)
        
        assert len(move_ops) == len(sample_widgets)
        for op in move_ops:
            assert "widget_id" in op
            assert "operation" in op
            assert "payload" in op
            assert op["operation"] == "move"
            assert "location" in op["payload"]

    def test_move_connector(self, sample_connector):
        """Test moving a connector widget."""
        operations = BatchWidgetOperations()
        
        move_ops = operations.move_widgets([sample_connector], offset_x=30, offset_y=20)
        
        assert len(move_ops) == 1
        op = move_ops[0]
        assert op["widget_id"] == "connector1"
        assert op["operation"] == "move"
        assert "src" in op["payload"]
        assert "dst" in op["payload"]

    def test_resize_widgets(self, sample_widgets):
        """Test generating resize operations for widgets."""
        operations = BatchWidgetOperations()
        
        resize_ops = operations.resize_widgets(sample_widgets, scale_factor=1.5)
        
        assert len(resize_ops) == len(sample_widgets)
        for op in resize_ops:
            assert "widget_id" in op
            assert "operation" in op
            assert "payload" in op
            assert op["operation"] == "resize"
            assert "size" in op["payload"]

    def test_resize_connector(self, sample_connector):
        """Test resizing a connector widget."""
        operations = BatchWidgetOperations()
        
        resize_ops = operations.resize_widgets([sample_connector], scale_factor=2.0)
        
        assert len(resize_ops) == 1
        op = resize_ops[0]
        assert op["widget_id"] == "connector1"
        assert op["operation"] == "resize"
        assert "line_width" in op["payload"]
        assert op["payload"]["line_width"] == 10.0  # 5.0 * 2.0

    def test_widgets_contain_id(self, sample_widgets):
        """Test finding widgets that contain a specific widget."""
        operations = BatchWidgetOperations()
        
        # Create a large widget that contains a smaller one
        large_widget = Note(
            id="large_note",
            state="normal",
            widget_type="Note",
            location={"x": 50, "y": 50},
            size={"width": 500, "height": 400},
            text="Large note"
        )
        
        all_widgets = sample_widgets + [large_widget]
        containers = operations.widgets_contain_id(all_widgets, "note1")
        
        # Should find widgets that contain note1
        assert isinstance(containers, list)

    def test_widgets_touch_id(self, sample_widgets):
        """Test finding widgets that touch a specific widget."""
        operations = BatchWidgetOperations()
        
        touching = operations.widgets_touch_id(sample_widgets, "note1")
        
        # Should find widgets that touch note1
        assert isinstance(touching, list)

    def test_widgets_touch_id_nonexistent(self, sample_widgets):
        """Test finding widgets that touch a nonexistent widget."""
        operations = BatchWidgetOperations()
        
        touching = operations.widgets_touch_id(sample_widgets, "nonexistent_id")
        
        # Should return empty list for nonexistent widget
        assert touching == []

    def test_create_spatial_group(self, sample_widgets):
        """Test creating spatial groups from widgets."""
        groups = create_spatial_group(sample_widgets, tolerance=50.0)
        
        assert isinstance(groups, list)
        assert len(groups) > 0
        
        # Each group should be a list of widgets
        for group in groups:
            assert isinstance(group, list)
            assert len(group) > 0

    def test_create_spatial_group_empty(self):
        """Test creating spatial groups from empty widget list."""
        groups = create_spatial_group([], tolerance=50.0)
        
        assert groups == []

    def test_find_widget_clusters(self, sample_widgets):
        """Test finding widget clusters."""
        clusters = find_widget_clusters(sample_widgets, min_cluster_size=2, tolerance=100.0)
        
        assert isinstance(clusters, list)
        
        # Each cluster should have at least min_cluster_size widgets
        for cluster in clusters:
            assert len(cluster) >= 2

    def test_find_widget_clusters_no_clusters(self, sample_widgets):
        """Test finding clusters when none exist."""
        # Use very small tolerance to ensure no clusters form
        clusters = find_widget_clusters(sample_widgets, min_cluster_size=2, tolerance=1.0)
        
        assert clusters == []

    def test_calculate_widget_density(self, sample_widgets):
        """Test calculating widget density in an area."""
        area = Rectangle(x=0, y=0, width=1000, height=1000)
        
        density = calculate_widget_density(sample_widgets, area)
        
        assert isinstance(density, float)
        assert density >= 0.0

    def test_calculate_widget_density_empty_area(self, sample_widgets):
        """Test calculating density in an empty area."""
        area = Rectangle(x=0, y=0, width=0, height=0)
        
        density = calculate_widget_density(sample_widgets, area)
        
        assert density == 0.0

    def test_calculate_widget_density_no_widgets(self):
        """Test calculating density with no widgets."""
        area = Rectangle(x=0, y=0, width=100, height=100)
        
        density = calculate_widget_density([], area)
        
        assert density == 0.0

    def test_widget_zone_properties(self):
        """Test WidgetZone model properties."""
        zone = WidgetZone(
            id="test_zone",
            name="Test Zone",
            description="A test zone",
            location={"x": 100, "y": 100},
            size={"width": 200, "height": 150},
            color="#ff0000ff",
            background_color="#00ff00ff",
            opacity=0.5,
            visible=True,
            locked=False,
            tolerance=10.0
        )
        
        assert zone.id == "test_zone"
        assert zone.name == "Test Zone"
        assert zone.description == "A test zone"
        assert zone.location["x"] == 100
        assert zone.location["y"] == 100
        assert zone.size["width"] == 200
        assert zone.size["height"] == 150
        assert zone.color == "#ff0000ff"
        assert zone.background_color == "#00ff00ff"
        assert zone.opacity == 0.5
        assert zone.visible is True
        assert zone.locked is False
        assert zone.tolerance == 10.0 