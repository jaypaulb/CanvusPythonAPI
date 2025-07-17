# Comprehensive Canvus API Endpoints Table

This table provides a complete list of all Canvus API endpoints, organized by resource type. It includes HTTP methods, paths, key parameters, descriptions, and Python client method signatures.

## Server Management

| Resource | Method | Path | Key Parameters | Description | Python Method |
|----------|--------|------|----------------|-------------|---------------|
| Server Info | GET | `/server-info` | - | Get server information | `get_server_info()` |
| Server Config | GET | `/server-config` | - | Get server configuration | `get_server_config()` |
| Server Config | PATCH | `/server-config` | settings (body) | Update server settings | - |
| Server Config | POST | `/server-config/send-test-email` | - | Send test email | - |

## Canvas Management

| Resource | Method | Path | Key Parameters | Description | Python Method |
|----------|--------|------|----------------|-------------|---------------|
| Canvases | GET | `/canvases` | subscribe (query) | List all canvases | `list_canvases(params)` |
| Canvases | GET | `/canvases/:id` | id (path), subscribe (query) | Get a single canvas | `get_canvas(canvas_id)` |
| Canvases | POST | `/canvases` | name, folder_id (body) | Create a canvas | `create_canvas(payload)` |
| Canvases | PATCH | `/canvases/:id` | id (path), name, mode (body) | Update canvas properties | `update_canvas(canvas_id, payload)` |
| Canvases | DELETE | `/canvases/:id` | id (path) | Delete a canvas | `delete_canvas(canvas_id)` |
| Canvases | GET | `/canvases/:id/preview` | id (path) | Get canvas preview | - |
| Canvases | POST | `/canvases/:id/restore` | id (path) | Restore demo canvas | `restore_demo_state(canvas_id)` |
| Canvases | POST | `/canvases/:id/save` | id (path) | Save demo state | `save_demo_state(canvas_id)` |
| Canvases | POST | `/canvases/:id/move` | id, folder_id (path/body) | Move canvas to folder | `move_canvas(canvas_id, folder_id)` |
| Canvases | POST | `/canvases/:id/copy` | id, folder_id (path/body) | Copy a canvas | `copy_canvas(canvas_id, payload)` |
| Canvases | GET | `/canvases/:id/permissions` | id (path) | Get canvas permissions | `get_canvas_permissions(canvas_id)` |
| Canvases | POST | `/canvases/:id/permissions` | id (path), permissions (body) | Set canvas permissions | `set_canvas_permissions(canvas_id, payload)` |

## Canvas Folders

| Resource | Method | Path | Key Parameters | Description | Python Method |
|----------|--------|------|----------------|-------------|---------------|
| Canvas Folders | GET | `/canvas-folders` | subscribe (query) | List all folders | `list_folders(params)` |
| Canvas Folders | GET | `/canvas-folders/:id` | id (path), subscribe (query) | Get a single folder | `get_folder(folder_id)` |
| Canvas Folders | POST | `/canvas-folders` | name, folder_id (body) | Create a folder | `create_folder(payload)` |
| Canvas Folders | PATCH | `/canvas-folders/:id` | id (path), name (body) | Update folder properties | `update_folder(folder_id, payload)` |
| Canvas Folders | POST | `/canvas-folders/:id/move` | id, folder_id (path/body) | Move folder | `move_folder(folder_id, payload)` |
| Canvas Folders | POST | `/canvas-folders/:id/copy` | id, folder_id (path/body) | Copy a folder | - |
| Canvas Folders | DELETE | `/canvas-folders/:id` | id (path) | Delete a folder | `delete_folder(folder_id)` |
| Canvas Folders | DELETE | `/canvas-folders/:id/children` | id (path) | Delete all children of a folder | - |
| Canvas Folders | GET | `/canvas-folders/:id/permissions` | id (path) | Get folder permissions | `get_folder_permissions(folder_id)` |
| Canvas Folders | POST | `/canvas-folders/:id/permissions` | id (path), permissions (body) | Set folder permissions | `set_folder_permissions(folder_id, payload)` |

## Canvas Content - Notes

| Resource | Method | Path | Key Parameters | Description | Python Method |
|----------|--------|------|----------------|-------------|---------------|
| Notes | GET | `/canvases/:id/notes` | id (path) | List all notes in canvas | `list_notes(canvas_id)` |
| Notes | GET | `/canvases/:id/notes/:note_id` | id, note_id (path) | Get a single note | `get_note(canvas_id, note_id)` |
| Notes | POST | `/canvases/:id/notes` | id (path), note (body) | Create a note | `create_note(canvas_id, payload)` |
| Notes | PATCH | `/canvases/:id/notes/:note_id` | id, note_id (path), note (body) | Update a note | `update_note(canvas_id, note_id, payload)` |
| Notes | DELETE | `/canvases/:id/notes/:note_id` | id, note_id (path) | Delete a note | `delete_note(canvas_id, note_id)` |

