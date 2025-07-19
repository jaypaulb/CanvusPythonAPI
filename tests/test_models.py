"""
Test Pydantic models for validation.
"""

from datetime import datetime
from canvus_api.models import (
    Group,
    GroupMember,
    VideoInput,
    VideoOutput,
    LicenseInfo,
    AuditLogEntry,
    MipmapInfo,
    Annotation,
)


class TestGroup:
    """Test Group model validation."""

    def test_group_creation(self):
        """Test creating a Group with required fields."""
        group_data = {
            "id": "group-123",
            "name": "Test Group",
        }
        group = Group(**group_data)
        assert group.id == "group-123"
        assert group.name == "Test Group"
        assert group.description is None

    def test_group_with_optional_fields(self):
        """Test creating a Group with optional fields."""
        group_data = {
            "id": "group-456",
            "name": "Test Group with Description",
            "description": "A test group",
            "member_count": 5,
        }
        group = Group(**group_data)
        assert group.id == "group-456"
        assert group.name == "Test Group with Description"
        assert group.description == "A test group"
        assert group.member_count == 5


class TestGroupMember:
    """Test GroupMember model validation."""

    def test_group_member_creation(self):
        """Test creating a GroupMember with required fields."""
        member_data = {
            "id": "user-123",
            "name": "Test User",
            "email": "test@example.com",
        }
        member = GroupMember(**member_data)
        assert member.id == "user-123"
        assert member.name == "Test User"
        assert member.email == "test@example.com"
        assert member.admin is False
        assert member.approved is True
        assert member.blocked is False


class TestVideoInput:
    """Test VideoInput model validation."""

    def test_video_input_creation(self):
        """Test creating a VideoInput with required fields."""
        video_input_data = {
            "id": "input-123",
            "name": "Test Video Input",
            "source": "camera-1",
            "location": {"x": 100.0, "y": 200.0},
            "size": {"width": 640.0, "height": 480.0},
        }
        video_input = VideoInput(**video_input_data)
        assert video_input.id == "input-123"
        assert video_input.name == "Test Video Input"
        assert video_input.source == "camera-1"
        assert video_input.location == {"x": 100.0, "y": 200.0}
        assert video_input.size == {"width": 640.0, "height": 480.0}
        assert video_input.depth == 1
        assert video_input.scale == 1.0
        assert video_input.pinned is False


class TestVideoOutput:
    """Test VideoOutput model validation."""

    def test_video_output_creation(self):
        """Test creating a VideoOutput with required fields."""
        video_output_data = {
            "id": "output-123",
            "name": "Test Video Output",
        }
        video_output = VideoOutput(**video_output_data)
        assert video_output.id == "output-123"
        assert video_output.name == "Test Video Output"
        assert video_output.source is None
        assert video_output.enabled is True

    def test_video_output_with_config(self):
        """Test creating a VideoOutput with configuration."""
        video_output_data = {
            "id": "output-456",
            "name": "HD Output",
            "source": "canvas-1",
            "enabled": True,
            "resolution": "1920x1080",
            "refresh_rate": 60,
        }
        video_output = VideoOutput(**video_output_data)
        assert video_output.id == "output-456"
        assert video_output.name == "HD Output"
        assert video_output.source == "canvas-1"
        assert video_output.resolution == "1920x1080"
        assert video_output.refresh_rate == 60


class TestLicenseInfo:
    """Test LicenseInfo model validation."""

    def test_license_info_creation(self):
        """Test creating a LicenseInfo with required fields."""
        license_data = {
            "status": "valid",
        }
        license_info = LicenseInfo(**license_data)
        assert license_info.status == "valid"
        assert license_info.license_key is None
        assert license_info.is_valid is True
        assert license_info.has_expired is False

    def test_license_info_with_details(self):
        """Test creating a LicenseInfo with detailed information."""
        license_data = {
            "license_key": "TEST-KEY-1234",
            "status": "valid",
            "type": "lifetime",
            "edition": "professional",
            "features": ["feature1", "feature2"],
            "max_users": 100,
            "max_canvases": 50,
            "max_clients": 10,
        }
        license_info = LicenseInfo(**license_data)
        assert license_info.license_key == "TEST-KEY-1234"
        assert license_info.status == "valid"
        assert license_info.type == "lifetime"
        assert license_info.edition == "professional"
        assert license_info.features == ["feature1", "feature2"]
        assert license_info.max_users == 100
        assert license_info.max_canvases == 50
        assert license_info.max_clients == 10


