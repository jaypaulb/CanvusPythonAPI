# Canvus API Client

A Python client for interacting with the Canvus API.

## Installation

```bash
pip install -r requirements.txt
```

## Features

### Access Token Management
- `list_tokens()` - List all access tokens
- `get_token(token_id)` - Get details of a specific token
- `create_token(token_data)` - Create a new access token
- `update_token(token_id, token_data)` - Update token properties
- `delete_token(token_id)` - Delete/revoke a token

### Server Operations
- `get_server_info()` - Get server version and status information
- `get_server_config()` - Get server configuration details

### Client Operations
- `list_clients()` - List all connected clients
- `get_client_workspaces(client_id)` - Get workspaces for a specific client
- `get_workspace(client_id, workspace_index)` - Get details of a specific workspace
- `update_workspace(client_id, workspace_index, settings)` - Update workspace settings

### Canvas Operations
- `list_canvases()` - List all available canvases
- `get_canvas(canvas_id)` - Get details of a specific canvas
- `create_canvas(canvas_data)` - Create a new canvas
- `update_canvas(canvas_id, canvas_data)` - Update canvas properties
- `delete_canvas(canvas_id)` - Delete a canvas

### Folder Operations
- `list_folders()` - List all canvas folders
- `get_folder(folder_id)` - Get details of a specific folder
- `create_folder(folder_data)` - Create a new folder
- `update_folder(folder_id, folder_data)` - Update folder properties
- `delete_folder(folder_id)` - Delete a folder

### Widget Operations

Generic widget endpoints (read-only):
- `list_widgets(canvas_id)` - List all widgets in a canvas
- `get_widget(canvas_id, widget_id)` - Get details of a specific widget

Direct widget type endpoints (full CRUD support):
- Notes: `list_notes()`, `get_note()`, `create_note()`, `update_note()`, `delete_note()`
- Images: `list_images()`, `get_image()`, `create_image()`, `update_image()`, `delete_image()`
- Browsers: `list_browsers()`, `get_browser()`, `create_browser()`, `update_browser()`, `delete_browser()`
- Videos: `list_videos()`, `get_video()`, `create_video()`, `update_video()`, `delete_video()`
- PDFs: `list_pdfs()`, `get_pdf()`, `create_pdf()`, `update_pdf()`, `delete_pdf()`
- Connectors: `list_connectors()`, `get_connector()`, `create_connector()`, `update_connector()`, `delete_connector()`

## Models

The client uses Pydantic models for request/response validation:

### Server Models
- `ServerInfo`: Server version, API version, and status information
- `ServerConfig`: Server configuration settings including features and authentication settings

### Client Models
- `Client`: Connected client information including ID, name, state, and server ID
- `Workspace`: Client workspace configuration including:
  - Canvas ID and server ID
  - Workspace name and index
  - View settings (pinned state, info panel visibility)
  - View rectangle (position and zoom)

### Canvas Models
- `Canvas`: Canvas properties including name, dimensions, description, and folder ID
- `CanvasFolder`: Folder properties including name, parent ID, and metadata

### Widget Models
- `BaseWidget`: Common widget properties
  - Location (x, y coordinates)
  - Size (width, height)
  - ID (server-assigned UUID)
  - State (widget lifecycle state)

- Widget Types (inherit from BaseWidget):
  - `Note`: Text content and styling properties
  - `Image`: Image metadata and file properties
  - `Browser`: Web browser widget with URL and settings
  - `Video`: Video player widget with source and playback settings
  - `PDF`: PDF viewer widget with document properties
  - `Connector`: Widget connection properties

### Access Control Models
- `AccessToken`: Token management including ID, description, and creation timestamp

## Error Handling

The client raises `CanvusAPIError` for API-related errors:
- Authentication errors (401)
- Permission denied (403)
- Resource not found (404)
- Validation errors (422)
- Server errors (500)

## Testing

## Configuration

Create a `config.json` file with your API credentials:

```json
{
    "base_url": "https://your-canvus-server.com/api/v1",
    "api_key": "your-api-key"
}
```

## Running Tests

Run the test suite:

```bash
python tests/test_canvus_api.py
```

The test suite includes:
- Server function tests (info, config)
- Folder operations tests
- Canvas operations tests
- Widget operations tests (notes, images, browsers, connectors)
- Client and workspace operations tests
- Token management tests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request 