## Canvas Content - Images

| Resource | Method | Path | Key Parameters | Description | Python Method |
|----------|--------|------|----------------|-------------|---------------|
| Images | GET | `/canvases/:id/images` | id (path) | List all images in canvas | `list_images(canvas_id)` |
| Images | GET | `/canvases/:id/images/:image_id` | id, image_id (path) | Get a single image | `get_image(canvas_id, image_id)` |
| Images | POST | `/canvases/:id/images` | id (path), image (multipart) | Create an image | `create_image(canvas_id, file_path, payload)` |
| Images | PATCH | `/canvases/:id/images/:image_id` | id, image_id (path), image (body) | Update an image | `update_image(canvas_id, image_id, payload)` |
| Images | DELETE | `/canvases/:id/images/:image_id` | id, image_id (path) | Delete an image | `delete_image(canvas_id, image_id)` |
| Images | GET | `/canvases/:id/images/:image_id/download` | id, image_id (path) | Download image binary | `download_image(canvas_id, image_id)` |

## Canvas Content - PDFs

| Resource | Method | Path | Key Parameters | Description | Python Method |
|----------|--------|------|----------------|-------------|---------------|
| PDFs | GET | `/canvases/:id/pdfs` | id (path) | List all PDFs in canvas | `list_pdfs(canvas_id)` |
| PDFs | GET | `/canvases/:id/pdfs/:pdf_id` | id, pdf_id (path) | Get a single PDF | `get_pdf(canvas_id, pdf_id)` |
| PDFs | POST | `/canvases/:id/pdfs` | id (path), pdf (multipart) | Create a PDF | `create_pdf(canvas_id, file_path, payload)` |
| PDFs | PATCH | `/canvases/:id/pdfs/:pdf_id` | id, pdf_id (path), pdf (body) | Update a PDF | `update_pdf(canvas_id, pdf_id, payload)` |
| PDFs | DELETE | `/canvases/:id/pdfs/:pdf_id` | id, pdf_id (path) | Delete a PDF | `delete_pdf(canvas_id, pdf_id)` |
| PDFs | GET | `/canvases/:id/pdfs/:pdf_id/download` | id, pdf_id (path) | Download PDF binary | `download_pdf(canvas_id, pdf_id)` |

## Canvas Content - Videos

| Resource | Method | Path | Key Parameters | Description | Python Method |
|----------|--------|------|----------------|-------------|---------------|
| Videos | GET | `/canvases/:id/videos` | id (path) | List all videos in canvas | `list_videos(canvas_id)` |
| Videos | GET | `/canvases/:id/videos/:video_id` | id, video_id (path) | Get a single video | `get_video(canvas_id, video_id)` |
| Videos | POST | `/canvases/:id/videos` | id (path), video (multipart) | Create a video | `create_video(canvas_id, file_path, payload)` |
| Videos | PATCH | `/canvases/:id/videos/:video_id` | id, video_id (path), video (body) | Update a video | `update_video(canvas_id, video_id, payload)` |
| Videos | DELETE | `/canvases/:id/videos/:video_id` | id, video_id (path) | Delete a video | `delete_video(canvas_id, video_id)` |
| Videos | GET | `/canvases/:id/videos/:video_id/download` | id, video_id (path) | Download video binary | `download_video(canvas_id, video_id)` |

## Canvas Content - Browsers

| Resource | Method | Path | Key Parameters | Description | Python Method |
|----------|--------|------|----------------|-------------|---------------|
| Browsers | GET | `/canvases/:id/browsers` | id (path) | List all browsers in canvas | `list_browsers(canvas_id)` |
| Browsers | GET | `/canvases/:id/browsers/:browser_id` | id, browser_id (path) | Get a single browser | `get_browser(canvas_id, browser_id)` |
| Browsers | POST | `/canvases/:id/browsers` | id (path), browser (body) | Create a browser | `create_browser(canvas_id, payload)` |
| Browsers | PATCH | `/canvases/:id/browsers/:browser_id` | id, browser_id (path), browser (body) | Update a browser | `update_browser(canvas_id, browser_id, payload)` |
| Browsers | DELETE | `/canvases/:id/browsers/:browser_id` | id, browser_id (path) | Delete a browser | `delete_browser(canvas_id, browser_id)` |

