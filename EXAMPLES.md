# Canvus Python API - Usage Examples

This document provides comprehensive examples for using the Canvus Python API client library.

## Table of Contents

- [Installation](#installation)
- [Basic Setup](#basic-setup)
- [Server Management](#server-management)
- [Canvas Management](#canvas-management)
- [Canvas Content](#canvas-content)
- [User Management](#user-management)
- [Groups](#groups)
- [Video Inputs & Outputs](#video-inputs--outputs)
- [License Management](#license-management)
- [Audit Log](#audit-log)
- [Mipmaps & Assets](#mipmaps--assets)
- [Annotations](#annotations)
- [Error Handling](#error-handling)
- [Advanced Features](#advanced-features)
- [Advanced Patterns](#advanced-patterns)

## Installation

```bash
pip install canvus-api
```

## Basic Setup

```python
import asyncio
from canvus_api import CanvusClient, CanvusAPIError

async def main():
    # Create client with your server URL and API token
    async with CanvusClient("https://your-canvus-server.com", "your-api-token") as client:
        # Your API calls here
        pass

# Run the async function
asyncio.run(main())
```

## Server Management

### Get Server Information

```python
async def get_server_info(client):
    """Get server information and configuration."""
    try:
        # Get server info
        info = await client.get_server_info()
        print(f"Server version: {info.version}")
        print(f"API versions: {info.api}")
        print(f"Server ID: {info.server_id}")
        
        # Get server configuration
        config = await client.get_server_config()
        print(f"Server name: {config.server_name}")
        print(f"Features: {config.features}")
        
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

### Update Server Configuration

```python
async def update_server_config(client):
    """Update server configuration."""
    try:
        # Update server name
        updated_config = await client.update_server_config({
            "server_name": "My Canvus Server"
        })
        print(f"Updated server name: {updated_config.server_name}")
        
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

### Send Test Email

```python
async def send_test_email(client):
    """Send a test email to verify email configuration."""
    try:
        result = await client.send_test_email()
        print(f"Test email result: {result}")
        
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

## Canvas Management

### List and Create Canvases

```python
async def manage_canvases(client):
    """List and create canvases."""
    try:
        # List all canvases
        canvases = await client.list_canvases()
        print(f"Found {len(canvases)} canvases")
        
        # Create a new canvas
        new_canvas = await client.create_canvas({
            "name": "My New Canvas",
            "description": "A canvas created via API",
            "folder_id": "folder-123"  # Optional
        })
        print(f"Created canvas: {new_canvas.name} (ID: {new_canvas.id})")
        
        # Get canvas details
        canvas = await client.get_canvas(new_canvas.id)
        print(f"Canvas mode: {canvas.mode}")
        print(f"Canvas state: {canvas.state}")
        
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

### Canvas Preview

```python
async def get_canvas_preview(client, canvas_id):
    """Get canvas preview image."""
    try:
        preview_data = await client.get_canvas_preview(canvas_id)
        
        # Save preview to file
        with open("canvas_preview.jpg", "wb") as f:
            f.write(preview_data)
        print("Canvas preview saved to canvas_preview.jpg")
        
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

### Canvas Background Management

```python
async def manage_canvas_background(client, canvas_id):
    """Manage canvas background."""
    try:
        # Get current background
        background = await client.get_canvas_background(canvas_id)
        print(f"Current background: {background}")
        
        # Set color background
        color_bg = await client.set_canvas_background(canvas_id, {
            "type": "color",
            "color": "#ff0000",
            "opacity": 0.8
        })
        print(f"Set color background: {color_bg}")
        
        # Set image background
        image_bg = await client.set_canvas_background_image(canvas_id, "background.jpg")
        print(f"Set image background: {image_bg}")
        
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

## Canvas Content

### Notes

```python
async def manage_notes(client, canvas_id):
    """Create and manage notes in a canvas."""
    try:
        # Create a note
        note = await client.create_note(canvas_id, {
            "text": "This is a test note",
            "title": "Test Note",
            "location": {"x": 100, "y": 100},
            "size": {"width": 200, "height": 150},
            "text_color": "#000000",
            "background_color": "#ffffff"
        })
        print(f"Created note: {note.text}")
        
        # Update the note
        updated_note = await client.update_note(canvas_id, note.id, {
            "text": "Updated note text",
            "text_color": "#ff0000"
        })
        print(f"Updated note: {updated_note.text}")
        
        # List all notes
        notes = await client.list_notes(canvas_id)
        print(f"Canvas has {len(notes)} notes")
        
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

### Images

```python
async def manage_images(client, canvas_id):
    """Upload and manage images in a canvas."""
    try:
        # Upload an image
        image = await client.create_image(canvas_id, "path/to/image.jpg", {
            "title": "My Image",
            "location": {"x": 200, "y": 200},
            "size": {"width": 300, "height": 200}
        })
        print(f"Uploaded image: {image.original_filename}")
        
        # Download the image
        image_data = await client.download_image(canvas_id, image.id)
        with open("downloaded_image.jpg", "wb") as f:
            f.write(image_data)
        print("Image downloaded successfully")
        
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

### Widgets

```python
async def manage_widgets(client, canvas_id):
    """Create and manage generic widgets."""
    try:
        # Create a custom widget
        widget = await client.create_widget(canvas_id, {
            "widget_type": "CustomWidget",
            "location": {"x": 300, "y": 300},
            "size": {"width": 250, "height": 100},
            "config": {
                "custom_property": "value",
                "enabled": True
            }
        })
        print(f"Created widget: {widget.widget_type}")
        
        # Update widget
        updated_widget = await client.update_widget(canvas_id, widget.id, {
            "config": {
                "custom_property": "updated_value",
                "enabled": False
            }
        })
        print(f"Updated widget config: {updated_widget.config}")
        
        # Delete widget
        await client.delete_widget(canvas_id, widget.id)
        print("Widget deleted")
        
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

## User Management

### User Operations

```python
async def manage_users(client):
    """Manage users (admin only)."""
    try:
        # List all users
        users = await client.list_users()
        print(f"Found {len(users)} users")
        
        # Create a new user
        new_user = await client.create_user({
            "email": "newuser@example.com",
            "name": "New User",
            "password": "securepassword123",
            "admin": False
        })
        print(f"Created user: {new_user.name}")
        
        # Update user
        updated_user = await client.update_user(new_user.id, {
            "name": "Updated User Name"
        })
        print(f"Updated user: {updated_user.name}")
        
        # Block user
        await client.block_user(new_user.id)
        print("User blocked")
        
        # Unblock user
        await client.unblock_user(new_user.id)
        print("User unblocked")
        
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

### Authentication

```python
async def authenticate_user(client):
    """User authentication examples."""
    try:
        # Login with email/password
        login_result = await client.login("user@example.com", "password")
        print(f"Login successful: {login_result}")
        
        # Login with token
        token_login = await client.login(token="your-token")
        print(f"Token login successful: {token_login}")
        
        # Logout
        await client.logout("your-token")
        print("Logout successful")
        
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

### Access Tokens

```python
async def manage_tokens(client, user_id):
    """Manage access tokens for a user."""
    try:
        # List user tokens
        tokens = await client.list_tokens(user_id)
        print(f"User has {len(tokens)} tokens")
        
        # Create new token
        token = await client.create_token(user_id, "API Token for automation")
        print(f"Created token: {token.id}")
        print(f"Plain token: {token.plain_token}")  # Only available on creation
        
        # Update token description
        updated_token = await client.update_token(user_id, token.id, "Updated description")
        print(f"Updated token: {updated_token.description}")
        
        # Delete token
        await client.delete_token(user_id, token.id)
        print("Token deleted")
        
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

## Groups

### Group Management

```python
async def manage_groups(client):
    """Manage user groups."""
    try:
        # List all groups
        groups = await client.list_groups()
        print(f"Found {len(groups)} groups")
        
        # Create a new group
        group = await client.create_group({
            "name": "Developers",
            "description": "Development team members"
        })
        print(f"Created group: {group['name']}")
        
        # Get group details
        group_details = await client.get_group(group['id'])
        print(f"Group description: {group_details['description']}")
        
        # Add user to group
        await client.add_user_to_group(group['id'], "user-123")
        print("User added to group")
        
        # List group members
        members = await client.list_group_members(group['id'])
        print(f"Group has {len(members)} members")
        
        # Remove user from group
        await client.remove_user_from_group(group['id'], "user-123")
        print("User removed from group")
        
        # Delete group
        await client.delete_group(group['id'])
        print("Group deleted")
        
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

## Video Inputs & Outputs

### Video Input Management

```python
async def manage_video_inputs(client, canvas_id):
    """Manage video input widgets."""
    try:
        # List canvas video inputs
        inputs = await client.list_canvas_video_inputs(canvas_id)
        print(f"Canvas has {len(inputs)} video inputs")
        
        # Create video input
        video_input = await client.create_video_input(canvas_id, {
            "name": "Camera 1",
            "source": "camera_1",
            "location": {"x": 100, "y": 100},
            "size": {"width": 640, "height": 480},
            "config": {
                "fps": 30,
                "resolution": "720p"
            },
            "depth": 1,
            "scale": 1.0,
            "pinned": False
        })
        print(f"Created video input: {video_input['name']}")
        
        # Delete video input
        await client.delete_video_input(canvas_id, video_input['id'])
        print("Video input deleted")
        
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

### Video Output Management

```python
async def manage_video_outputs(client, client_id):
    """Manage video outputs for a client."""
    try:
        # List client video outputs
        outputs = await client.list_client_video_outputs(client_id)
        print(f"Client has {len(outputs)} video outputs")
        
        # Set video output source
        updated_output = await client.set_video_output_source(client_id, 0, {
            "source": "canvas-1",
            "enabled": True,
            "resolution": "1920x1080",
            "refresh_rate": 60
        })
        print(f"Updated output source: {updated_output['source']}")
        
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

## License Management

### License Information

```python
async def get_license_info(client):
    """Get license information."""
    try:
        license_info = await client.get_license_info()
        print(f"License status: {license_info['status']}")
        print(f"License type: {license_info['type']}")
        print(f"Max users: {license_info['max_users']}")
        print(f"Max canvases: {license_info['max_canvases']}")
        print(f"Features: {license_info['features']}")
        
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

### Offline License Activation

```python
async def offline_license_activation(client):
    """Handle offline license activation."""
    try:
        # Request offline activation
        activation_request = await client.request_offline_activation("LICENSE-KEY-123")
        print(f"Activation request data: {activation_request['request_data']}")
        print(f"Expires at: {activation_request['expires_at']}")
        
        # Install offline license (after getting activation data from another machine)
        license_data = "offline_license_data_here"
        result = await client.install_offline_license(license_data)
        print(f"License installation result: {result}")
        
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

## Audit Log

### Audit Log Operations

```python
async def audit_log_operations(client):
    """Work with audit logs."""
    try:
        # Get audit log with filters
        audit_log = await client.get_audit_log({
            "user_id": "user-123",
            "action": "canvas_created",
            "limit": 50
        })
        print(f"Found {len(audit_log['entries'])} audit entries")
        
        # Export audit log as CSV
        csv_data = await client.export_audit_log_csv({
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        })
        
        # Save CSV to file
        with open("audit_log.csv", "wb") as f:
            f.write(csv_data)
        print("Audit log exported to audit_log.csv")
        
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

## Mipmaps & Assets

### Mipmap Operations

```python
async def mipmap_operations(client, canvas_id):
    """Work with mipmaps and assets."""
    try:
        # Get mipmap info
        mipmap_info = await client.get_mipmap_info("hash123", canvas_id)
        print(f"Mipmap levels: {mipmap_info['levels']}")
        print(f"Format: {mipmap_info['format']}")
        
        # Get mipmap level image
        level_image = await client.get_mipmap_level_image("hash123", 0, canvas_id)
        with open("mipmap_level_0.webp", "wb") as f:
            f.write(level_image)
        print("Mipmap level image saved")
        
        # Get asset file
        asset_data = await client.get_asset_file("hash123", canvas_id)
        with open("asset_file", "wb") as f:
            f.write(asset_data)
        print("Asset file downloaded")
        
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

## Annotations

### Annotation Operations

```python
async def annotation_operations(client, canvas_id):
    """Work with widget annotations."""
    try:
        # List widget annotations
        annotations = await client.list_widget_annotations(canvas_id)
        print(f"Found {len(annotations)} annotations")
        
        for annotation in annotations:
            print(f"Annotation: {annotation['type']} - {annotation['content']}")
        
        # Subscribe to annotation changes
        async for update in client.subscribe_annotations(canvas_id):
            print(f"Annotation update: {update}")
            # Process annotation updates in real-time
            
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

## Error Handling

### Comprehensive Error Handling

```python
async def robust_api_calls(client):
    """Example of robust error handling."""
    try:
        # Attempt API call
        result = await client.get_canvas("non-existent-id")
        
    except CanvusAPIError as e:
        if e.status_code == 404:
            print("Canvas not found")
        elif e.status_code == 401:
            print("Authentication failed")
        elif e.status_code == 403:
            print("Permission denied")
        elif e.status_code == 429:
            print("Rate limit exceeded")
        elif e.status_code == 408:
            print("Request timeout")
        else:
            print(f"API error: {e.status_code} - {e}")
            
    except Exception as e:
        print(f"Unexpected error: {e}")
```

### Enhanced Error Handling with Retry Logic

```python
async def robust_api_with_retry(client):
    """Example using enhanced error handling with automatic retry."""
    try:
        # Client automatically retries on transient failures
        result = await client.get_canvas("canvas-id")
        
    except RateLimitError as e:
        print(f"Rate limit exceeded: {e}")
        # Client automatically retries with exponential backoff
        
    except TimeoutError as e:
        print(f"Request timeout: {e}")
        # Client automatically retries with exponential backoff
        
    except ServerError as e:
        print(f"Server error: {e}")
        # Client automatically retries on 5xx errors
```

## Advanced Features

### Advanced Filtering

```python
async def advanced_filtering(client, canvas_id):
    """Use advanced filtering system."""
    from canvus_api.filters import Filter
    
    try:
        # Filter notes with specific text
        text_filter = Filter('{"widget_type": "Note", "text": "*important*"}')
        important_notes = await client.list_widgets(canvas_id, filter=text_filter)
        print(f"Found {len(important_notes)} important notes")
        
        # Filter by location
        location_filter = Filter('{"location.x": {"$gt": 100}, "location.y": {"$lt": 300}}')
        positioned_widgets = await client.list_widgets(canvas_id, filter=location_filter)
        print(f"Found {len(positioned_widgets)} widgets in position range")
        
        # Complex filter with multiple conditions
        complex_filter = Filter('''{
            "$and": [
                {"widget_type": "Note"},
                {"size.width": {"$gt": 150}},
                {"text": {"$regex": ".*test.*"}}
            ]
        }''')
        filtered_widgets = await client.list_widgets(canvas_id, filter=complex_filter)
        print(f"Found {len(filtered_widgets)} matching widgets")
        
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

### Spatial Operations

```python
async def spatial_operations(client, canvas_id):
    """Use spatial operations and geometry utilities."""
    from canvus_api.geometry import Rectangle, Point, widget_bounding_box, widgets_intersect
    
    try:
        # Get all widgets
        widgets = await client.list_widgets(canvas_id)
        
        # Create a search area
        search_area = Rectangle(x=100, y=100, width=400, height=300)
        
        # Find widgets in the search area
        widgets_in_area = []
        for widget in widgets:
            try:
                bbox = widget_bounding_box(widget)
                if bbox.x >= search_area.x and bbox.y >= search_area.y and \
                   bbox.x + bbox.width <= search_area.x + search_area.width and \
                   bbox.y + bbox.height <= search_area.y + search_area.height:
                    widgets_in_area.append(widget)
            except (ValueError, AttributeError):
                continue
        
        print(f"Found {len(widgets_in_area)} widgets in search area")
        
        # Check for intersecting widgets
        for i, widget1 in enumerate(widgets):
            for j, widget2 in enumerate(widgets[i+1:], i+1):
                try:
                    if widgets_intersect(widget1, widget2):
                        print(f"Widgets {widget1.id} and {widget2.id} intersect")
                except (ValueError, AttributeError):
                    continue
                    
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

### Cross-Canvas Search

```python
async def cross_canvas_search(client):
    """Search for widgets across all canvases."""
    from canvus_api.search import find_widgets_across_canvases
    
    try:
        # Search for notes containing "important"
        results = await find_widgets_across_canvases(client, '{"text": "*important*"}')
        
        print(f"Found {len(results)} widgets across all canvases:")
        for result in results:
            canvas_id = result['canvas_id']
            widget = result['widget']
            print(f"  Canvas {canvas_id}: {widget.widget_type} - {widget.id}")
            
        # Search for large images
        large_images = await find_widgets_across_canvases(client, 
            '{"widget_type": "Image", "size.width": {"$gt": 300}}')
        
        print(f"Found {len(large_images)} large images")
        
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

### Import/Export System

```python
async def import_export_example(client, canvas_id):
    """Export and import widgets with assets."""
    from canvus_api.export import export_widgets_to_folder, import_widgets_from_folder
    
    try:
        # Export widgets to folder
        export_path = "exported_widgets"
        await export_widgets_to_folder(client, canvas_id, export_path)
        print(f"Exported widgets to {export_path}")
        
        # Create a new canvas for import
        new_canvas = await client.create_canvas({
            "name": "Imported Canvas",
            "description": "Canvas with imported widgets"
        })
        
        # Import widgets to new canvas
        await import_widgets_from_folder(client, new_canvas.id, export_path)
        print(f"Imported widgets to canvas {new_canvas.id}")
        
        # Verify import
        imported_widgets = await client.list_widgets(new_canvas.id)
        print(f"Imported {len(imported_widgets)} widgets")
        
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

### Advanced Widget Operations

```python
async def advanced_widget_operations(client, canvas_id):
    """Use advanced widget operations and spatial grouping."""
    from canvus_api.widget_operations import (
        WidgetZoneManager, BatchWidgetOperations, 
        create_spatial_group, find_widget_clusters
    )
    
    try:
        # Get all widgets
        widgets = await client.list_widgets(canvas_id)
        
        # Create spatial zones
        zone_manager = WidgetZoneManager()
        
        # Group widgets by spatial proximity
        spatial_groups = create_spatial_group(widgets, tolerance=50.0)
        print(f"Created {len(spatial_groups)} spatial groups")
        
        # Find clusters of widgets
        clusters = find_widget_clusters(widgets, min_cluster_size=3, tolerance=100.0)
        print(f"Found {len(clusters)} widget clusters")
        
        # Create zones for each cluster
        zones = []
        for i, cluster in enumerate(clusters):
            zone = zone_manager.create_zone_from_widgets(
                cluster, 
                f"Zone {i+1}", 
                f"Zone containing {len(cluster)} widgets"
            )
            zones.append(zone)
            print(f"Created zone: {zone.name}")
        
        # Perform batch operations
        batch_ops = BatchWidgetOperations()
        
        # Move all notes by 50 pixels to the right
        notes = [w for w in widgets if w.widget_type == "Note"]
        move_operations = batch_ops.move_widgets(notes, offset_x=50, offset_y=0)
        print(f"Generated {len(move_operations)} move operations")
        
        # Resize all images by 1.2x
        images = [w for w in widgets if w.widget_type == "Image"]
        resize_operations = batch_ops.resize_widgets(images, scale_factor=1.2)
        print(f"Generated {len(resize_operations)} resize operations")
        
        # Find widgets that contain a specific widget
        if widgets:
            target_widget = widgets[0]
            containers = batch_ops.widgets_contain_id(widgets, target_widget.id)
            print(f"Found {len(containers)} widgets containing {target_widget.id}")
            
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

## Advanced Patterns

### Batch Operations

```python
async def batch_operations(client, canvas_id):
    """Perform batch operations."""
    try:
        # Create multiple notes in batch
        note_data = [
            {"text": f"Note {i}", "location": {"x": i * 100, "y": 100}}
            for i in range(5)
        ]
        
        created_notes = []
        for data in note_data:
            note = await client.create_note(canvas_id, data)
            created_notes.append(note)
        
        print(f"Created {len(created_notes)} notes")
        
        # Clean up
        for note in created_notes:
            await client.delete_note(canvas_id, note.id)
        print("Cleaned up all notes")
        
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

### Real-time Updates

```python
async def real_time_updates(client, canvas_id):
    """Subscribe to real-time updates."""
    try:
        # Subscribe to widget updates
        async for update in client.subscribe_widgets(canvas_id):
            print(f"Widget update: {update['widget_type']} - {update['id']}")
            
            # Process different widget types
            if update['widget_type'] == 'Note':
                print(f"Note text: {update.get('text', 'No text')}")
            elif update['widget_type'] == 'Image':
                print(f"Image filename: {update.get('original_filename', 'No filename')}")
                
    except CanvusAPIError as e:
        print(f"Error: {e}")
```

### File Upload with Progress

```python
async def upload_with_progress(client, canvas_id, file_path):
    """Upload file with progress tracking."""
    try:
        # Get file size for progress calculation
        import os
        file_size = os.path.getsize(file_path)
        
        print(f"Uploading {file_path} ({file_size} bytes)")
        
        # Upload file (progress tracking would be implemented in the client)
        if file_path.endswith('.jpg') or file_path.endswith('.png'):
            result = await client.create_image(canvas_id, file_path, {
                "title": "Uploaded Image"
            })
        elif file_path.endswith('.pdf'):
            result = await client.create_pdf(canvas_id, file_path, {
                "title": "Uploaded PDF"
            })
        elif file_path.endswith('.mp4'):
            result = await client.create_video(canvas_id, file_path, {
                "title": "Uploaded Video"
            })
        
        print(f"Upload completed: {result.id}")
        
    except CanvusAPIError as e:
        print(f"Upload error: {e}")
```

## Complete Example

Here's a complete example that demonstrates multiple API features:

```python
import asyncio
from canvus_api import CanvusClient, CanvusAPIError

async def complete_example():
    """Complete example demonstrating multiple API features."""
    
    async with CanvusClient("https://your-canvus-server.com", "your-api-token") as client:
        try:
            # 1. Get server information
            info = await client.get_server_info()
            print(f"Connected to Canvus server version {info.version}")
            
            # 2. Create a canvas
            canvas = await client.create_canvas({
                "name": "API Demo Canvas",
                "description": "Canvas created via Python API"
            })
            print(f"Created canvas: {canvas.name}")
            
            # 3. Add a note to the canvas
            note = await client.create_note(canvas.id, {
                "text": "Hello from Python API!",
                "location": {"x": 100, "y": 100},
                "size": {"width": 200, "height": 100}
            })
            print(f"Added note: {note.text}")
            
            # 4. Upload an image
            image = await client.create_image(canvas.id, "demo_image.jpg", {
                "title": "Demo Image",
                "location": {"x": 300, "y": 100}
            })
            print(f"Uploaded image: {image.original_filename}")
            
            # 5. Set canvas background
            await client.set_canvas_background(canvas.id, {
                "type": "color",
                "color": "#f0f0f0"
            })
            print("Set canvas background")
            
            # 6. Get canvas preview
            preview = await client.get_canvas_preview(canvas.id)
            with open("canvas_preview.jpg", "wb") as f:
                f.write(preview)
            print("Saved canvas preview")
            
            # 7. Clean up
            await client.delete_canvas(canvas.id)
            print("Demo completed and cleaned up")
            
        except CanvusAPIError as e:
            print(f"API Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(complete_example())
```

This comprehensive examples file covers all the major features of the Canvus Python API. Users can refer to specific sections for their use cases and adapt the examples to their needs. 