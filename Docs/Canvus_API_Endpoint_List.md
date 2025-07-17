# Canvus API Endpoint List

This document lists all Canvus API endpoints, grouped by resource, with HTTP method, path, and a short description. Every resource is fully enumerated—no placeholders or omissions.

---

## Canvases API

- `GET    /canvases` — List all canvases
- `GET    /canvases/:id` — Get a single canvas
- `POST   /canvases` — Create a canvas
- `PATCH  /canvases/:id` — Update (rename/mode) a canvas
- `DELETE /canvases/:id` — Delete a canvas
- `GET    /canvases/:id/preview` — Get canvas preview
- `POST   /canvases/:id/restore` — Restore demo canvas
- `POST   /canvases/:id/save` — Save demo state
- `POST   /canvases/:id/move` — Move/trash a canvas
- `POST   /canvases/:id/copy` — Copy a canvas
- `GET    /canvases/:id/permissions` — Get permissions
- `POST   /canvases/:id/permissions` — Set permissions

## Canvas Folders API

- `GET    /canvas-folders` — List all folders
- `GET    /canvas-folders/:id` — Get a single folder
- `POST   /canvas-folders` — Create a folder
- `PATCH  /canvas-folders/:id` — Rename a folder
- `POST   /canvas-folders/:id/move` — Move a folder to another folder or to trash
- `POST   /canvas-folders/:id/copy` — Copy a folder inside another folder
- `DELETE /canvas-folders/:id` — Delete a folder
- `DELETE /canvas-folders/:id/children` — Delete all children of a folder (not the folder itself)
- `GET    /canvas-folders/:id/permissions` — Get permission overrides on a folder
- `POST   /canvas-folders/:id/permissions` — Set permission overrides on a folder

## Notes API

- `GET    /canvases/:id/notes` — List all notes of the specified canvas
- `GET    /canvases/:id/notes/:note_id` — Get a single note
- `POST   /canvases/:id/notes` — Create a note
- `PATCH  /canvases/:id/notes/:note_id` — Update a note
- `DELETE /canvases/:id/notes/:note_id` — Delete a note

## Images API

- `GET    /canvases/:id/images` — List all images of the specified canvas
- `GET    /canvases/:id/images/:image_id` — Get a single image
- `POST   /canvases/:id/images` — Create an image (multipart POST)
- `PATCH  /canvases/:id/images/:image_id` — Update an image
- `DELETE /canvases/:id/images/:image_id` — Delete an image

## PDFs API

- `GET    /canvases/:id/pdfs` — List all PDFs of the specified canvas
- `GET    /canvases/:id/pdfs/:pdf_id` — Get a single PDF
- `GET    /canvases/:id/pdfs/:pdf_id/download` — Download a single PDF
- `POST   /canvases/:id/pdfs` — Create a PDF (multipart POST)
- `PATCH  /canvases/:id/pdfs/:pdf_id` — Update a PDF
- `DELETE /canvases/:id/pdfs/:pdf_id` — Delete a PDF

## Videos API

- `GET    /canvases/:id/videos` — List all videos of the specified canvas
- `GET    /canvases/:id/videos/:video_id` — Get a single video
- `GET    /canvases/:id/videos/:video_id/download` — Download a single video
- `POST   /canvases/:id/videos` — Create a video (multipart POST)
- `PATCH  /canvases/:id/videos/:video_id` — Update a video
- `DELETE /canvases/:id/videos/:video_id` — Delete a video

## Widgets API

- `GET    /canvases/:id/widgets` — List all widgets of the specified canvas
- `GET    /canvases/:id/widgets/:widget_id` — Get a single widget
- `POST   /canvases/:id/widgets` — Create a widget
- `PATCH  /canvases/:id/widgets/:widget_id` — Update a widget
- `DELETE /canvases/:id/widgets/:widget_id` — Delete a widget

## Anchors API

- `GET    /canvases/:id/anchors` — List all anchors of the specified canvas
- `GET    /canvases/:id/anchors/:anchor_id` — Get a single anchor

## Browsers API

- `GET    /canvases/:id/browsers` — List all browsers of the specified canvas
- `GET    /canvases/:id/browsers/:browser_id` — Get a single browser

## Connectors API