## Canvas Content - Anchors

| Resource | Method | Path | Key Parameters | Description | Python Method |
|----------|--------|------|----------------|-------------|---------------|
| Anchors | GET | `/canvases/:id/anchors` | id (path) | List all anchors in canvas | `list_anchors(canvas_id)` |
| Anchors | GET | `/canvases/:id/anchors/:anchor_id` | id, anchor_id (path) | Get a single anchor | `get_anchor(canvas_id, anchor_id)` |
| Anchors | POST | `/canvases/:id/anchors` | id (path), anchor (body) | Create an anchor | `create_anchor(canvas_id, payload)` |
| Anchors | PATCH | `/canvases/:id/anchors/:anchor_id` | id, anchor_id (path), anchor (body) | Update an anchor | `update_anchor(canvas_id, anchor_id, payload)` |
| Anchors | DELETE | `/canvases/:id/anchors/:anchor_id` | id, anchor_id (path) | Delete an anchor | `delete_anchor(canvas_id, anchor_id)` |

## Canvas Content - Connectors

| Resource | Method | Path | Key Parameters | Description | Python Method |
|----------|--------|------|----------------|-------------|---------------|
| Connectors | GET | `/canvases/:id/connectors` | id (path) | List all connectors in canvas | `list_connectors(canvas_id)` |
| Connectors | GET | `/canvases/:id/connectors/:connector_id` | id, connector_id (path) | Get a single connector | `get_connector(canvas_id, connector_id)` |
| Connectors | POST | `/canvases/:id/connectors` | id (path), connector (body) | Create a connector | `create_connector(canvas_id, payload)` |
| Connectors | PATCH | `/canvases/:id/connectors/:connector_id` | id, connector_id (path), connector (body) | Update a connector | `update_connector(canvas_id, connector_id, payload)` |
| Connectors | DELETE | `/canvases/:id/connectors/:connector_id` | id, connector_id (path) | Delete a connector | `delete_connector(canvas_id, connector_id)` |

## Canvas Content - Widgets

| Resource | Method | Path | Key Parameters | Description | Python Method |
|----------|--------|------|----------------|-------------|---------------|
| Widgets | GET | `/canvases/:id/widgets` | id (path) | List all widgets in canvas | `list_widgets(canvas_id)` |
| Widgets | GET | `/canvases/:id/widgets/:widget_id` | id, widget_id (path) | Get a single widget | `get_widget(canvas_id, widget_id)` |
| Widgets | POST | `/canvases/:id/widgets` | id (path), widget (body) | Create a widget | - |
| Widgets | PATCH | `/canvases/:id/widgets/:widget_id` | id, widget_id (path), widget (body) | Update a widget | - |
| Widgets | DELETE | `/canvases/:id/widgets/:widget_id` | id, widget_id (path) | Delete a widget | - |

## Canvas Backgrounds

| Resource | Method | Path | Key Parameters | Description | Python Method |
|----------|--------|------|----------------|-------------|---------------|
| Canvas Backgrounds | GET | `/canvases/:id/background` | id (path) | Get canvas background | - |
| Canvas Backgrounds | PATCH | `/canvases/:id/background` | id (path), background (body) | Set canvas background | - |
| Canvas Backgrounds | POST | `/canvases/:id/background` | id (path), image (multipart) | Set canvas background image | - |

## Canvas Color Presets

| Resource | Method | Path | Key Parameters | Description | Python Method |
|----------|--------|------|----------------|-------------|---------------|
| Color Presets | GET | `/canvases/:canvasId/color-presets` | canvasId (path) | Get color presets for canvas | - |
| Color Presets | PATCH | `/canvases/:canvasId/color-presets` | canvasId (path), presets (body) | Update color presets | - |

## Uploads Folder

| Resource | Method | Path | Key Parameters | Description | Python Method |
|----------|--------|------|----------------|-------------|---------------|
| Uploads Folder | POST | `/canvases/:id/uploads-folder` | id (path), json/data (multipart) | Upload a note | `upload_note(canvas_id, payload)` |
| Uploads Folder | POST | `/canvases/:id/uploads-folder` | id (path), json/data (multipart) | Upload a file asset | `upload_file(canvas_id, file_path, payload)` |

## User Management

