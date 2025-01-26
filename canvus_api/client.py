"""
Core implementation of the Canvus API client.
"""

from typing import Optional, Dict, Any, List, Type, TypeVar, Union
import json
import httpx
from pydantic import BaseModel, ValidationError
import aiohttp
from fastapi import HTTPException

from .models import Canvas, CanvasStatus, ServerInfo, ServerConfig, User, CanvasFolder, Anchor, Note, Image, Browser, Video, PDF, Widget, Connector, AccessToken, TokenResponse, Workspace
from .exceptions import CanvusAPIError, AuthenticationError

T = TypeVar('T', bound=BaseModel)
JsonData = Union[Dict[str, Any], str]


class CanvusAPIError(Exception):
    """Custom exception for Canvus API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class CanvusClient:
    """Client for interacting with the Canvus API."""

    def __init__(self, base_url: str, api_key: str):
        """Initialize the client."""
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> 'CanvusClient':
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
        endpoint = endpoint.lstrip('/')
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
        return_binary: bool = False
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

        kwargs = {}
        if params:
            kwargs["params"] = params
        if json_data:
            kwargs["json"] = json_data
        if data:
            kwargs["data"] = data
        kwargs["headers"] = {
            **request_headers,
            "Private-Token": self.api_key  # Real token for request
        }

        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, **kwargs) as response:
                status = response.status
                print(f"Response status: {status}")
                
                if status not in range(200, 300):
                    text = await response.text()
                    print(f"Error response: {text}")
                    raise CanvusAPIError(text, status_code=status)

                if return_binary:
                    return await response.read()

                text = await response.text()
                if not text:
                    data = None
                else:
                    try:
                        data = json.loads(text)
                    except Exception as e:
                        raise CanvusAPIError(
                            f"Failed to decode JSON response: {str(e)}",
                            status_code=500
                        )

                if response_model is not None:
                    try:
                        if isinstance(data, list):
                            return [response_model.model_validate(item) for item in data]
                        else:
                            return response_model.model_validate(data)
                    except Exception as e:
                        raise CanvusAPIError(
                            f"Failed to validate response model: {str(e)}",
                            status_code=500
                        )
                return data

    # Server Operations
    async def get_server_info(self) -> ServerInfo:
        """Get server information."""
        return await self._request(
            "GET",
            "server-info",
            response_model=ServerInfo
        )

    async def get_server_config(self) -> ServerConfig:
        """Get server configuration."""
        return await self._request(
            "GET",
            "server-config",
            response_model=ServerConfig
        )

    # Canvas Operations
    async def list_canvases(self, params: Optional[JsonData] = None) -> List[Canvas]:
        """List all available canvases."""
        return await self._request(
            "GET",
            "canvases",
            response_model=Canvas,
            params=self._parse_payload(params) if params else None
        )

    async def get_canvas(self, canvas_id: str) -> Canvas:
        """Get details of a specific canvas."""
        return await self._request(
            "GET",
            f"canvases/{canvas_id}",
            response_model=Canvas
        )

    async def create_canvas(self, payload: Dict[str, Any]) -> Canvas:
        """Create a new canvas."""
        return await self._request(
            "POST",
            "canvases",
            response_model=Canvas,
            json_data=payload
        )

    async def update_canvas(self, canvas_id: str, payload: Dict[str, Any]) -> Canvas:
        """Update canvas properties."""
        return await self._request(
            "PATCH",
            f"canvases/{canvas_id}",
            response_model=Canvas,
            json_data=payload
        )

    async def move_canvas(self, canvas_id: str, folder_id: str) -> Canvas:
        """Move a canvas to a different folder."""
        return await self._request(
            "POST",
            f"canvases/{canvas_id}/move",
            response_model=Canvas,
            json_data={"folder_id": folder_id}
        )

    async def copy_canvas(self, canvas_id: str, payload: Dict[str, Any]) -> Canvas:
        """Create a copy of a canvas."""
        return await self._request(
            "POST",
            f"canvases/{canvas_id}/copy",
            response_model=Canvas,
            json_data=payload
        )

    async def get_canvas_permissions(self, canvas_id: str) -> Dict[str, Any]:
        """Get canvas permissions."""
        return await self._request(
            "GET",
            f"canvases/{canvas_id}/permissions"
        )

    async def delete_canvas(self, canvas_id: str) -> None:
        """Delete a canvas."""
        await self._request(
            "DELETE",
            f"canvases/{canvas_id}"
        )

    # Folder Operations
    async def list_folders(self, params: Optional[JsonData] = None) -> List[CanvasFolder]:
        """List all available canvas folders."""
        return await self._request(
            "GET",
            "canvas-folders",
            response_model=CanvasFolder,
            params=self._parse_payload(params) if params else None
        )

    async def get_folder(self, folder_id: str) -> CanvasFolder:
        """Get details of a specific folder."""
        return await self._request(
            "GET",
            f"canvas-folders/{folder_id}",
            response_model=CanvasFolder
        )

    async def create_folder(self, payload: JsonData) -> CanvasFolder:
        """Create a new folder."""
        return await self._request(
            "POST",
            "canvas-folders",
            response_model=CanvasFolder,
            json_data=payload
        )

    async def update_folder(self, folder_id: str, payload: JsonData) -> CanvasFolder:
        """Update folder properties."""
        return await self._request(
            "PATCH",
            f"canvas-folders/{folder_id}",
            response_model=CanvasFolder,
            json_data=payload
        )

    async def move_folder(self, folder_id: str, payload: JsonData) -> CanvasFolder:
        """Move a folder to a different parent folder."""
        return await self._request(
            "POST",
            f"canvas-folders/{folder_id}/move",
            response_model=CanvasFolder,
            json_data=payload
        )

    async def delete_folder(self, folder_id: str) -> None:
        """Delete a folder."""
        await self._request(
            "DELETE",
            f"canvas-folders/{folder_id}"
        )

    # Demo Canvas Operations
    async def set_canvas_mode(self, canvas_id: str, is_demo: bool) -> Canvas:
        """Change a canvas between normal and demo mode."""
        return await self._request(
            "PATCH",
            f"canvases/{canvas_id}",
            response_model=Canvas,
            json_data={"mode": "demo" if is_demo else "normal"}
        )

    async def save_demo_state(self, canvas_id: str) -> None:
        """Save the current state of a demo canvas."""
        await self._request(
            "POST",
            f"canvases/{canvas_id}/save"
        )

    async def restore_demo_state(self, canvas_id: str) -> None:
        """Restore a demo canvas to its last saved state."""
        await self._request(
            "POST",
            f"canvases/{canvas_id}/restore"
        )

    # Permission Management
    async def set_canvas_permissions(self, canvas_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Set permission overrides on a canvas."""
        return await self._request(
            "POST",
            f"canvases/{canvas_id}/permissions",
            json_data=payload
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
        return await self._request(
            "GET",
            f"canvas-folders/{folder_id}/permissions"
        )

    async def set_folder_permissions(self, folder_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Set permission overrides on a folder."""
        return await self._request(
            "POST",
            f"canvas-folders/{folder_id}/permissions",
            json_data=payload
        )

    # Canvas Content Operations
    async def list_anchors(self, canvas_id: str) -> List[Anchor]:
        """List all anchors in a canvas."""
        return await self._request(
            "GET",
            f"canvases/{canvas_id}/anchors",
            response_model=Anchor
        )

    async def create_anchor(self, canvas_id: str, payload: JsonData) -> Anchor:
        """Create a new anchor in a canvas."""
        return await self._request(
            "POST",
            f"canvases/{canvas_id}/anchors",
            response_model=Anchor,
            json_data=payload
        )

    async def update_anchor(self, canvas_id: str, anchor_id: str, payload: JsonData) -> Anchor:
        """Update an existing anchor."""
        return await self._request(
            "PATCH",
            f"canvases/{canvas_id}/anchors/{anchor_id}",
            response_model=Anchor,
            json_data=payload
        )

    async def delete_anchor(self, canvas_id: str, anchor_id: str) -> None:
        """Delete an anchor."""
        await self._request(
            "DELETE",
            f"canvases/{canvas_id}/anchors/{anchor_id}"
        )

    async def list_notes(self, canvas_id: str) -> List[Note]:
        """List all notes in a canvas."""
        return await self._request(
            "GET",
            f"canvases/{canvas_id}/notes",
            response_model=Note
        )

    async def create_note(self, canvas_id: str, payload: Dict[str, Any]) -> Note:
        """Create a new note in a canvas."""
        return await self._request(
            "POST",
            f"canvases/{canvas_id}/notes",
            response_model=Note,
            json_data=payload
        )

    async def update_note(self, canvas_id: str, note_id: str, payload: Dict[str, Any]) -> Note:
        """Update a note in a canvas."""
        return await self._request(
            "PATCH",
            f"canvases/{canvas_id}/notes/{note_id}",
            response_model=Note,
            json_data=payload
        )

    async def delete_note(self, canvas_id: str, note_id: str) -> None:
        """Delete a note."""
        await self._request(
            "DELETE",
            f"canvases/{canvas_id}/notes/{note_id}"
        )

    async def list_images(self, canvas_id: str) -> List[Image]:
        """List all images in a canvas."""
        return await self._request(
            "GET",
            f"canvases/{canvas_id}/images",
            response_model=Image
        )

    async def create_image(self, canvas_id: str, file_path: str, payload: Optional[JsonData] = None) -> Image:
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
            form.add_field('json', json.dumps(self._parse_payload(payload)))
            
        # Add file
        file_handle = open(file_path, 'rb')
        try:
            form.add_field('data', file_handle)
            
            headers = {
                "Private-Token": self.api_key,
                "Accept": "application/json"
            }
            
            return await self._request(
                "POST",
                f"canvases/{canvas_id}/images",
                response_model=Image,
                headers=headers,
                data=form
            )
        finally:
            file_handle.close()

    async def update_image(self, canvas_id: str, image_id: str, payload: JsonData) -> Image:
        """Update an existing image."""
        return await self._request(
            "PATCH",
            f"canvases/{canvas_id}/images/{image_id}",
            response_model=Image,
            json_data=payload
        )

    async def delete_image(self, canvas_id: str, image_id: str) -> None:
        """Delete an image."""
        await self._request(
            "DELETE",
            f"canvases/{canvas_id}/images/{image_id}"
        )

    async def list_browsers(self, canvas_id: str) -> List[Browser]:
        """List all browser instances in a canvas."""
        return await self._request(
            "GET",
            f"canvases/{canvas_id}/browsers",
            response_model=Browser
        )

    async def create_browser(self, canvas_id: str, payload: Dict[str, Any]) -> Browser:
        """Create a new browser in a canvas."""
        return await self._request(
            "POST",
            f"canvases/{canvas_id}/browsers",
            response_model=Browser,
            json_data=payload
        )

    async def update_browser(self, canvas_id: str, browser_id: str, payload: Dict[str, Any]) -> Browser:
        """Update a browser in a canvas."""
        return await self._request(
            "PATCH",
            f"canvases/{canvas_id}/browsers/{browser_id}",
            response_model=Browser,
            json_data=payload
        )

    async def delete_browser(self, canvas_id: str, browser_id: str) -> None:
        """Delete a browser instance."""
        await self._request(
            "DELETE",
            f"canvases/{canvas_id}/browsers/{browser_id}"
        )

    async def list_videos(self, canvas_id: str) -> List[Video]:
        """List all videos in a canvas."""
        return await self._request(
            "GET",
            f"canvases/{canvas_id}/videos",
            response_model=Video
        )

    async def create_video(self, canvas_id: str, file_path: str, payload: Optional[JsonData] = None) -> Video:
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
            form.add_field('json', json.dumps(self._parse_payload(payload)))
            
        # Add file
        file_handle = open(file_path, 'rb')
        try:
            form.add_field('data', file_handle)
            
            headers = {
                "Private-Token": self.api_key,
                "Accept": "application/json"
            }
            
            return await self._request(
                "POST",
                f"canvases/{canvas_id}/videos",
                response_model=Video,
                headers=headers,
                data=form
            )
        finally:
            file_handle.close()

    async def update_video(self, canvas_id: str, video_id: str, payload: JsonData) -> Video:
        """Update an existing video."""
        return await self._request(
            "PATCH",
            f"canvases/{canvas_id}/videos/{video_id}",
            response_model=Video,
            json_data=payload
        )

    async def delete_video(self, canvas_id: str, video_id: str) -> None:
        """Delete a video."""
        await self._request(
            "DELETE",
            f"canvases/{canvas_id}/videos/{video_id}"
        )

    async def list_pdfs(self, canvas_id: str) -> List[PDF]:
        """List all PDFs in a canvas."""
        return await self._request(
            "GET",
            f"canvases/{canvas_id}/pdfs",
            response_model=PDF
        )

    async def create_pdf(self, canvas_id: str, file_path: str, payload: Optional[JsonData] = None) -> PDF:
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
            form.add_field('json', json.dumps(self._parse_payload(payload)))
            
        # Add file
        file_handle = open(file_path, 'rb')
        try:
            form.add_field('data', file_handle)
            
            headers = {
                "Private-Token": self.api_key,
                "Accept": "application/json"
            }
            
            return await self._request(
                "POST",
                f"canvases/{canvas_id}/pdfs",
                response_model=PDF,
                headers=headers,
                data=form
            )
        finally:
            file_handle.close()

    async def update_pdf(self, canvas_id: str, pdf_id: str, payload: JsonData) -> PDF:
        """Update an existing PDF."""
        return await self._request(
            "PATCH",
            f"canvases/{canvas_id}/pdfs/{pdf_id}",
            response_model=PDF,
            json_data=payload
        )

    async def delete_pdf(self, canvas_id: str, pdf_id: str) -> None:
        """Delete a PDF."""
        await self._request(
            "DELETE",
            f"canvases/{canvas_id}/pdfs/{pdf_id}"
        )

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
        form.add_field('json', json.dumps(data))
            
        return await self._request(
            "POST",
            f"canvases/{canvas_id}/uploads-folder",
            data=form
        )

    async def upload_file(self, canvas_id: str, file_path: str, payload: Optional[JsonData] = None) -> Dict[str, Any]:
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
                raise CanvusAPIError("upload_type must be missing, empty or 'asset' for file uploads")
            form.add_field('json', json.dumps(data))
            
        # Add file data part
        with open(file_path, 'rb') as f:
            form.add_field('data', f)
            
        return await self._request(
            "POST",
            f"canvases/{canvas_id}/uploads-folder",
            data=form
        )

    # Widget Operations (Read-only)
    async def list_widgets(self, canvas_id: str) -> List[Widget]:
        """List all widgets in a canvas."""
        return await self._request(
            "GET",
            f"canvases/{canvas_id}/widgets",
            response_model=Widget
        )

    async def get_widget(self, canvas_id: str, widget_id: str) -> Widget:
        """Get details of a specific widget."""
        return await self._request(
            "GET",
            f"canvases/{canvas_id}/widgets/{widget_id}",
            response_model=Widget
        )

    async def get_anchor(self, canvas_id: str, anchor_id: str) -> Anchor:
        """Get details of a specific anchor."""
        return await self._request(
            "GET",
            f"canvases/{canvas_id}/anchors/{anchor_id}",
            response_model=Anchor
        )

    async def get_note(self, canvas_id: str, note_id: str) -> Note:
        """Get details of a specific note."""
        return await self._request(
            "GET",
            f"canvases/{canvas_id}/notes/{note_id}",
            response_model=Note
        )

    async def get_image(self, canvas_id: str, image_id: str) -> Image:
        """Get details of a specific image."""
        return await self._request(
            "GET",
            f"canvases/{canvas_id}/images/{image_id}",
            response_model=Image
        )

    async def download_image(self, canvas_id: str, image_id: str) -> bytes:
        """Download an image's binary content."""
        return await self._request(
            "GET",
            f"canvases/{canvas_id}/images/{image_id}/download",
            return_binary=True
        )

    async def get_browser(self, canvas_id: str, browser_id: str) -> Browser:
        """Get details of a specific browser instance."""
        return await self._request(
            "GET",
            f"canvases/{canvas_id}/browsers/{browser_id}",
            response_model=Browser
        )

    async def get_video(self, canvas_id: str, video_id: str) -> Video:
        """Get details of a specific video."""
        return await self._request(
            "GET",
            f"canvases/{canvas_id}/videos/{video_id}",
            response_model=Video
        )

    async def download_video(self, canvas_id: str, video_id: str) -> bytes:
        """Download a video's binary content."""
        return await self._request(
            "GET",
            f"canvases/{canvas_id}/videos/{video_id}/download",
            return_binary=True
        )

    async def get_pdf(self, canvas_id: str, pdf_id: str) -> PDF:
        """Get details of a specific PDF."""
        return await self._request(
            "GET",
            f"canvases/{canvas_id}/pdfs/{pdf_id}",
            response_model=PDF
        )

    async def download_pdf(self, canvas_id: str, pdf_id: str) -> bytes:
        """Download a PDF's binary content."""
        return await self._request(
            "GET",
            f"canvases/{canvas_id}/pdfs/{pdf_id}/download",
            return_binary=True
        )

    # Connector Operations
    async def list_connectors(self, canvas_id: str) -> List[Connector]:
        """List all connectors in a canvas."""
        return await self._request(
            "GET",
            f"canvases/{canvas_id}/connectors",
            response_model=Connector
        )

    async def get_connector(self, canvas_id: str, connector_id: str) -> Connector:
        """Get details of a specific connector."""
        return await self._request(
            "GET",
            f"canvases/{canvas_id}/connectors/{connector_id}",
            response_model=Connector
        )

    async def create_connector(self, canvas_id: str, payload: Dict[str, Any]) -> Connector:
        """Create a new connector in a canvas."""
        return await self._request(
            "POST",
            f"canvases/{canvas_id}/connectors",
            response_model=Connector,
            json_data=payload
        )

    async def update_connector(self, canvas_id: str, connector_id: str, payload: Dict[str, Any]) -> Connector:
        """Update a connector in a canvas."""
        return await self._request(
            "PATCH",
            f"canvases/{canvas_id}/connectors/{connector_id}",
            response_model=Connector,
            json_data=payload
        )

    async def delete_connector(self, canvas_id: str, connector_id: str) -> None:
        """Delete a connector."""
        await self._request(
            "DELETE",
            f"canvases/{canvas_id}/connectors/{connector_id}"
        )

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
            "GET",
            f"users/{user_id}/access-tokens",
            response_model=AccessToken
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
            response_model=AccessToken
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
            json_data={"description": description}
        )

    async def update_token(self, user_id: int, token_id: str, description: str) -> AccessToken:
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
            json_data={"description": description}
        )

    async def delete_token(self, user_id: int, token_id: str) -> None:
        """Delete an access token.
        
        The token is revoked and can no longer be used.
        
        Args:
            user_id (int): The ID of the user
            token_id (str): The ID of the token to delete
        """
        await self._request(
            "DELETE",
            f"users/{user_id}/access-tokens/{token_id}"
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
            "GET",
            f"clients/{client_id}/workspaces",
            response_model=Workspace
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
            response_model=Workspace
        )

    async def update_workspace(
        self, 
        client_id: str, 
        workspace_index: int,
        payload: Dict[str, Any]
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
            json_data=payload
        )

    # Client Operations
    async def list_clients(self) -> List[Dict[str, Any]]:
        """List all connected clients."""
        return await self._request(
            "GET",
            "clients",
            response_model=None
        )

    async def get_client_workspaces(self, client_id: str) -> List[Workspace]:
        """Get workspaces for a specific client."""
        return await self._request(
            "GET",
            f"clients/{client_id}/workspaces",
            response_model=Workspace
        )

    async def find_admin_client(self, admin_email: str = "admin@local.local") -> Optional[str]:
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