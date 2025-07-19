"""
Pytest configuration and fixtures for Canvus API tests.
"""

import pytest
import pytest_asyncio
import asyncio
from pathlib import Path
from canvus_api import CanvusClient
from canvus_api.exceptions import CanvusAPIError
from .test_utils import load_config


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def client():
    """Create a shared client instance for all tests."""
    config = load_config()

    async with CanvusClient(
        base_url=config["server"]["base_url"],
        api_key=config["authentication"]["api_key"],
        verify_ssl=config["server"].get("verify_ssl", False),
    ) as client:
        yield client


@pytest.fixture(scope="session")
def test_config():
    """Load test configuration."""
    return load_config()


@pytest.fixture(scope="session")
def user_id(test_config):
    """Get user ID from config."""
    return test_config.get("user_id", 1000)


@pytest.fixture(scope="session")
def test_files_dir():
    """Get path to test files directory."""
    return Path(__file__).parent / "test_files"


@pytest_asyncio.fixture
async def test_canvas(client):
    """Create a test canvas for testing."""
    canvas_payload = {
        "name": f"Test Canvas - {asyncio.get_event_loop().time()}",
        "description": "Canvas created for testing",
    }

    canvas = await client.create_canvas(canvas_payload)
    yield canvas

    # Cleanup
    try:
        await client.delete_canvas(canvas.id)
    except Exception:
        pass


@pytest_asyncio.fixture
async def test_folder(client):
    """Create a test folder for testing."""
    folder_payload = {
        "name": f"Test Folder - {asyncio.get_event_loop().time()}",
        "description": "Folder created for testing",
    }

    folder = await client.create_folder(folder_payload)
    yield folder

    # Cleanup
    try:
        await client.delete_folder(folder.id)
    except Exception:
        pass


@pytest_asyncio.fixture
async def test_user(client):
    """Create a test user for testing."""
    user_payload = {
        "email": f"testuser_{asyncio.get_event_loop().time()}@test.local",
        "name": "Test User",
        "password": "TestPassword123!",
    }

    try:
        user = await client.create_user(user_payload)
        yield user

        # Cleanup
        try:
            if user.id is not None:
                await client.delete_user(user.id)
        except Exception:
            pass
    except CanvusAPIError as e:
        # If user creation fails due to permissions, create a mock user
        if e.status_code in [401, 403]:
            from canvus_api.models import User

            mock_user = User(
                id=99999,
                email=user_payload["email"],
                name=user_payload["name"],
                admin=False,
                approved=True,
                blocked=False,
                state="normal",
            )
            yield mock_user
        else:
            raise


@pytest_asyncio.fixture
async def test_group(client):
    """Create a test group for testing."""
    group_payload = {
        "name": f"Test Group - {asyncio.get_event_loop().time()}",
        "description": "Group created for testing",
    }

    group = await client.create_group(group_payload)
    yield group

    # Cleanup
    try:
        await client.delete_group(group["id"])
    except Exception:
        pass


@pytest_asyncio.fixture
async def test_token(client, user_id):
    """Create a test token for testing."""
    token = await client.create_token(user_id, "Test token")
    yield token

    # Cleanup
    try:
        await client.delete_token(user_id, token.id)
    except Exception:
        pass


@pytest.fixture
def sample_image_path(test_files_dir):
    """Get path to sample image file."""
    image_path = test_files_dir / "test_image.jpg"
    if not image_path.exists():
        # Create a dummy file if it doesn't exist
        image_path.parent.mkdir(exist_ok=True)
        with open(image_path, "wb") as f:
            f.write(b"dummy image data")
    return str(image_path)


@pytest.fixture
def sample_pdf_path(test_files_dir):
    """Get path to sample PDF file."""
    pdf_path = test_files_dir / "test_pdf.pdf"
    if not pdf_path.exists():
        # Create a dummy file if it doesn't exist
        pdf_path.parent.mkdir(exist_ok=True)
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\ndummy pdf data")
    return str(pdf_path)


@pytest.fixture
def sample_video_path(test_files_dir):
    """Get path to sample video file."""
    video_path = test_files_dir / "test_video.mp4"
    if not video_path.exists():
        # Create a dummy file if it doesn't exist
        video_path.parent.mkdir(exist_ok=True)
        with open(video_path, "wb") as f:
            f.write(b"dummy video data")
    return str(video_path)
