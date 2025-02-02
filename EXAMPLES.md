# Canvus API Client Examples

This document provides practical examples of using the Canvus API client.

## Basic Setup

```python
from canvus_api import CanvusClient, CanvusAPIError
import json

# Initialize the client
async with CanvusClient(
    base_url="https://your-canvus-server.com/api/v1",
    api_key="your-api-key"
) as client:
    # API calls will go here
    pass
```

## Working with Payloads

### Using Dictionary Payloads

```python
# Define payload as a dictionary
canvas_payload = {
    "name": "My New Canvas",
    "width": 1920,
    "height": 1080,
    "description": "Created via API",
    "folder_id": None,
    "background_color": "#FFFFFF"
}

canvas = await client.create_canvas(canvas_payload)
```

### Using JSON Files

```python
# Load payload from a JSON file
with open("payloads/create_canvas.json", "r") as f:
    canvas_payload = json.load(f)
    
canvas = await client.create_canvas(canvas_payload)
```

Example `payloads/create_canvas.json`:
```json
{
    "name": "My New Canvas",
    "width": 1920,
    "height": 1080,
    "description": "Created via API",
    "folder_id": null,
    "background_color": "#FFFFFF"
}
```

## Subscribing to Updates

### Widget Updates

```python
async def handle_widget_update(widget):
    """Handle widget update events."""
    print(f"Widget type: {widget.__class__.__name__}")
    if hasattr(widget, 'content'):
        print(f"Content: {widget.content}")  # For notes
    if hasattr(widget, 'url'):
        print(f"URL: {widget.url}")  # For browsers
    print(f"Location: ({widget.location.x}, {widget.location.y})")

# Subscribe to all widget updates in a canvas
async for widget in client.subscribe_widgets("canvas-id", callback=handle_widget_update):
    # Process widget updates as they arrive
    print(f"Received update for widget: {widget.id}")
```

### Note Updates

```python
async def handle_note_update(note):
    """Handle note update events."""
    print(f"Note content: {note.content}")
    print(f"Location: ({note.location.x}, {note.location.y})")
    print(f"Background color: {note.background_color}")

# Subscribe to updates for a specific note
async for note in client.subscribe_note("canvas-id", "note-id", callback=handle_note_update):
    # Process note updates as they arrive
    print(f"Received update for note: {note.id}")
```

### Workspace Updates

```python
async def handle_workspace_update(update):
    """Handle workspace update events."""
    print(f"Workspace updated: {update.workspace_name}")
    print(f"View rectangle: {update.view_rectangle}")

# Subscribe to workspace updates
async for update in client.subscribe_workspace(
    "client-id",
    workspace_index=0,
    callback=handle_workspace_update
):
    # Process updates as they arrive
    print(f"Received update for workspace: {update.workspace_name}")
```

### Using Multiple Subscriptions

```python
import asyncio

async def monitor_widgets(client, canvas_id):
    """Monitor all widget updates in a canvas."""
    async for widget in client.subscribe_widgets(canvas_id):
        print(f"Widget {widget.id} updated: {widget}")

async def monitor_note(client, canvas_id, note_id):
    """Monitor updates for a specific note."""
    async for note in client.subscribe_note(canvas_id, note_id):
        print(f"Note {note_id} updated: {note.content}")

async def monitor_workspace(client, client_id, workspace_index):
    """Monitor updates for a specific workspace."""
    async for update in client.subscribe_workspace(client_id, workspace_index):
        print(f"Workspace {workspace_index} updated: {update}")

async def main():
    async with CanvusClient(...) as client:
        # Start multiple subscriptions concurrently
        await asyncio.gather(
            monitor_widgets(client, "canvas-1"),
            monitor_note(client, "canvas-1", "note-1"),
            monitor_workspace(client, "client-1", 0)
        )

# Run the monitoring tasks
asyncio.run(main())
```

## Error Handling

All examples should include error handling:

```python
try:
    result = await client.some_operation()
except CanvusAPIError as e:
    print(f"Error {e.status_code}: {e.message}")
```