class TestAuditLogEntry:
    """Test AuditLogEntry model validation."""

    def test_audit_log_entry_creation(self):
        """Test creating an AuditLogEntry with required fields."""
        timestamp = datetime.now()
        entry_data = {
            "id": "log-123",
            "timestamp": timestamp,
            "action": "user_login",
        }
        entry = AuditLogEntry(**entry_data)
        assert entry.id == "log-123"
        assert entry.timestamp == timestamp
        assert entry.action == "user_login"
        assert entry.user_id is None
        assert entry.resource_type is None

    def test_audit_log_entry_with_details(self):
        """Test creating an AuditLogEntry with detailed information."""
        timestamp = datetime.now()
        entry_data = {
            "id": "log-456",
            "timestamp": timestamp,
            "user_id": "user-123",
            "user_email": "user@example.com",
            "action": "canvas_created",
            "resource_type": "canvas",
            "resource_id": "canvas-123",
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0...",
        }
        entry = AuditLogEntry(**entry_data)
        assert entry.id == "log-456"
        assert entry.timestamp == timestamp
        assert entry.user_id == "user-123"
        assert entry.user_email == "user@example.com"
        assert entry.action == "canvas_created"
        assert entry.resource_type == "canvas"
        assert entry.resource_id == "canvas-123"
        assert entry.ip_address == "192.168.1.1"
        assert entry.user_agent == "Mozilla/5.0..."


class TestMipmapInfo:
    """Test MipmapInfo model validation."""

    def test_mipmap_info_creation(self):
        """Test creating a MipmapInfo with required fields."""
        mipmap_data = {
            "public_hash_hex": "abc123def456",
            "canvas_id": "canvas-123",
        }
        mipmap_info = MipmapInfo(**mipmap_data)
        assert mipmap_info.public_hash_hex == "abc123def456"
        assert mipmap_info.canvas_id == "canvas-123"
        assert mipmap_info.levels == []
        assert mipmap_info.format is None

    def test_mipmap_info_with_details(self):
        """Test creating a MipmapInfo with detailed information."""
        mipmap_data = {
            "public_hash_hex": "def789ghi012",
            "canvas_id": "canvas-456",
            "levels": [0, 1, 2, 3],
            "format": "webp",
            "width": 1920,
            "height": 1080,
        }
        mipmap_info = MipmapInfo(**mipmap_data)
        assert mipmap_info.public_hash_hex == "def789ghi012"
        assert mipmap_info.canvas_id == "canvas-456"
        assert mipmap_info.levels == [0, 1, 2, 3]
        assert mipmap_info.format == "webp"
        assert mipmap_info.width == 1920
        assert mipmap_info.height == 1080


class TestAnnotation:
    """Test Annotation model validation."""

    def test_annotation_creation(self):
        """Test creating an Annotation with required fields."""
        annotation_data = {
            "id": "annotation-123",
            "widget_id": "widget-123",
            "type": "comment",
            "content": "This is a test comment",
        }
        annotation = Annotation(**annotation_data)
        assert annotation.id == "annotation-123"
        assert annotation.widget_id == "widget-123"
        assert annotation.type == "comment"
        assert annotation.content == "This is a test comment"
        assert annotation.author_id is None
        assert annotation.position is None

    def test_annotation_with_details(self):
        """Test creating an Annotation with detailed information."""
        annotation_data = {
            "id": "annotation-456",
            "widget_id": "widget-456",
            "type": "highlight",
            "content": "Important section",
            "author_id": "user-123",
            "author_name": "Test User",
            "position": {"x": 100.0, "y": 200.0},
            "color": "#ff0000",
        }
        annotation = Annotation(**annotation_data)
        assert annotation.id == "annotation-456"
        assert annotation.widget_id == "widget-456"
        assert annotation.type == "highlight"
        assert annotation.content == "Important section"
        assert annotation.author_id == "user-123"
        assert annotation.author_name == "Test User"
        assert annotation.position == {"x": 100.0, "y": 200.0}
        assert annotation.color == "#ff0000"
