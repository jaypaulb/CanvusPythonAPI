"""
Core implementation of the Canvus API client.
"""

from typing import (
    Optional,
    Dict,
    Any,
    List,
    Type,
    TypeVar,
    Union,
    AsyncGenerator,
    Callable,
)
import json
import os
from pydantic import BaseModel, ValidationError
import aiohttp

from .models import (
    Canvas,
    ServerInfo,
    ServerConfig,
    User,
    CanvasFolder,
    Anchor,
    Note,
    Image,
    Browser,
    Video,
    PDF,
    Widget,
    Connector,
    AccessToken,
    TokenResponse,
    Workspace,
)
from .exceptions import CanvusAPIError

T = TypeVar("T", bound=BaseModel)
JsonData = Union[Dict[str, Any], str]


class CanvusClient:
    """Client for interacting with the Canvus API."""

    def __init__(self, base_url: str, api_key: str, verify_ssl: bool = True):
        """Initialize the client.
        
        Args:
            base_url: The base URL of the Canvus server
            api_key: The API key for authentication
            verify_ssl: Whether to verify SSL certificates (default: True)
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.verify_ssl = verify_ssl
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "CanvusClient":
        """Set up the client session."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Clean up the client session."""
        if self.session:
            await self.session.close()
            self.session = None

    def _parse_payload(self, data: JsonData) -> Dict[str, Any]:
        """Parse and validate JSON payload."""
        if isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError as e:
                raise CanvusAPIError("Invalid JSON string") from e
        return data

    def _build_url(self, endpoint: str) -> str:
        """Build the full URL for an API endpoint."""
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/api/v1/{endpoint}"

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        response_model: Optional[Type] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        return_binary: bool = False,
        stream: bool = False,
    ) -> Any:
        """Make a request to the API."""
        url = self._build_url(endpoint)
        print(f"Making {method} request to {endpoint}")

        # Prepare headers
        request_headers = {
            "Private-Token": "***",  # Redacted for security
            "Accept": "application/json" if not return_binary else "*/*",
        }
        if headers:
            request_headers.update(headers)
        if json_data is not None:
            request_headers["Content-Type"] = "application/json"

        request_kwargs: Dict[str, Any] = {}
        if params:
            request_kwargs["params"] = params
        if json_data:
            request_kwargs["json"] = json_data
        if data:
            request_kwargs["data"] = data
        request_kwargs["headers"] = {
            **request_headers,
            "Private-Token": self.api_key,  # Real token for request
        }

        # Create SSL context based on verify_ssl setting
        import ssl
        connector = None
        if url.startswith('https://') and not self.verify_ssl:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.request(method, url, **request_kwargs) as response:
                status = response.status
                print(f"Response status: {status}")

                if status not in range(200, 300):
                    text = await response.text()
                    print(f"Error response: {text}")
                    raise CanvusAPIError(text, status_code=status)

                if return_binary:
                    return await response.read()

                if stream:
                    return response  # Return the response object for streaming

                text = await response.text()
                if not text:
                    data = None
                else:
                    try:
                        data = json.loads(text)
                    except Exception as e:
                        raise CanvusAPIError(
                            f"Failed to decode JSON response: {str(e)}", status_code=500
                        )

                if response_model is not None:
                    try:
                        if isinstance(data, list):
                            return [
                                response_model.model_validate(item) for item in data
                            ]
                        else:
                            return response_model.model_validate(data)
                    except Exception as e:
                        raise CanvusAPIError(
                            f"Failed to validate response model: {str(e)}",
                            status_code=500,
                        )
                return data

    async def subscribe(
        self,
        endpoint: str,
        *,
        response_model: Optional[Type[T]] = None,
        params: Optional[Dict[str, Any]] = None,
        callback: Optional[Callable[[Union[T, Dict[str, Any]]], None]] = None,
    ) -> AsyncGenerator[Union[T, Dict[str, Any]], None]:
        """Subscribe to a streaming endpoint.

        Args:
            endpoint (str): The API endpoint to subscribe to
            response_model (Type[T], optional): Pydantic model for response validation
            params (Dict[str, Any], optional): Query parameters
            callback (Callable, optional): Callback function for processing updates

        Yields:
            Union[T, Dict[str, Any]]: Stream of updates from the endpoint
        """
        # Add subscribe=true to params
        params = params or {}
        params["subscribe"] = "true"

        # Make streaming request
        response = await self._request("GET", endpoint, params=params, stream=True)

        try:
            # Process the stream
            async for line in response.content:
                if not line:
                    continue

                try:
                    # Parse JSON data
                    data = json.loads(line)

                    # Validate with model if provided
                    if response_model:
                        result = response_model.model_validate(data)
                    else:
                        result = data

                    # Call callback if provided
                    if callback:
                        callback(result)

                    yield result

                except json.JSONDecodeError as e:
                    print(f"Failed to parse JSON from stream: {e}")
                    continue
                except ValidationError as e:
                    print(f"Failed to validate stream data: {e}")
                    continue
                except Exception as e:
                    print(f"Error processing stream data: {e}")
                    continue

        finally:
            # Ensure response is closed
            await response.release()

    # Server Operations
    async def get_server_info(self) -> ServerInfo:
        """Get server information."""
        return await self._request("GET", "server-info", response_model=ServerInfo)

    async def get_server_config(self) -> ServerConfig:
        """Get server configuration."""
        return await self._request("GET", "server-config", response_model=ServerConfig)

    async def update_server_config(self, payload: Dict[str, Any]) -> ServerConfig:
        """Update server configuration.

        Args:
            payload: Server configuration data to update. Can include:
                - server_name: Server display name
                - features: Feature flags and settings
                - auth: Authentication configuration
                - access: Access control settings
                - external_url: External URL for the server
                - email: Email configuration
                - authentication: Authentication provider settings

        Returns:
            ServerConfig: The updated server configuration.

        Raises:
            ValidationError: If payload contains invalid configuration data.
            AuthenticationError: If authentication fails.
            CanvusAPIError: For other API-related errors.

        Example:
            >>> config = await client.update_server_config({
            ...     "server_name": "My Canvus Server",
            ...     "external_url": "https://canvus.example.com"
            ... })
            >>> print(config.server_name)
            My Canvus Server
        """
        return await self._request(
            "PATCH", "server-config", response_model=ServerConfig, json_data=payload
        )

    async def send_test_email(self) -> Dict[str, Any]:
        """Send a test email to verify email configuration.

        Returns:
            Dict[str, Any]: Response indicating success or failure of the test email.
                Typically contains status information about the email sending attempt.

        Raises:
            AuthenticationError: If authentication fails.
            CanvusAPIError: If email configuration is invalid or sending fails.

        Example:
            >>> result = await client.send_test_email()
            >>> print(result.get('status', 'Unknown'))
            sent
        """
        return await self._request("POST", "server-config/send-test-email")

    # Canvas Operations
    async def list_canvases(self, params: Optional[JsonData] = None) -> List[Canvas]:
        """List all available canvases."""
        return await self._request(
            "GET",
            "canvases",
            response_model=Canvas,
            params=self._parse_payload(params) if params else None,
        )

    async def get_canvas(self, canvas_id: str) -> Canvas:
        """Get details of a specific canvas."""
        return await self._request(
            "GET", f"canvases/{canvas_id}", response_model=Canvas
        )

    async def create_canvas(self, payload: Dict[str, Any]) -> Canvas:
        """Create a new canvas."""
        return await self._request(
            "POST", "canvases", response_model=Canvas, json_data=payload
        )

    async def update_canvas(self, canvas_id: str, payload: Dict[str, Any]) -> Canvas:
        """Update canvas properties."""
        return await self._request(
            "PATCH", f"canvases/{canvas_id}", response_model=Canvas, json_data=payload
        )

    async def move_canvas(self, canvas_id: str, folder_id: str) -> Canvas:
        """Move a canvas to a different folder."""
        return await self._request(
            "POST",
            f"canvases/{canvas_id}/move",
            response_model=Canvas,
            json_data={"folder_id": folder_id},
        )

    async def copy_canvas(self, canvas_id: str, payload: Dict[str, Any]) -> Canvas:
        """Create a copy of a canvas."""
        return await self._request(
            "POST",
            f"canvases/{canvas_id}/copy",
            response_model=Canvas,
            json_data=payload,
        )

    async def get_canvas_permissions(self, canvas_id: str) -> Dict[str, Any]:
        """Get canvas permissions."""
        return await self._request("GET", f"canvases/{canvas_id}/permissions")

    async def get_canvas_preview(self, canvas_id: str) -> bytes:
        """Get canvas preview image.

        Args:
            canvas_id: The ID of the canvas to get the preview for.

        Returns:
            bytes: Binary image data of the canvas preview.

        Raises:
            ResourceNotFoundError: If the canvas is not found.
            AuthenticationError: If authentication fails.
            CanvusAPIError: For other API-related errors.

        Example:
            >>> preview_data = await client.get_canvas_preview("canvas-123")
            >>> with open("preview.png", "wb") as f:
            ...     f.write(preview_data)
        """
        return await self._request(
            "GET", f"canvases/{canvas_id}/preview", return_binary=True
        )

    async def delete_canvas(self, canvas_id: str) -> None:
        """Delete a canvas."""
        await self._request("DELETE", f"canvases/{canvas_id}")

    # Folder Operations
    async def list_folders(
        self, params: Optional[JsonData] = None
    ) -> List[CanvasFolder]:
        """List all available canvas folders."""
        return await self._request(
            "GET",
            "canvas-folders",
            response_model=CanvasFolder,
            params=self._parse_payload(params) if params else None,
        )

    async def get_folder(self, folder_id: str) -> CanvasFolder:
        """Get details of a specific folder."""
        return await self._request(
            "GET", f"canvas-folders/{folder_id}", response_model=CanvasFolder
        )

    async def create_folder(self, payload: JsonData) -> CanvasFolder:
        """Create a new folder."""
        return await self._request(
            "POST", "canvas-folders", response_model=CanvasFolder, json_data=payload
        )

    async def update_folder(self, folder_id: str, payload: JsonData) -> CanvasFolder:
        """Update folder properties."""
        return await self._request(
            "PATCH",
            f"canvas-folders/{folder_id}",
            response_model=CanvasFolder,
            json_data=payload,
        )

    async def move_folder(self, folder_id: str, payload: JsonData) -> CanvasFolder:
        """Move a folder to a different parent folder."""
        return await self._request(
            "POST",
            f"canvas-folders/{folder_id}/move",
            response_model=CanvasFolder,
            json_data=payload,
        )

    async def copy_folder(
        self, folder_id: str, payload: Dict[str, Any]
    ) -> CanvasFolder:
        """Copy a folder to a different location.

        Args:
            folder_id: The ID of the folder to copy.
            payload: Copy configuration data. Must include:
                - folder_id: ID of the destination parent folder
                - name: Optional new name for the copied folder

        Returns:
            CanvasFolder: The newly created folder copy.

        Raises:
            ValidationError: If payload is missing required fields.
            ResourceNotFoundError: If source or destination folder is not found.
            AuthenticationError: If authentication fails.
            CanvusAPIError: For other API-related errors.

        Example:
            >>> copied_folder = await client.copy_folder("folder-123", {
            ...     "folder_id": "parent-folder-456",
            ...     "name": "Copy of My Folder"
            ... })
            >>> print(copied_folder.name)
            Copy of My Folder
        """
        return await self._request(
            "POST",
            f"canvas-folders/{folder_id}/copy",
            response_model=CanvasFolder,
            json_data=payload,
        )

    async def delete_folder(self, folder_id: str) -> None:
        """Delete a folder."""
        await self._request("DELETE", f"canvas-folders/{folder_id}")

    async def delete_folder_children(self, folder_id: str) -> None:
        """Delete all children of a folder.

        Args:
            folder_id: The ID of the folder whose children should be deleted.

        Raises:
            ResourceNotFoundError: If the folder is not found.
            AuthenticationError: If authentication fails.
            CanvusAPIError: For other API-related errors.

        Example:
            >>> await client.delete_folder_children("folder-123")
            >>> print("All children deleted successfully")
        """
        await self._request("DELETE", f"canvas-folders/{folder_id}/children")

    # Demo Canvas Operations
    async def set_canvas_mode(self, canvas_id: str, is_demo: bool) -> Canvas:
        """Change a canvas between normal and demo mode."""
        return await self._request(
            "PATCH",
            f"canvases/{canvas_id}",
            response_model=Canvas,
            json_data={"mode": "demo" if is_demo else "normal"},
        )

    async def save_demo_state(self, canvas_id: str) -> None:
        """Save the current state of a demo canvas."""
        await self._request("POST", f"canvases/{canvas_id}/save")

    async def restore_demo_state(self, canvas_id: str) -> None:
        """Restore a demo canvas to its last saved state."""
        await self._request("POST", f"canvases/{canvas_id}/restore")

    # Permission Management
    async def set_canvas_permissions(
        self, canvas_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Set permission overrides on a canvas."""
        return await self._request(
            "POST", f"canvases/{canvas_id}/permissions", json_data=payload
        )

    async def get_folder_permissions(self, folder_id: str) -> Dict[str, Any]:
        """Get the permission overrides on a folder.

        Args:
            folder_id (str): The ID of the folder

        Returns:
            dict: The folder permissions including:
                - editors_can_share (bool)
                - users (list): List of user permissions with inheritance info
                - groups (list): List of group permissions
        """
        return await self._request("GET", f"canvas-folders/{folder_id}/permissions")

    async def set_folder_permissions(
        self, folder_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Set permission overrides on a folder."""
        return await self._request(
            "POST", f"canvas-folders/{folder_id}/permissions", json_data=payload
        )

    # Canvas Content Operations
    async def list_anchors(self, canvas_id: str) -> List[Anchor]:
        """List all anchors in a canvas."""
        return await self._request(
            "GET", f"canvases/{canvas_id}/anchors", response_model=Anchor
        )

    async def create_anchor(self, canvas_id: str, payload: JsonData) -> Anchor:
        """Create a new anchor in a canvas."""
        return await self._request(
            "POST",
            f"canvases/{canvas_id}/anchors",
            response_model=Anchor,
            json_data=payload,
        )

    async def update_anchor(
        self, canvas_id: str, anchor_id: str, payload: JsonData
    ) -> Anchor:
        """Update an existing anchor."""
        return await self._request(
            "PATCH",
            f"canvases/{canvas_id}/anchors/{anchor_id}",
            response_model=Anchor,
            json_data=payload,
        )

    async def delete_anchor(self, canvas_id: str, anchor_id: str) -> None:
        """Delete an anchor."""
        await self._request("DELETE", f"canvases/{canvas_id}/anchors/{anchor_id}")

    async def list_notes(self, canvas_id: str) -> List[Note]:
        """List all notes in a canvas."""
        return await self._request(
            "GET", f"canvases/{canvas_id}/notes", response_model=Note
        )

    async def create_note(self, canvas_id: str, payload: Dict[str, Any]) -> Note:
        """Create a new note in a canvas."""
        return await self._request(
            "POST",
            f"canvases/{canvas_id}/notes",
            response_model=Note,
            json_data=payload,
        )

    async def update_note(
        self, canvas_id: str, note_id: str, payload: Dict[str, Any]
    ) -> Note:
        """Update a note in a canvas."""
        return await self._request(
            "PATCH",
            f"canvases/{canvas_id}/notes/{note_id}",
            response_model=Note,
            json_data=payload,
        )

    async def delete_note(self, canvas_id: str, note_id: str) -> None:
        """Delete a note."""
        await self._request("DELETE", f"canvases/{canvas_id}/notes/{note_id}")

    async def list_images(self, canvas_id: str) -> List[Image]:
        """List all images in a canvas."""
        return await self._request(
            "GET", f"canvases/{canvas_id}/images", response_model=Image
        )

    async def create_image(
        self, canvas_id: str, file_path: str, payload: Optional[JsonData] = None
    ) -> Image:
        """Create a new image in a canvas using multipart upload.

        Args:
            canvas_id (str): The ID of the canvas
            file_path (str): Path to the image file
            payload (JsonData, optional): Additional data like position, title, etc.

        Returns:
            Image: The created image object
        """
        if not self.session:
            raise CanvusAPIError("Client session not initialized")

        # Create form data
        form = aiohttp.FormData()
        if payload:
            form.add_field("json", json.dumps(self._parse_payload(payload)))

        # Add file
        file_handle = open(file_path, "rb")
        try:
            form.add_field("data", file_handle)

            headers = {"Private-Token": self.api_key, "Accept": "application/json"}

            return await self._request(
                "POST",
                f"canvases/{canvas_id}/images",
                response_model=Image,
                headers=headers,
                data=form,
            )
        finally:
            file_handle.close()

    async def update_image(
        self, canvas_id: str, image_id: str, payload: JsonData
    ) -> Image:
        """Update an existing image."""
        return await self._request(
            "PATCH",
            f"canvases/{canvas_id}/images/{image_id}",
            response_model=Image,
            json_data=payload,
        )

    async def delete_image(self, canvas_id: str, image_id: str) -> None:
        """Delete an image."""
        await self._request("DELETE", f"canvases/{canvas_id}/images/{image_id}")

    async def list_browsers(self, canvas_id: str) -> List[Browser]:
        """List all browser instances in a canvas."""
        return await self._request(
            "GET", f"canvases/{canvas_id}/browsers", response_model=Browser
        )

    async def create_browser(self, canvas_id: str, payload: Dict[str, Any]) -> Browser:
        """Create a new browser in a canvas."""
        return await self._request(
            "POST",
            f"canvases/{canvas_id}/browsers",
            response_model=Browser,
            json_data=payload,
        )

    async def update_browser(
        self, canvas_id: str, browser_id: str, payload: Dict[str, Any]
    ) -> Browser:
        """Update a browser in a canvas."""
        return await self._request(
            "PATCH",
            f"canvases/{canvas_id}/browsers/{browser_id}",
            response_model=Browser,
            json_data=payload,
        )

    async def delete_browser(self, canvas_id: str, browser_id: str) -> None:
        """Delete a browser instance."""
        await self._request("DELETE", f"canvases/{canvas_id}/browsers/{browser_id}")

    async def list_videos(self, canvas_id: str) -> List[Video]:
        """List all videos in a canvas."""
        return await self._request(
            "GET", f"canvases/{canvas_id}/videos", response_model=Video
        )

    async def create_video(
        self, canvas_id: str, file_path: str, payload: Optional[JsonData] = None
    ) -> Video:
        """Create a new video in a canvas using multipart upload.

        Args:
            canvas_id (str): The ID of the canvas
            file_path (str): Path to the video file
            payload (JsonData, optional): Additional data like position, title, etc.

        Returns:
            Video: The created video object
        """
        if not self.session:
            raise CanvusAPIError("Client session not initialized")

        # Create form data
        form = aiohttp.FormData()
        if payload:
            form.add_field("json", json.dumps(self._parse_payload(payload)))

        # Add file
        file_handle = open(file_path, "rb")
        try:
            form.add_field("data", file_handle)

            headers = {"Private-Token": self.api_key, "Accept": "application/json"}

            return await self._request(
                "POST",
                f"canvases/{canvas_id}/videos",
                response_model=Video,
                headers=headers,
                data=form,
            )
        finally:
            file_handle.close()

    async def update_video(
        self, canvas_id: str, video_id: str, payload: JsonData
    ) -> Video:
        """Update an existing video."""
        return await self._request(
            "PATCH",
            f"canvases/{canvas_id}/videos/{video_id}",
            response_model=Video,
            json_data=payload,
        )

    async def delete_video(self, canvas_id: str, video_id: str) -> None:
        """Delete a video."""
        await self._request("DELETE", f"canvases/{canvas_id}/videos/{video_id}")

    async def list_canvas_video_inputs(self, canvas_id: str) -> List[Dict[str, Any]]:
        """List all video input widgets in a canvas.

        Args:
            canvas_id (str): The ID of the canvas to list video inputs for

        Returns:
            List[Dict[str, Any]]: List of video input widgets as dictionaries

        Raises:
            CanvusAPIError: If the request fails or canvas is not found
        """
        return await self._request("GET", f"canvases/{canvas_id}/video-inputs")

    async def create_video_input(self, canvas_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new video input widget in a canvas.

        Args:
            canvas_id (str): The ID of the canvas
            payload (Dict[str, Any]): Video input creation data including:
                - name (str): Name of the video input
                - source (str): Video source identifier
                - location (Dict[str, float]): Widget position {"x": float, "y": float}
                - size (Dict[str, float]): Widget dimensions {"width": float, "height": float}
                - config (Dict[str, Any], optional): Custom configuration for the video input
                - depth (int, optional): Z-order depth
                - scale (float, optional): Scale factor
                - pinned (bool, optional): Whether widget is pinned

        Returns:
            Dict[str, Any]: The created video input widget data

        Raises:
            CanvusAPIError: If video input creation fails
        """
        return await self._request(
            "POST",
            f"canvases/{canvas_id}/video-inputs",
            json_data=payload,
        )

    async def delete_video_input(self, canvas_id: str, input_id: str) -> None:
        """Delete a video input widget from a canvas.

        Args:
            canvas_id (str): The ID of the canvas
            input_id (str): The ID of the video input to delete

        Raises:
            CanvusAPIError: If video input deletion fails or video input is not found
        """
        await self._request(
            "DELETE",
            f"canvases/{canvas_id}/video-inputs/{input_id}",
        )

    async def list_pdfs(self, canvas_id: str) -> List[PDF]:
        """List all PDFs in a canvas."""
        return await self._request(
            "GET", f"canvases/{canvas_id}/pdfs", response_model=PDF
        )

    async def create_pdf(
        self, canvas_id: str, file_path: str, payload: Optional[JsonData] = None
    ) -> PDF:
        """Create a new PDF in a canvas using multipart upload.

        Args:
            canvas_id (str): The ID of the canvas
            file_path (str): Path to the PDF file
            payload (JsonData, optional): Additional data like position, title, etc.

        Returns:
            PDF: The created PDF object
        """
        if not self.session:
            raise CanvusAPIError("Client session not initialized")

        # Create form data
        form = aiohttp.FormData()
        if payload:
            form.add_field("json", json.dumps(self._parse_payload(payload)))

        # Add file
        file_handle = open(file_path, "rb")
        try:
            form.add_field("data", file_handle)

            headers = {"Private-Token": self.api_key, "Accept": "application/json"}

            return await self._request(
                "POST",
                f"canvases/{canvas_id}/pdfs",
                response_model=PDF,
                headers=headers,
                data=form,
            )
        finally:
            file_handle.close()

    async def update_pdf(self, canvas_id: str, pdf_id: str, payload: JsonData) -> PDF:
        """Update an existing PDF."""
        return await self._request(
            "PATCH",
            f"canvases/{canvas_id}/pdfs/{pdf_id}",
            response_model=PDF,
            json_data=payload,
        )

    async def delete_pdf(self, canvas_id: str, pdf_id: str) -> None:
        """Delete a PDF."""
        await self._request("DELETE", f"canvases/{canvas_id}/pdfs/{pdf_id}")

    # Uploads Folder Operations
    async def upload_note(self, canvas_id: str, payload: JsonData) -> Dict[str, Any]:
        """Create a new note in the uploads folder.

        Args:
            canvas_id (str): The ID of the canvas
            payload (JsonData): Note data including:
                - upload_type (str): Must be "note"
                - text (str, optional): Text content of the note
                - title (str, optional): Title of the note
                - background_color (str, optional): Color of the note

        Returns:
            dict: The created note object
        """
        data = self._parse_payload(payload)
        if data.get("upload_type") != "note":
            raise CanvusAPIError("upload_type must be 'note' for note uploads")

        # Create form data with json part
        form = aiohttp.FormData()
        form.add_field("json", json.dumps(data))

        return await self._request(
            "POST", f"canvases/{canvas_id}/uploads-folder", data=form
        )

    async def upload_file(
        self, canvas_id: str, file_path: str, payload: Optional[JsonData] = None
    ) -> Dict[str, Any]:
        """Upload a file to the canvas's uploads folder.
        The file type (PDF, image, video, etc.) is automatically recognized.

        Args:
            canvas_id (str): The ID of the canvas
            file_path (str): Path to the file to upload
            payload (JsonData, optional): Additional data including:
                - upload_type (str, optional): Must be missing, empty or "asset"
                - title (str, optional): Title of the asset
                - original_filename (str, optional): Original filename

        Returns:
            dict: The created asset object
        """
        if not self.session:
            raise CanvusAPIError("Client session not initialized")

        # Create form data
        form = aiohttp.FormData()
        if payload:
            data = self._parse_payload(payload)
            if data.get("upload_type") not in (None, "", "asset"):
                raise CanvusAPIError(
                    "upload_type must be missing, empty or 'asset' for file uploads"
                )
            form.add_field("json", json.dumps(data))

        # Add file data part
        with open(file_path, "rb") as f:
            form.add_field("data", f)

        return await self._request(
            "POST", f"canvases/{canvas_id}/uploads-folder", data=form
        )

    # Widget Operations (Read-only)
    async def list_widgets(self, canvas_id: str) -> List[Widget]:
        """List all widgets in a canvas."""
        return await self._request(
            "GET", f"canvases/{canvas_id}/widgets", response_model=Widget
        )

    async def get_widget(self, canvas_id: str, widget_id: str) -> Widget:
        """Get details of a specific widget."""
        return await self._request(
            "GET", f"canvases/{canvas_id}/widgets/{widget_id}", response_model=Widget
        )

    async def create_widget(self, canvas_id: str, payload: Dict[str, Any]) -> Widget:
        """Create a new widget in a canvas.

        Args:
            canvas_id (str): The ID of the canvas
            payload (Dict[str, Any]): Widget creation data including:
                - widget_type (str): Type of widget to create
                - location (Dict[str, float]): Widget position {"x": float, "y": float}
                - size (Dict[str, float]): Widget dimensions {"width": float, "height": float}
                - config (Dict[str, Any], optional): Custom configuration for the widget
                - depth (int, optional): Z-order depth
                - scale (float, optional): Scale factor
                - pinned (bool, optional): Whether widget is pinned
                - parent_id (str, optional): Parent widget ID

        Returns:
            Widget: The created widget

        Raises:
            CanvusAPIError: If widget creation fails
        """
        return await self._request(
            "POST",
            f"canvases/{canvas_id}/widgets",
            response_model=Widget,
            json_data=payload,
        )

    async def update_widget(
        self, canvas_id: str, widget_id: str, payload: Dict[str, Any]
    ) -> Widget:
        """Update a widget in a canvas.

        Args:
            canvas_id (str): The ID of the canvas
            widget_id (str): The ID of the widget to update
            payload (Dict[str, Any]): Widget update data. Can include:
                - location (Dict[str, float]): New position
                - size (Dict[str, float]): New dimensions
                - config (Dict[str, Any]): Updated configuration
                - depth (int): New Z-order depth
                - scale (float): New scale factor
                - pinned (bool): New pinned state
                - parent_id (str): New parent widget ID

        Returns:
            Widget: The updated widget

        Raises:
            CanvusAPIError: If widget update fails
        """
        return await self._request(
            "PATCH",
            f"canvases/{canvas_id}/widgets/{widget_id}",
            response_model=Widget,
            json_data=payload,
        )

    async def delete_widget(self, canvas_id: str, widget_id: str) -> None:
        """Delete a widget from a canvas.

        Args:
            canvas_id (str): The ID of the canvas
            widget_id (str): The ID of the widget to delete

        Raises:
            CanvusAPIError: If widget deletion fails
        """
        await self._request("DELETE", f"canvases/{canvas_id}/widgets/{widget_id}")

    # Canvas Background Operations
    async def get_canvas_background(self, canvas_id: str) -> Dict[str, Any]:
        """Get the background configuration for a canvas.

        Args:
            canvas_id (str): The ID of the canvas

        Returns:
            Dict[str, Any]: Background configuration data including:
                - type (str): Background type (color, image, etc.)
                - color (str, optional): Background color
                - image_url (str, optional): Background image URL
                - opacity (float, optional): Background opacity
                - scale (float, optional): Background scale factor

        Raises:
            CanvusAPIError: If background retrieval fails
        """
        return await self._request("GET", f"canvases/{canvas_id}/background")

    async def set_canvas_background(
        self, canvas_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Set the background configuration for a canvas.

        Args:
            canvas_id (str): The ID of the canvas
            payload (Dict[str, Any]): Background configuration data including:
                - type (str): Background type (color, image, etc.)
                - color (str, optional): Background color
                - opacity (float, optional): Background opacity
                - scale (float, optional): Background scale factor

        Returns:
            Dict[str, Any]: Updated background configuration

        Raises:
            CanvusAPIError: If background update fails
        """
        return await self._request(
            "PATCH", f"canvases/{canvas_id}/background", json_data=payload
        )

    async def set_canvas_background_image(
        self, canvas_id: str, file_path: str
    ) -> Dict[str, Any]:
        """Set a canvas background image by uploading a file.

        Args:
            canvas_id (str): The ID of the canvas
            file_path (str): Path to the image file to upload

        Returns:
            Dict[str, Any]: Background configuration with uploaded image

        Raises:
            CanvusAPIError: If image upload or background setting fails
            FileNotFoundError: If the specified file doesn't exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image file not found: {file_path}")

        # Create form data for file upload
        form_data = aiohttp.FormData()
        form_data.add_field(
            "image", open(file_path, "rb"), filename=os.path.basename(file_path)
        )

        return await self._request(
            "POST", f"canvases/{canvas_id}/background", data=form_data
        )

    async def get_color_presets(self, canvas_id: str) -> Dict[str, Any]:
        """Get color presets for a canvas.

        Args:
            canvas_id: The ID of the canvas

        Returns:
            Dict[str, Any]: Color presets data

        Raises:
            CanvusAPIError: If the request fails
        """
        return await self._request("GET", f"canvases/{canvas_id}/color-presets")

    async def update_color_presets(
        self, canvas_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update color presets for a canvas.

        Args:
            canvas_id (str): The ID of the canvas
            payload (Dict[str, Any]): Color presets configuration data

        Returns:
            Dict[str, Any]: Updated color presets data

        Raises:
            CanvusAPIError: If the color presets update fails
        """
        return await self._request(
            "PATCH", f"canvases/{canvas_id}/color-presets", json_data=payload
        )

    async def get_anchor(self, canvas_id: str, anchor_id: str) -> Anchor:
        """Get details of a specific anchor."""
        return await self._request(
            "GET", f"canvases/{canvas_id}/anchors/{anchor_id}", response_model=Anchor
        )

    async def get_note(self, canvas_id: str, note_id: str) -> Note:
        """Get details of a specific note."""
        return await self._request(
            "GET", f"canvases/{canvas_id}/notes/{note_id}", response_model=Note
        )

    async def get_image(self, canvas_id: str, image_id: str) -> Image:
        """Get details of a specific image."""
        return await self._request(
            "GET", f"canvases/{canvas_id}/images/{image_id}", response_model=Image
        )

    async def download_image(self, canvas_id: str, image_id: str) -> bytes:
        """Download an image's binary content."""
        return await self._request(
            "GET",
            f"canvases/{canvas_id}/images/{image_id}/download",
            return_binary=True,
        )

    async def get_browser(self, canvas_id: str, browser_id: str) -> Browser:
        """Get details of a specific browser instance."""
        return await self._request(
            "GET", f"canvases/{canvas_id}/browsers/{browser_id}", response_model=Browser
        )

    async def get_video(self, canvas_id: str, video_id: str) -> Video:
        """Get details of a specific video."""
        return await self._request(
            "GET", f"canvases/{canvas_id}/videos/{video_id}", response_model=Video
        )

    async def download_video(self, canvas_id: str, video_id: str) -> bytes:
        """Download a video's binary content."""
        return await self._request(
            "GET",
            f"canvases/{canvas_id}/videos/{video_id}/download",
            return_binary=True,
        )

    async def get_pdf(self, canvas_id: str, pdf_id: str) -> PDF:
        """Get details of a specific PDF."""
        return await self._request(
            "GET", f"canvases/{canvas_id}/pdfs/{pdf_id}", response_model=PDF
        )

    async def download_pdf(self, canvas_id: str, pdf_id: str) -> bytes:
        """Download a PDF's binary content."""
        return await self._request(
            "GET", f"canvases/{canvas_id}/pdfs/{pdf_id}/download", return_binary=True
        )

    # Connector Operations
    async def list_connectors(self, canvas_id: str) -> List[Connector]:
        """List all connectors in a canvas."""
        return await self._request(
            "GET", f"canvases/{canvas_id}/connectors", response_model=Connector
        )

    async def get_connector(self, canvas_id: str, connector_id: str) -> Connector:
        """Get details of a specific connector."""
        return await self._request(
            "GET",
            f"canvases/{canvas_id}/connectors/{connector_id}",
            response_model=Connector,
        )

    async def create_connector(
        self, canvas_id: str, payload: Dict[str, Any]
    ) -> Connector:
        """Create a new connector in a canvas."""
        return await self._request(
            "POST",
            f"canvases/{canvas_id}/connectors",
            response_model=Connector,
            json_data=payload,
        )

    async def update_connector(
        self, canvas_id: str, connector_id: str, payload: Dict[str, Any]
    ) -> Connector:
        """Update a connector in a canvas."""
        return await self._request(
            "PATCH",
            f"canvases/{canvas_id}/connectors/{connector_id}",
            response_model=Connector,
            json_data=payload,
        )

    async def delete_connector(self, canvas_id: str, connector_id: str) -> None:
        """Delete a connector."""
        await self._request("DELETE", f"canvases/{canvas_id}/connectors/{connector_id}")

    # Token Management
    async def list_tokens(self, user_id: int) -> List[AccessToken]:
        """List access tokens for a user.

        Regular users can only see their own tokens.
        Administrators can list access tokens of other users.
        The actual tokens are not returned.

        Args:
            user_id (int): The ID of the user

        Returns:
            List[AccessToken]: List of access token information
        """
        return await self._request(
            "GET", f"users/{user_id}/access-tokens", response_model=AccessToken
        )

    async def get_token(self, user_id: int, token_id: str) -> AccessToken:
        """Get information about a single access token.

        Args:
            user_id (int): The ID of the user
            token_id (str): The ID of the token

        Returns:
            AccessToken: Token information
        """
        return await self._request(
            "GET",
            f"users/{user_id}/access-tokens/{token_id}",
            response_model=AccessToken,
        )

    async def create_token(self, user_id: int, description: str) -> TokenResponse:
        """Create a new access token.

        Note: The plain text token is only returned in this response.
        It cannot be retrieved afterwards.

        Args:
            user_id (int): The ID of the user
            description (str): Description of the new token

        Returns:
            TokenResponse: Created token information including the plain token
        """
        return await self._request(
            "POST",
            f"users/{user_id}/access-tokens",
            response_model=TokenResponse,
            json_data={"description": description},
        )

    async def update_token(
        self, user_id: int, token_id: str, description: str
    ) -> AccessToken:
        """Update an access token's description.

        Args:
            user_id (int): The ID of the user
            token_id (str): The ID of the token
            description (str): New description for the token

        Returns:
            AccessToken: Updated token information
        """
        return await self._request(
            "PATCH",
            f"users/{user_id}/access-tokens/{token_id}",
            response_model=AccessToken,
            json_data={"description": description},
        )

    async def delete_token(self, user_id: int, token_id: str) -> None:
        """Delete an access token.

        The token is revoked and can no longer be used.

        Args:
            user_id (int): The ID of the user
            token_id (str): The ID of the token to delete
        """
        await self._request("DELETE", f"users/{user_id}/access-tokens/{token_id}")

    # User Management
    async def list_users(self) -> List[User]:
        """List all users on the server.

        Returns:
            List[User]: List of all users
        """
        return await self._request("GET", "users", response_model=User)

    async def get_user(self, user_id: int) -> User:
        """Get information about a single user.

        Args:
            user_id (int): The ID of the user to get

        Returns:
            User: User information
        """
        return await self._request("GET", f"users/{user_id}", response_model=User)

    async def create_user(self, payload: Dict[str, Any]) -> User:
        """Create a new user (admin only).

        Args:
            payload (Dict[str, Any]): User data including:
                - email (str): Email address (required)
                - name (str): Display name (required)
                - password (str, optional): Password
                - admin (bool, optional): Is admin user
                - approved (bool, optional): Is initially approved
                - blocked (bool, optional): Is initially blocked

        Returns:
            User: Created user information
        """
        return await self._request(
            "POST", "users", response_model=User, json_data=payload
        )

    async def delete_user(self, user_id: int) -> None:
        """Permanently delete a user (admin only).

        Args:
            user_id (int): The ID of the user to delete
        """
        await self._request("DELETE", f"users/{user_id}")

    async def register_user(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user account (no authentication required).

        Args:
            payload (Dict[str, Any]): User registration data including:
                - email (str): Email address (required)
                - name (str): Display name (required)
                - password (str): Password (required)
                - admin (bool, optional): Is admin user
                - approved (bool, optional): Is initially approved
                - blocked (bool, optional): Is initially blocked

        Returns:
            Dict[str, Any]: Registration response
        """
        return await self._request("POST", "users/register", json_data=payload)

    async def approve_user(self, user_id: int) -> User:
        """Approve a registered user account (admin only).

        Args:
            user_id (int): The ID of the user to approve

        Returns:
            User: Updated user information
        """
        return await self._request(
            "POST", f"users/{user_id}/approve", response_model=User
        )

    async def confirm_email(self, token: str) -> Dict[str, Any]:
        """Confirm user email address with token from email.

        Args:
            token (str): Token from confirmation email

        Returns:
            Dict[str, Any]: Confirmation response
        """
        return await self._request(
            "POST", "users/confirm-email", json_data={"token": token}
        )

    async def change_password(
        self, user_id: int, current_password: str, new_password: str
    ) -> User:
        """Change a user's password.

        Regular users can only change their own password.
        Admins can change any user's password.

        Args:
            user_id (int): The ID of the user
            current_password (str): Current password
            new_password (str): New password

        Returns:
            User: Updated user information
        """
        return await self._request(
            "POST",
            f"users/{user_id}/password",
            response_model=User,
            json_data={
                "current_password": current_password,
                "new_password": new_password,
            },
        )

    async def request_password_reset(self, email: str) -> None:
        """Request a password reset email.

        Args:
            email (str): Email address of the user
        """
        await self._request(
            "POST", "users/password/create-reset-token", json_data={"email": email}
        )

    async def validate_reset_token(self, token: str) -> Dict[str, Any]:
        """Validate a password reset token without consuming it.

        Args:
            token (str): Token from reset email

        Returns:
            Dict[str, Any]: Validation response
        """
        return await self._request(
            "GET", "users/password/validate-reset-token", params={"token": token}
        )

    async def reset_password(self, token: str, new_password: str) -> Dict[str, Any]:
        """Reset password using token from reset email.

        Args:
            token (str): Token from reset email
            new_password (str): New password

        Returns:
            Dict[str, Any]: Reset response
        """
        return await self._request(
            "POST",
            "users/password/reset",
            json_data={"token": token, "password": new_password},
        )

    async def login(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Sign in user and get access token.

        Can authenticate with either:
        1. Email and password
        2. Existing token (will be validated and refreshed)

        Args:
            email (str, optional): User email
            password (str, optional): User password
            token (str, optional): Existing token to validate

        Returns:
            Dict[str, Any]: Login response with token and user info
        """
        if token:
            payload = {"token": token}
        else:
            if not email or not password:
                raise ValueError("Must provide either token or email+password")
            payload = {"email": email, "password": password}

        return await self._request("POST", "users/login", json_data=payload)

    async def logout(self, token: Optional[str] = None) -> None:
        """Sign out user by invalidating token.

        Args:
            token (str, optional): Token to invalidate. If not provided,
                                 the client's token will be used.
        """
        payload = {"token": token} if token else None
        await self._request("POST", "users/logout", json_data=payload)

    async def get_current_user(self) -> User:
        """Get information about the currently authenticated user.

        This method validates the current token and returns the user information.

        Returns:
            User: Current user information

        Raises:
            CanvusAPIError: If authentication fails or token is invalid
        """
        # Use the login method with the current token to validate and get user info
        response = await self.login(token=self.api_key)

        # The login response should contain user information
        if "user" in response:
            return User.model_validate(response["user"])
        elif "id" in response:
            # If the response itself is user data
            return User.model_validate(response)
        else:
            raise CanvusAPIError(
                "Unable to extract user information from login response"
            )

    async def block_user(self, user_id: int) -> User:
        """Block a user from signing in.

        Regular users can only block themselves.
        Admins can block any user.

        Args:
            user_id (int): The ID of the user to block

        Returns:
            User: Updated user information
        """
        return await self._request(
            "POST", f"users/{user_id}/block", response_model=User
        )

    async def unblock_user(self, user_id: int) -> User:
        """Unblock a user (admin only).

        Args:
            user_id (int): The ID of the user to unblock

        Returns:
            User: Updated user information
        """
        return await self._request(
            "POST", f"users/{user_id}/unblock", response_model=User
        )

    async def update_user(self, user_id: int, payload: Dict[str, Any]) -> User:
        """Update user profile information.

        Regular users can only update their own profile and only certain fields.
        Admins can update all fields of any user.

        Args:
            user_id (int): The ID of the user to update
            payload (Dict[str, Any]): Update data which may include:
                - email (str): New email address
                - name (str): New display name
                - password (str): New password (admin only)
                - admin (bool): Is admin (admin only)
                - approved (bool): Is approved (admin only)
                - blocked (bool): Is blocked
                - need_email_confirmation (bool): Has confirmed email (admin only)

        Returns:
            User: Updated user information
        """
        return await self._request(
            "PATCH", f"users/{user_id}", response_model=User, json_data=payload
        )

    # Group Operations
    async def list_groups(self) -> List[Dict[str, Any]]:
        """List all user groups.

        Returns:
            List[Dict[str, Any]]: List of groups with id, name, and description

        Raises:
            CanvusAPIError: If the request fails
        """
        return await self._request("GET", "groups")

    async def get_group(self, group_id: str) -> Dict[str, Any]:
        """Get a single user group.

        Args:
            group_id (str): The ID of the group to retrieve

        Returns:
            Dict[str, Any]: Group data with id, name, and description

        Raises:
            CanvusAPIError: If the request fails or group is not found
        """
        return await self._request("GET", f"groups/{group_id}")

    async def create_group(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user group.

        Args:
            payload (Dict[str, Any]): Group creation data containing:
                - name (str): Name of the group (required)
                - description (str, optional): Description of the group

        Returns:
            Dict[str, Any]: Created group data with id, name, and description

        Raises:
            CanvusAPIError: If the request fails or validation fails
        """
        return await self._request("POST", "groups", json_data=payload)

    async def delete_group(self, group_id: str) -> None:
        """Delete a user group.

        Args:
            group_id (str): The ID of the group to delete

        Raises:
            CanvusAPIError: If the request fails or group is not found
        """
        await self._request("DELETE", f"groups/{group_id}")

    async def add_user_to_group(self, group_id: str, user_id: str) -> Dict[str, Any]:
        """Add a user to a group.

        Args:
            group_id (str): The ID of the group to add the user to
            user_id (str): The ID of the user to add to the group

        Returns:
            Dict[str, Any]: Response data from the API

        Raises:
            CanvusAPIError: If the request fails, group/user not found, or user already in group
        """
        payload = {"user_id": user_id}
        return await self._request(
            "POST", f"groups/{group_id}/members", json_data=payload
        )

    async def list_group_members(self, group_id: str) -> List[Dict[str, Any]]:
        """List all members of a group.

        Args:
            group_id (str): The ID of the group to list members for

        Returns:
            List[Dict[str, Any]]: List of group members as dictionaries

        Raises:
            CanvusAPIError: If the request fails or group is not found
        """
        return await self._request("GET", f"groups/{group_id}/members")

    async def remove_user_from_group(self, group_id: str, user_id: str) -> None:
        """Remove a user from a group.

        Args:
            group_id (str): The ID of the group to remove the user from
            user_id (str): The ID of the user to remove from the group

        Raises:
            CanvusAPIError: If the request fails, group/user not found, or user not in group
        """
        await self._request("DELETE", f"groups/{group_id}/members/{user_id}")

    # Workspace Operations
    async def list_workspaces(self, client_id: str) -> List[Workspace]:
        """List all workspaces of a client.

        Args:
            client_id (str): ID of the client

        Returns:
            List[Workspace]: List of workspaces
        """
        return await self._request(
            "GET", f"clients/{client_id}/workspaces", response_model=Workspace
        )

    async def get_workspace(self, client_id: str, workspace_index: int) -> Workspace:
        """Get details of a specific workspace.

        Args:
            client_id (str): ID of the client
            workspace_index (int): Index of the workspace to get

        Returns:
            Workspace: Workspace information
        """
        return await self._request(
            "GET",
            f"clients/{client_id}/workspaces/{workspace_index}",
            response_model=Workspace,
        )

    async def update_workspace(
        self, client_id: str, workspace_index: int, payload: Dict[str, Any]
    ) -> Workspace:
        """Update workspace parameters.

        Args:
            client_id (str): ID of the client
            workspace_index (int): Index of the workspace to update
            payload (Dict[str, Any]): Update data which may include:
                - info_panel_visible (bool): Is the workspace info panel visible
                - pinned (bool): Is the workspace pinned
                - view_rectangle (dict): The visible rectangle in canvas coordinates

        Returns:
            Workspace: Updated workspace information
        """
        return await self._request(
            "PATCH",
            f"clients/{client_id}/workspaces/{workspace_index}",
            response_model=Workspace,
            json_data=payload,
        )

    # Client Operations
    async def list_clients(self) -> List[Dict[str, Any]]:
        """List all connected clients."""
        return await self._request("GET", "clients", response_model=None)

    async def get_client(self, client_id: str) -> Dict[str, Any]:
        """Get a specific client by ID.

        Args:
            client_id (str): The ID of the client to retrieve

        Returns:
            Dict[str, Any]: Client data as dictionary

        Raises:
            CanvusAPIError: If the request fails or client is not found
        """
        return await self._request("GET", f"clients/{client_id}")

    async def list_client_video_inputs(self, client_id: str) -> List[Dict[str, Any]]:
        """List all video inputs for a specific client.

        Args:
            client_id (str): The ID of the client to list video inputs for

        Returns:
            List[Dict[str, Any]]: List of client video inputs as dictionaries

        Raises:
            CanvusAPIError: If the request fails or client is not found
        """
        return await self._request("GET", f"clients/{client_id}/video-inputs")

    async def list_client_video_outputs(self, client_id: str) -> List[Dict[str, Any]]:
        """List all video outputs for a specific client.

        Args:
            client_id (str): The ID of the client to list video outputs for

        Returns:
            List[Dict[str, Any]]: List of client video outputs as dictionaries

        Raises:
            CanvusAPIError: If the request fails or client is not found
        """
        return await self._request("GET", f"clients/{client_id}/video-outputs")

    async def set_video_output_source(self, client_id: str, index: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Set the source for a specific video output on a client.

        Args:
            client_id (str): The ID of the client
            index (int): The index of the video output to configure
            payload (Dict[str, Any]): Video output source configuration including:
                - source (str): Video source identifier
                - enabled (bool, optional): Whether the output is enabled
                - resolution (str, optional): Output resolution
                - refresh_rate (int, optional): Refresh rate in Hz

        Returns:
            Dict[str, Any]: Updated video output data as dictionary

        Raises:
            CanvusAPIError: If the request fails, client not found, or invalid configuration
        """
        return await self._request(
            "PATCH",
            f"clients/{client_id}/video-outputs/{index}",
            json_data=payload,
        )

    async def update_video_output(self, canvas_id: str, output_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Update a video output on a canvas.

        Args:
            canvas_id (str): The ID of the canvas
            output_id (str): The ID of the video output to update
            payload (Dict[str, Any]): Video output update configuration including:
                - name (str, optional): New name for the video output
                - enabled (bool, optional): Whether the output is enabled
                - resolution (str, optional): Output resolution
                - refresh_rate (int, optional): Refresh rate in Hz
                - source (str, optional): Video source identifier

        Returns:
            Dict[str, Any]: Updated video output data as dictionary

        Raises:
            CanvusAPIError: If the request fails, canvas not found, or invalid configuration
        """
        return await self._request(
            "PATCH",
            f"canvases/{canvas_id}/video-outputs/{output_id}",
            json_data=payload,
        )

    async def get_license_info(self) -> Dict[str, Any]:
        """Get license information for the Canvus server.

        Returns:
            Dict[str, Any]: License information data as dictionary including:
                - license_key (str): The license key
                - status (str): License status (active, expired, etc.)
                - expiry_date (str, optional): License expiry date
                - features (List[str], optional): List of enabled features
                - max_users (int, optional): Maximum number of users allowed
                - max_canvases (int, optional): Maximum number of canvases allowed

        Raises:
            CanvusAPIError: If the request fails or license info cannot be retrieved
        """
        return await self._request("GET", "license")

    async def get_client_workspaces(self, client_id: str) -> List[Workspace]:
        """Get workspaces for a specific client."""
        return await self._request(
            "GET", f"clients/{client_id}/workspaces", response_model=Workspace
        )

    async def find_admin_client(
        self, admin_email: str = "admin@local.local"
    ) -> Optional[str]:
        """Find the client ID where the admin user is logged in.

        Args:
            admin_email (str): The email of the admin user to look for

        Returns:
            Optional[str]: The client ID where admin is found, or None if not found
        """
        try:
            # Get list of all connected clients
            clients = await self.list_clients()

            # Check each client's workspaces for admin user
            for client in clients:
                try:
                    workspaces = await self.get_client_workspaces(client["id"])
                    for workspace in workspaces:
                        if workspace.user == admin_email:
                            return client["id"]
                except Exception:
                    # Skip clients that error out
                    continue

            return None

        except Exception as e:
            print(f"Error finding admin client: {e}")
            return None

    # Subscription Methods
    async def subscribe_widgets(
        self,
        canvas_id: str,
        callback: Optional[
            Callable[[Union[Note, Image, Browser, Video, PDF, Widget]], None]
        ] = None,
    ) -> AsyncGenerator[Union[Note, Image, Browser, Video, PDF, Widget], None]:
        """Subscribe to updates for all widgets in a canvas.

        Args:
            canvas_id (str): The ID of the canvas to monitor widgets for
            callback (Callable, optional): Function to call for each widget update

        Yields:
            Union[Note, Image, Browser, Video, PDF, Widget]: Stream of widget updates
        """
        async for update in self.subscribe(
            f"canvases/{canvas_id}/widgets",
            params={"subscribe": "true"},
            callback=callback,
        ):
            # Determine widget type and validate accordingly
            widget_type = update.get("type")
            if widget_type == "note":
                yield Note.model_validate(update)
            elif widget_type == "image":
                yield Image.model_validate(update)
            elif widget_type == "browser":
                yield Browser.model_validate(update)
            elif widget_type == "video":
                yield Video.model_validate(update)
            elif widget_type == "pdf":
                yield PDF.model_validate(update)
            else:
                yield Widget.model_validate(update)

    async def subscribe_workspace(
        self,
        client_id: str,
        workspace_index: int,
        callback: Optional[Callable[[Workspace], None]] = None,
    ) -> AsyncGenerator[Workspace, None]:
        """Subscribe to updates for a specific workspace.

        Args:
            client_id (str): The ID of the client
            workspace_index (int): The index of the workspace
            callback (Callable, optional): Function to call for each update

        Yields:
            Workspace: Stream of workspace updates
        """
        async for update in self.subscribe(
            f"clients/{client_id}/workspaces/{workspace_index}",
            response_model=Workspace,
            callback=callback,
        ):
            yield update

    async def subscribe_note(
        self,
        canvas_id: str,
        note_id: str,
        callback: Optional[Callable[[Note], None]] = None,
    ) -> AsyncGenerator[Note, None]:
        """Subscribe to updates for a specific note.

        Args:
            canvas_id (str): The ID of the canvas containing the note
            note_id (str): The ID of the note to subscribe to
            callback (Callable, optional): Function to call for each update

        Yields:
            Note: Stream of note updates
        """
        async for update in self.subscribe(
            f"canvases/{canvas_id}/notes/{note_id}",
            response_model=Note,
            callback=callback,
        ):
            yield update