- `GET    /canvases/:id/connectors` — List all connectors for the specified canvas
- `GET    /canvases/:id/connectors/:connector_id` — Get a single connector
- `POST   /canvases/:id/connectors` — Create a connector
- `PATCH  /canvases/:id/connectors/:connector_id` — Update a connector
- `DELETE /canvases/:id/connectors/:connector_id` — Delete a connector

## Annotations API

- `GET    /canvases/:canvasId/widgets?annotations=1` — List all annotations for widgets on a canvas (as part of widgets)
- `GET    /canvases/:canvasId/widgets?annotations=1&subscribe=1` — Subscribe to annotation changes (streaming)

> Note: There are no dedicated POST/PATCH/DELETE endpoints for annotations; all annotation operations are performed as part of widget operations.

## Canvas Backgrounds API

- `GET    /canvases/:id/background` — Get canvas background
- `PATCH  /canvases/:id/background` — Set canvas background (solid color or haze)
- `POST   /canvases/:id/background` — Set canvas background to an image (multipart POST)

## Color Presets API

- `GET    /canvases/:canvasId/color-presets` — Get color presets for a canvas
- `PATCH  /canvases/:canvasId/color-presets` — Update color presets for a canvas

## Clients API

- `GET    /clients` — List all clients connected to the server
- `GET    /clients/:id` — Get a single client

## Groups API

- `GET    /groups` — List all user groups
- `GET    /groups/:id` — Get a single user group
- `POST   /groups` — Create a new user group
- `DELETE /groups/:id` — Delete a user group
- `POST   /groups/:group_id/members` — Add a user to a group
- `GET    /groups/:id/members` — List users in a group
- `DELETE /groups/:group_id/members/:user_id` — Remove a user from a group

## Audit Log API

- `GET    /audit-log` — Get the list of audit events (paginated)
- `GET    /audit-log/export-csv` — Export the audit log as CSV

## License API

- `GET    /license` — Get license info
- `POST   /license/activate` — Activate license online
- `GET    /license/request` — Generate offline activation request
- `POST   /license` — Install license from offline activation

## Mipmaps & Assets API

- `GET    /mipmaps/{publicHashHex}` — Get mipmap info for an asset
- `GET    /mipmaps/{publicHashHex}/{level}` — Get a specific mipmap level image (WebP)
- `GET    /assets/{publicHashHex}` — Get asset file by hash

> All require `canvas-id` and `Private-Token` headers.

## Video Inputs API

- `GET    /canvases/:id/video-inputs` — List all video input widgets on a canvas
- `POST   /canvases/:id/video-inputs` — Create a video input widget
- `DELETE /canvases/:id/video-inputs/:input_id` — Delete a video input widget
- `GET    /clients/:client_id/video-inputs` — List video input sources (capture devices) on a client

## Video Outputs API

- `GET    /clients/:client_id/video-outputs` — List all video outputs for a client device
- `PATCH  /clients/:client_id/video-outputs/:index` — Set video output source or suspend
- `PATCH  /canvases/:id/video-outputs/:output_id` — Update a video output (name, resolution)

## Uploads Folder API

- `POST   /canvases/:id/uploads-folder` — Upload a note (multipart POST)
- `POST   /canvases/:id/uploads-folder` — Upload a file asset (multipart POST)

## Workspaces API

- `GET    /clients/:client_id/workspaces` — List all workspaces of a client
- `GET    /clients/:client_id/workspaces/:workspace_index` — Get a single workspace
- `PATCH  /clients/:client_id/workspaces/:workspace_index` — Update workspace parameters

## Access Tokens API

- `GET    /users/:id/access-tokens` — List access tokens for a user
- `GET    /users/:id/access-tokens/:token-id` — Get info about a single access token
- `POST   /users/:id/access-tokens` — Create a new access token
- `PATCH  /users/:id/access-tokens/:token-id` — Change access token description
- `DELETE /users/:id/access-tokens/:token-id` — Delete (revoke) an access token

## Server Config API

- `GET    /server-config` — Get server settings
- `PATCH  /server-config` — Change server settings
- `POST   /server-config/send-test-email` — Send a test email

## Server Info API

- `GET    /server-info` — Get server info

---

For a tabular summary of all endpoints, see [Canvus_API_Endpoint_Table.md](Canvus_API_Endpoint_Table.md)
