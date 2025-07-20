"""Test circular parenting check and position offsetting functionality."""

import pytest
from unittest.mock import AsyncMock
from canvus_api.client import CanvusClient
from canvus_api.exceptions import CanvusAPIError
from canvus_api.models import Widget

pytestmark = pytest.mark.asyncio


class TestCircularParenting:
    """Test circular parenting detection and prevention."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return CanvusClient("https://test.com", "test-key")

    @pytest.fixture
    def mock_widgets(self):
        """Create mock widgets for testing."""
        return [
            Widget(
                id="widget-1",
                widget_type="Note",
                location={"x": 100, "y": 100},
                size={"width": 200, "height": 100},
                parent_id=None,
            ),
            Widget(
                id="widget-2",
                widget_type="Note",
                location={"x": 300, "y": 300},
                size={"width": 200, "height": 100},
                parent_id="widget-1",
            ),
            Widget(
                id="widget-3",
                widget_type="Note",
                location={"x": 500, "y": 500},
                size={"width": 200, "height": 100},
                parent_id="widget-2",
            ),
        ]

    async def test_circular_parenting_self_reference(self, client):
        """Test that setting a widget as its own parent is rejected."""
        with pytest.raises(
            CanvusAPIError, match="Cannot set widget.*as its own parent"
        ):
            await client._check_circular_parenting("canvas-1", "widget-1", "widget-1")

    async def test_circular_parenting_direct_cycle(self, client, mock_widgets):
        """Test that direct circular parenting is detected."""
        client.list_widgets = AsyncMock(return_value=mock_widgets)

        # Try to set widget-1 as parent of widget-2, which would create a cycle
        with pytest.raises(CanvusAPIError, match="Circular parenting detected"):
            await client._check_circular_parenting("canvas-1", "widget-2", "widget-1")

    async def test_circular_parenting_indirect_cycle(self, client, mock_widgets):
        """Test that indirect circular parenting is detected."""
        client.list_widgets = AsyncMock(return_value=mock_widgets)

        # Try to set widget-1 as parent of widget-3, which would create a cycle
        with pytest.raises(CanvusAPIError, match="Circular parenting detected"):
            await client._check_circular_parenting("canvas-1", "widget-3", "widget-1")

    async def test_valid_parenting(self, client, mock_widgets):
        """Test that valid parenting is allowed."""
        client.list_widgets = AsyncMock(return_value=mock_widgets)

        # This should not raise an exception
        await client._check_circular_parenting("canvas-1", "widget-1", "widget-2")

    def test_calculate_parent_offset(self, client):
        """Test the parent offset calculation formula."""
        current_location = {"x": 1000, "y": 500}
        parent_location = {"x": 200, "y": 100}

        offset = client._calculate_parent_offset(current_location, parent_location)

        # Formula: current_location - parent_location - 30
        expected_x = 1000 - 200 - 30  # 770
        expected_y = 500 - 100 - 30  # 370

        assert offset["x"] == expected_x
        assert offset["y"] == expected_y

    def test_calculate_parent_offset_with_negative_values(self, client):
        """Test offset calculation with negative parent coordinates."""
        current_location = {"x": 100, "y": 100}
        parent_location = {"x": -200, "y": -300}

        offset = client._calculate_parent_offset(current_location, parent_location)

        # Formula: current_location - parent_location - 30
        expected_x = 100 - (-200) - 30  # 270
        expected_y = 100 - (-300) - 30  # 370

        assert offset["x"] == expected_x
        assert offset["y"] == expected_y

    async def test_update_widget_with_parent_id(self, client):
        """Test that update_widget applies circular parenting check and offsetting."""
        # Mock the necessary methods
        client._check_circular_parenting = AsyncMock()
        client.get_widget = AsyncMock()
        client._request = AsyncMock()

        # Mock widget responses
        current_widget = Widget(
            id="widget-1",
            widget_type="Note",
            location={"x": 1000, "y": 500},
            size={"width": 200, "height": 100},
            parent_id=None,
        )
        parent_widget = Widget(
            id="widget-2",
            widget_type="Note",
            location={"x": 200, "y": 100},
            size={"width": 200, "height": 100},
            parent_id=None,
        )

        client.get_widget.side_effect = [current_widget, parent_widget]
        client._request.return_value = current_widget

        # Test payload with parent_id change
        payload = {"parent_id": "widget-2"}

        await client.update_widget("canvas-1", "widget-1", payload)

        # Verify circular parenting check was called
        client._check_circular_parenting.assert_called_once_with(
            "canvas-1", "widget-1", "widget-2"
        )

        # Verify the payload was modified with calculated offset
        # Expected offset: (1000-200-30, 500-100-30) = (770, 370)
        expected_location = {"x": 770, "y": 370}
        assert payload["location"] == expected_location

    async def test_update_widget_without_parent_id(self, client):
        """Test that update_widget doesn't apply checks when parent_id is not changed."""
        client._check_circular_parenting = AsyncMock()
        client.get_widget = AsyncMock()
        client._request = AsyncMock()

        payload = {"title": "New Title"}

        await client.update_widget("canvas-1", "widget-1", payload)

        # Verify circular parenting check was NOT called
        client._check_circular_parenting.assert_not_called()

        # Verify payload was not modified
        assert "location" not in payload
