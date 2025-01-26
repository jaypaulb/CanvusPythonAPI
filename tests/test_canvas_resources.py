"""
Test suite for Canvus canvas resources (widgets, content, etc.).
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Optional, Tuple

# Add the tests directory to Python path
test_dir = Path(__file__).parent
if str(test_dir) not in sys.path:
    sys.path.append(str(test_dir))

# Ensure test_files directory exists
test_files_dir = test_dir / "test_files"
if not test_files_dir.exists():
    test_files_dir.mkdir(exist_ok=True)

from canvus_api import CanvusClient, CanvusAPIError
from test_utils import (
    print_success, print_error, print_info, 
    print_warning, print_header, load_config
)

async def create_test_token(client: CanvusClient, user_id: int) -> Tuple[str, str]:
    """Create a test token for running tests.
    
    Returns:
        Tuple[str, str]: Token ID and plain token value
    """
    print_header("Creating Test Token")
    token = await client.create_token(user_id, "Test Suite Token")
    print_success(f"Created test token: {token.id}")
    return token.id, token.plain_token

async def test_note_operations(client: CanvusClient, canvas_id: str) -> None:
    """Test note CRUD operations."""
    print_header("Testing Note Operations")
    
    note_id = None
    try:
        # Create note
        note = await client.create_note(canvas_id, {
            "text": "Test note content",
            "title": "Test Note",
            "location": {"x": 100, "y": 100},
            "size": {"width": 300, "height": 200}
        })
        note_id = note.id
        print_success(f"Created note: {note.id}")
        
        # Get note
        retrieved = await client.get_note(canvas_id, note.id)
        print_success(f"Retrieved note: {retrieved.id}")
        
        # Update note
        updated = await client.update_note(canvas_id, note.id, {
            "text": "Updated content",
            "location": {"x": 150, "y": 150}
        })
        print_success(f"Updated note: {updated.id}")
        
        # List notes
        notes = await client.list_notes(canvas_id)
        print_success(f"Listed notes: {len(notes)} found")
        
        # Delete note
        await client.delete_note(canvas_id, note.id)
        print_success(f"Deleted note: {note.id}")
        
    except Exception as e:
        print_error(f"Note operations error: {e}")
        if note_id:
            try:
                await client.delete_note(canvas_id, note_id)
            except:
                pass

async def test_image_operations(client: CanvusClient, canvas_id: str) -> None:
    """Test image operations."""
    image_id = None
    downloaded_path = None
    try:
        # Create an image
        image_payload = {
            "location": {"x": 200, "y": 200},
            "size": {"width": 400, "height": 300}
        }
        image = await client.create_image(canvas_id, "tests/test_files/test_image.jpg", image_payload)
        image_id = image.id
        print_success(f"Created image with ID: {image_id}")

        # Get image details
        image = await client.get_image(canvas_id, image_id)
        print_success(f"Retrieved image details: {image}")

        # Download image
        content = await client.download_image(canvas_id, image_id)
        downloaded_path = "tests/test_files/downloaded_image.jpg"
        with open(downloaded_path, "wb") as f:
            f.write(content)
        print_success(f"Downloaded image to {downloaded_path}")

        # Update image
        update_payload = {
            "location": {"x": 250, "y": 250}
        }
        image = await client.update_image(canvas_id, image_id, update_payload)
        print_success(f"Updated image location: {image}")

        # List images
        images = await client.list_images(canvas_id)
        print_success(f"Listed {len(images)} images")

    except Exception as e:
        print_error(f"Error in image operations: {e}")
        raise
    finally:
        # Clean up
        if image_id:
            try:
                await client.delete_image(canvas_id, image_id)
                print_success("Deleted test image")
            except Exception as e:
                print_error(f"Error deleting image: {e}")

        if downloaded_path and os.path.exists(downloaded_path):
            try:
                os.remove(downloaded_path)
                print_success("Cleaned up downloaded image")
            except Exception as e:
                print_error(f"Error cleaning up downloaded image: {e}")

async def test_browser_operations(client: CanvusClient, canvas_id: str) -> None:
    """Test browser CRUD operations."""
    print_header("Testing Browser Operations")
    
    browser_id = None
    try:
        # Create browser
        browser = await client.create_browser(canvas_id, {
            "url": "https://www.example.com",
            "location": {"x": 300, "y": 300},
            "size": {"width": 800, "height": 600}
        })
        browser_id = browser.id
        print_success(f"Created browser: {browser.id}")
        
        # Get browser
        retrieved = await client.get_browser(canvas_id, browser.id)
        print_success(f"Retrieved browser: {retrieved.id}")
        
        # Update browser
        updated = await client.update_browser(canvas_id, browser.id, {
            "url": "https://www.google.com",
            "location": {"x": 350, "y": 350}
        })
        print_success(f"Updated browser: {updated.id}")
        
        # List browsers
        browsers = await client.list_browsers(canvas_id)
        print_success(f"Listed browsers: {len(browsers)} found")
        
        # Delete browser
        await client.delete_browser(canvas_id, browser.id)
        print_success(f"Deleted browser: {browser.id}")
        
    except Exception as e:
        print_error(f"Browser operations error: {e}")
        if browser_id:
            try:
                await client.delete_browser(canvas_id, browser_id)
            except:
                pass

async def test_connector_operations(client: CanvusClient, canvas_id: str) -> None:
    """Test connector CRUD operations."""
    print_header("Testing Connector Operations")
    
    note_id = None
    connector_id = None
    try:
        # First create a note to connect to
        note = await client.create_note(canvas_id, {
            "text": "Test note for connector",
            "location": {"x": 100, "y": 100},
            "size": {"width": 200, "height": 150}
        })
        note_id = note.id
        
        # Create connector
        connector = await client.create_connector(canvas_id, {
            "src": {
                "id": note.id,
                "rel_location": {"x": 0, "y": 0.5},
                "tip": "none",
                "auto_location": False
            },
            "dst": {
                "id": note.id,
                "rel_location": {"x": 1, "y": 0.5},
                "tip": "solid-equilateral-triangle",
                "auto_location": False
            },
            "line_color": "#000000ff",
            "line_width": 2.0,
            "type": "curve"
        })
        connector_id = connector.id
        print_success(f"Created connector: {connector.id}")
        
        # Get connector
        retrieved = await client.get_connector(canvas_id, connector.id)
        print_success(f"Retrieved connector: {retrieved.id}")
        
        # Update connector
        updated = await client.update_connector(canvas_id, connector.id, {
            "line_color": "#ff0000ff"
        })
        print_success(f"Updated connector: {updated.id}")
        
        # List connectors
        connectors = await client.list_connectors(canvas_id)
        print_success(f"Listed connectors: {len(connectors)} found")
        
        # Delete connector
        await client.delete_connector(canvas_id, connector.id)
        print_success(f"Deleted connector: {connector.id}")
        connector_id = None  # Mark as deleted so we don't try to delete again
        
    except Exception as e:
        print_error(f"Connector operations error: {e}")
    finally:
        if connector_id:
            try:
                await client.delete_connector(canvas_id, connector_id)
            except:
                pass
        if note_id:
            try:
                await client.delete_note(canvas_id, note_id)
            except:
                pass

async def test_video_operations(client: CanvusClient, canvas_id: str) -> None:
    """Test video operations."""
    video_id = None
    downloaded_path = None
    try:
        # Create a video
        video_payload = {
            "location": {"x": 400, "y": 400},
            "size": {"width": 640, "height": 480}
        }
        video = await client.create_video(canvas_id, "tests/test_files/test_video.mp4", video_payload)
        video_id = video.id
        print_success(f"Created video with ID: {video_id}")

        # Get video details
        video = await client.get_video(canvas_id, video_id)
        print_success(f"Retrieved video details: {video}")

        # Download video
        content = await client.download_video(canvas_id, video_id)
        downloaded_path = "tests/test_files/downloaded_video.mp4"
        with open(downloaded_path, "wb") as f:
            f.write(content)
        print_success(f"Downloaded video to {downloaded_path}")

        # Update video
        update_payload = {
            "location": {"x": 450, "y": 450}
        }
        video = await client.update_video(canvas_id, video_id, update_payload)
        print_success(f"Updated video location: {video}")

        # List videos
        videos = await client.list_videos(canvas_id)
        print_success(f"Listed {len(videos)} videos")

    except Exception as e:
        print_error(f"Error in video operations: {e}")
        raise
    finally:
        # Clean up
        if video_id:
            try:
                await client.delete_video(canvas_id, video_id)
                print_success("Deleted test video")
            except Exception as e:
                print_error(f"Error deleting video: {e}")

        if downloaded_path and os.path.exists(downloaded_path):
            try:
                os.remove(downloaded_path)
                print_success("Cleaned up downloaded video")
            except Exception as e:
                print_error(f"Error cleaning up downloaded video: {e}")

async def test_pdf_operations(client: CanvusClient, canvas_id: str) -> None:
    """Test PDF operations."""
    pdf_id = None
    downloaded_path = None
    try:
        # Create a PDF
        pdf_payload = {
            "location": {"x": 600, "y": 600},
            "size": {"width": 800, "height": 1000}
        }
        pdf = await client.create_pdf(canvas_id, "tests/test_files/test_pdf.pdf", pdf_payload)
        pdf_id = pdf.id
        print_success(f"Created PDF with ID: {pdf_id}")

        # Get PDF details
        pdf = await client.get_pdf(canvas_id, pdf_id)
        print_success(f"Retrieved PDF details: {pdf}")

        # Download PDF
        content = await client.download_pdf(canvas_id, pdf_id)
        downloaded_path = "tests/test_files/downloaded_document.pdf"
        with open(downloaded_path, "wb") as f:
            f.write(content)
        print_success(f"Downloaded PDF to {downloaded_path}")

        # Update PDF
        update_payload = {
            "location": {"x": 650, "y": 650}
        }
        pdf = await client.update_pdf(canvas_id, pdf_id, update_payload)
        print_success(f"Updated PDF location: {pdf}")

        # List PDFs
        pdfs = await client.list_pdfs(canvas_id)
        print_success(f"Listed {len(pdfs)} PDFs")

    except Exception as e:
        print_error(f"Error in PDF operations: {e}")
        raise
    finally:
        # Clean up
        if pdf_id:
            try:
                await client.delete_pdf(canvas_id, pdf_id)
                print_success("Deleted test PDF")
            except Exception as e:
                print_error(f"Error deleting PDF: {e}")

        if downloaded_path and os.path.exists(downloaded_path):
            try:
                os.remove(downloaded_path)
                print_success("Cleaned up downloaded PDF")
            except Exception as e:
                print_error(f"Error cleaning up downloaded PDF: {e}")

async def setup_test_canvas(client: CanvusClient) -> Optional[str]:
    """Create a test canvas for resource testing."""
    try:
        canvas = await client.create_canvas({
            "name": f"Resource Test Canvas {asyncio.get_event_loop().time()}",
            "width": 1920,
            "height": 1080
        })
        print_success(f"Created test canvas: {canvas.id}")
        return canvas.id
    except Exception as e:
        print_error(f"Failed to create test canvas: {e}")
        return None

async def cleanup_test_canvas(client: CanvusClient, canvas_id: str) -> None:
    """Clean up the test canvas."""
    try:
        await client.delete_canvas(canvas_id)
        print_success(f"Cleaned up test canvas: {canvas_id}")
    except Exception as e:
        print_error(f"Failed to clean up test canvas: {e}")

async def test_canvas_resources(client: CanvusClient) -> None:
    """Main test function."""
    print_header("Starting Canvus Resource Tests")
    
    # Get user ID from config or use default
    config = load_config()
    user_id = config.get("user_id", 1000)  # Default to 1000 if not specified
    
    # Create a test token for our test suite
    test_token_id, test_token = await create_test_token(client, user_id)
    
    try:
        # Create a new client with our test token
        async with CanvusClient(
            base_url=config["base_url"],
            api_key=test_token
        ) as test_client:
            print_success("Test client initialized with new token")
            
            # Create test canvas
            canvas_id = await setup_test_canvas(test_client)
            if not canvas_id:
                return
            
            try:
                # Run all tests with the test token
                await test_note_operations(test_client, canvas_id)
                await test_image_operations(test_client, canvas_id)
                await test_browser_operations(test_client, canvas_id)
                await test_connector_operations(test_client, canvas_id)
                await test_video_operations(test_client, canvas_id)
                await test_pdf_operations(test_client, canvas_id)
            finally:
                # Clean up test canvas
                await cleanup_test_canvas(test_client, canvas_id)
    finally:
        # Clean up our test token
        try:
            await client.delete_token(user_id, test_token_id)
            print_success("Cleaned up test token")
        except Exception as e:
            print_error(f"Failed to clean up test token: {e}")

if __name__ == "__main__":
    async def run():
        config = load_config()
        print_success("Configuration loaded")
        
        async with CanvusClient(
            base_url=config["base_url"],
            api_key=config["api_key"]
        ) as client:
            print_success("Client initialized")
            await test_canvas_resources(client)
            
    asyncio.run(run()) 