| Resource | Method | Path | Key Parameters | Description | Python Method |
|----------|--------|------|----------------|-------------|---------------|
| Users | GET | `/users` | subscribe (query) | List all users | `list_users()` |
| Users | GET | `/users/:id` | id (path), subscribe (query) | Get a single user | `get_user(user_id)` |
| Users | POST | `/users` | email, name, password (body) | Create a user (admin) | `create_user(payload)` |
| Users | DELETE | `/users/:id` | id (path) | Delete a user (admin) | `delete_user(user_id)` |
| Users | PATCH | `/users/:id` | id (path), user data (body) | Update user profile | `update_user(user_id, payload)` |
| Users | POST | `/users/register` | email, name, password (body) | Register new user | `register_user(payload)` |
| Users | POST | `/users/:id/approve` | id (path) | Approve user (admin) | `approve_user(user_id)` |
| Users | POST | `/users/confirm-email` | token (body) | Confirm email address | `confirm_email(token)` |
| Users | POST | `/users/:id/password` | id (path), current/new password (body) | Change password | `change_password(user_id, current_password, new_password)` |
| Users | POST | `/users/password/create-reset-token` | email (body) | Request password reset | `request_password_reset(email)` |
| Users | GET | `/users/password/validate-reset-token` | token (query) | Validate reset token | `validate_reset_token(token)` |
| Users | POST | `/users/password/reset` | token, password (body) | Reset password | `reset_password(token, new_password)` |
| Users | POST | `/users/login` | email/password or token (body) | Login user | `login(email, password, token)` |
| Users | POST | `/users/logout` | token (body) | Logout user | `logout(token)` |
| Users | POST | `/users/:id/block` | id (path) | Block user | `block_user(user_id)` |
| Users | POST | `/users/:id/unblock` | id (path) | Unblock user (admin) | `unblock_user(user_id)` |
| Users | POST | `/users/login/saml` | - | SAML login | - |

## Access Tokens

| Resource | Method | Path | Key Parameters | Description | Python Method |
|----------|--------|------|----------------|-------------|---------------|
| Access Tokens | GET | `/users/:id/access-tokens` | id (path) | List user access tokens | `list_tokens(user_id)` |
| Access Tokens | GET | `/users/:id/access-tokens/:token-id` | id, token-id (path) | Get token info | `get_token(user_id, token_id)` |
| Access Tokens | POST | `/users/:id/access-tokens` | id (path), description (body) | Create access token | `create_token(user_id, description)` |
| Access Tokens | PATCH | `/users/:id/access-tokens/:token-id` | id, token-id (path), description (body) | Update token description | `update_token(user_id, token_id, description)` |
| Access Tokens | DELETE | `/users/:id/access-tokens/:token-id` | id, token-id (path) | Delete access token | `delete_token(user_id, token_id)` |

## Groups

| Resource | Method | Path | Key Parameters | Description | Python Method |
|----------|--------|------|----------------|-------------|---------------|
| Groups | GET | `/groups` | - | List all user groups | - |
| Groups | GET | `/groups/:id` | id (path) | Get a single group | - |
| Groups | POST | `/groups` | name, description (body) | Create a new group | - |
| Groups | DELETE | `/groups/:id` | id (path) | Delete a group | - |
| Groups | POST | `/groups/:group_id/members` | group_id (path), id (body) | Add user to group | - |
| Groups | GET | `/groups/:id/members` | id (path) | List group members | - |
| Groups | DELETE | `/groups/:group_id/members/:user_id` | group_id, user_id (path) | Remove user from group | - |

## Clients & Workspaces

| Resource | Method | Path | Key Parameters | Description | Python Method |
|----------|--------|------|----------------|-------------|---------------|
| Clients | GET | `/clients` | - | List all connected clients | `list_clients()` |
| Clients | GET | `/clients/:id` | id (path) | Get a single client | - |
| Workspaces | GET | `/clients/:client_id/workspaces` | client_id (path) | List client workspaces | `list_workspaces(client_id)` |
| Workspaces | GET | `/clients/:client_id/workspaces/:workspace_index` | client_id, workspace_index (path) | Get a single workspace | `get_workspace(client_id, workspace_index)` |
| Workspaces | PATCH | `/clients/:client_id/workspaces/:workspace_index` | client_id, workspace_index (path), params (body) | Update workspace | `update_workspace(client_id, workspace_index, payload)` |

## Video Inputs & Outputs