## Authentication

### Creating an Access Token

```python
token_payload = {
    "description": "API access token for automation",
    "expiration": "2024-12-31T23:59:59Z"  # Optional: ISO 8601 date
}

token = await client.create_token(token_payload)
# Important: Save the plain token value, it's only available on creation
print(f"New token created: {token.plain_token}")
```

## Working with Canvases

### Creating and Managing Canvases

```python
# Create a new canvas with all possible fields
canvas_payload = {
    "name": "My New Canvas",
    "width": 1920,
    "height": 1080,
    "description": "Created via API",
    "folder_id": "parent-folder-uuid",
    "background_color": "#FFFFFF"
}
# Optional fields: description, folder_id, background_color

canvas = await client.create_canvas(canvas_payload)

# Update canvas with all possible fields
update_payload = {
    "name": "Updated Canvas Name",
    "description": "Updated via API",
    "background_color": "#F0F0F0"
}
# All fields are optional in updates

await client.update_canvas(canvas.id, update_payload)
```

## Working with Folders

### Organizing Canvases

```python
folder_payload = {
    "name": "My Projects",
    "parent_id": "parent-folder-uuid"
}
# Optional fields: parent_id

folder = await client.create_folder(folder_payload)
```

## Working with Widgets

### Notes

```python
note_payload = {
    "content": "Important meeting notes",
    "location": {
        "x": 100,
        "y": 100,
        "z": 0
    },
    "size": {
        "width": 200,
        "height": 150
    },
    "background_color": "#FFFF00",
    "text_color": "#000000",
    "font_size": 14
}
# Optional fields: z, background_color, text_color, font_size

note = await client.create_note(canvas_id, note_payload)
```

### Images

```python
# Upload an image (multipart form data)
with open("image.jpg", "rb") as f:
    image = await client.create_image(canvas_id, {
        "location": {"x": 300, "y": 200},
        "size": {"width": 400, "height": 300}
    }, file=f)
```

### Browsers

```python
browser_payload = {
    "url": "https://example.com",
    "location": {
        "x": 500,
        "y": 300,
        "z": 0
    },
    "size": {
        "width": 800,
        "height": 600
    },
    "title": "Example Website",
    "scroll_position": {
        "x": 0,
        "y": 0
    },
    "zoom_level": 1.0
}
# Optional fields: z, title, scroll_position, zoom_level

browser = await client.create_browser(canvas_id, browser_payload)
```

## Working with Clients and Workspaces

### Managing Workspaces

```python
workspace_payload = {
    "pinned": True,
    "info_panel_visible": True,
    "view_rectangle": {
        "x": 0,
        "y": 0,
        "width": 1000,
        "height": 800
    },
    "workspace_name": "Main Workspace",
    "workspace_state": "normal"
}
# Optional fields: workspace_name, workspace_state
# Required fields: pinned, info_panel_visible, view_rectangle

await client.update_workspace(client_id, workspace_index, workspace_payload)
```

### Opening a Canvas in a Workspace

```python
open_canvas_payload = {
    "canvas_id": canvas_id,
    "server_id": workspace.server_id
}
# Required fields: canvas_id, server_id

await client._request(
    "POST",
    f"clients/{client_id}/workspaces/{workspace_index}/open-canvas",
    json_data=open_canvas_payload
)
```

## Common Patterns

### Finding the Admin Client

```python
async def find_admin_client(client):
    """Find the client where admin@local.local is logged in."""
    clients = await client.list_clients()
    
    for client_info in clients:
        workspaces = await client.get_client_workspaces(client_info["id"])
        for workspace in workspaces:
            if workspace.user == "admin@local.local":
                return client_info["id"]
    return None
```

## Best Practices

1. Always handle errors appropriately
2. Save access tokens securely
3. Clean up resources (delete test canvases, etc.)
4. Restore workspace settings after modifying them
5. Use appropriate timeouts for operations that may take time
6. Validate responses using the provided models
7. Consider storing commonly used payloads in JSON files
8. Document which fields are optional vs required in your payloads 