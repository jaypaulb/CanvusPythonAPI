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

    def __init__(self, base_url: str, api_key: str):
        """Initialize the client."""
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
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

        async with aiohttp.ClientSession() as session:
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

    async def delete_folder(self, folder_id: str) -> None:
        """Delete a folder."""
        await self._request("DELETE", f"canvas-folders/{folder_id}")

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