| Resource | Method | Path | Key Parameters | Description | Python Method |
|----------|--------|------|----------------|-------------|---------------|
| Video Inputs | GET | `/canvases/:id/video-inputs` | id (path) | List video input widgets | - |
| Video Inputs | POST | `/canvases/:id/video-inputs` | id (path), widget (body) | Create video input widget | - |
| Video Inputs | DELETE | `/canvases/:id/video-inputs/:input_id` | id, input_id (path) | Delete video input widget | - |
| Video Inputs | GET | `/clients/:client_id/video-inputs` | client_id (path) | List client video inputs | - |
| Video Outputs | GET | `/clients/:client_id/video-outputs` | client_id (path) | List client video outputs | - |
| Video Outputs | PATCH | `/clients/:client_id/video-outputs/:index` | client_id, index (path), source/suspended (body) | Set video output source | - |
| Video Outputs | PATCH | `/canvases/:id/video-outputs/:output_id` | id, output_id (path), name/resolution (body) | Update video output | - |

## License Management

| Resource | Method | Path | Key Parameters | Description | Python Method |
|----------|--------|------|----------------|-------------|---------------|
| License | GET | `/license` | - | Get license info | - |
| License | POST | `/license/activate` | key (body) | Activate license online | - |
| License | GET | `/license/request` | key (query) | Generate offline activation request | - |
| License | POST | `/license` | license (body) | Install offline license | - |

## Audit Log

| Resource | Method | Path | Key Parameters | Description | Python Method |
|----------|--------|------|----------------|-------------|---------------|
| Audit Log | GET | `/audit-log` | filters (query) | Get audit events (paginated) | - |
| Audit Log | GET | `/audit-log/export-csv` | filters (query) | Export audit log as CSV | - |

## Mipmaps & Assets

| Resource | Method | Path | Key Parameters | Description | Python Method |
|----------|--------|------|----------------|-------------|---------------|
| Mipmaps | GET | `/mipmaps/{publicHashHex}` | publicHashHex (path), canvas-id (header) | Get mipmap info | - |
| Mipmaps | GET | `/mipmaps/{publicHashHex}/{level}` | publicHashHex, level (path), canvas-id (header) | Get mipmap level image | - |
| Assets | GET | `/assets/{publicHashHex}` | publicHashHex (path), canvas-id (header) | Get asset file by hash | - |

## Annotations

| Resource | Method | Path | Key Parameters | Description | Python Method |
|----------|--------|------|----------------|-------------|---------------|
| Annotations | GET | `/canvases/:canvasId/widgets?annotations=1` | canvasId (path), annotations (query) | List widget annotations | - |
| Annotations | GET | `/canvases/:canvasId/widgets?annotations=1&subscribe=1` | canvasId (path), annotations, subscribe (query) | Subscribe to annotation changes | - |

## Subscription Methods

| Resource | Method | Path | Key Parameters | Description | Python Method |
|----------|--------|------|----------------|-------------|---------------|
| Subscribe | GET | Various endpoints | subscribe=true (query) | Subscribe to real-time updates | `subscribe(endpoint, response_model, params, callback)` |
| Subscribe Widgets | - | - | canvas_id | Subscribe to widget updates | `subscribe_widgets(canvas_id, callback)` |
| Subscribe Workspace | - | - | client_id, workspace_index | Subscribe to workspace updates | `subscribe_workspace(client_id, workspace_index, callback)` |
| Subscribe Note | - | - | canvas_id, note_id | Subscribe to note updates | `subscribe_note(canvas_id, note_id, callback)` |

## Utility Methods

| Resource | Method | Path | Key Parameters | Description | Python Method |
|----------|--------|------|----------------|-------------|---------------|
| Utility | - | - | admin_email | Find admin client | `find_admin_client(admin_email)` |
| Utility | - | - | client_id | Get client workspaces | `get_client_workspaces(client_id)` |

---

## Notes

- **Authentication**: All endpoints require a `Private-Token` header with a valid access token
- **Base URL**: All endpoints are prefixed with `/api/v1/`
- **Streaming**: Add `subscribe=true` query parameter to enable real-time updates
- **File Uploads**: Use multipart/form-data for file uploads (images, videos, PDFs)
- **Permissions**: Some endpoints require admin privileges
- **Error Handling**: All endpoints return appropriate HTTP status codes and error messages

## Python Client Usage

```python
from canvus_api import CanvusClient

async with CanvusClient("https://canvus.example.com", "your-api-token") as client:
    # List all canvases
    canvases = await client.list_canvases()
    
    # Create a new canvas
    canvas = await client.create_canvas({"name": "My Canvas", "folder_id": "folder-123"})
    
    # Add a note to the canvas
    note = await client.create_note(canvas.id, {"text": "Hello World", "position": {"x": 100, "y": 100}})
```

For detailed information about each endpoint, refer to the individual API documentation files in the `Docs/` directory. 