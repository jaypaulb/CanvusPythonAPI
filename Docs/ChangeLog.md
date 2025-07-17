# Changelog

## v1.3 proposed based on found undocumented api calls

- Added:
  - Annotations API - currently get only - appears to have been build with the intent to only be used internally for the WebClient.
  - Canvas Backgrounds API - fully working.
  - Color Presets API - gui elements for the notes are in CanvusClient - no gui for the ink or text color elements.
  - Connectors API - fully working.
  - Mipmaps API - fully working although again this looks to be for internal use on the WebClient.
  - Video Inputs API - full working.
  - Video Outputs API - only one function is missing - patching the source to a widget responds with "widgets unsupported", however if you manually set the output to a widget (ie turn output on from a widget) you can then patch the on/off setting without a problem so i suspect this is just a "check" forcing only workspace-# as a valid input for source.

## v1.2

- Added unauthenticated access for link-shared canvases and `link_permission` attribute to the `permissions` endpoint.
- Added `/uploads-folder` endpoint.
- Added `/send-test-email` endpoint.
- Added `title` parameter for Notes.
- Filter out the ID of the currently open canvas in the Client API if the user who makes the request doesn't have access to that canvas.
- Added `server_name` attribute to the `/server-config`.

## v1.1

- Removed `ini` file tokens, made authentication mandatory for most endpoints.
- Added `/login`, `login/saml` and `/logout` endpoints.
- Added users and groups management API.
- Added `/permissions` endpoints for canvases and folders.
- Added DELETE `/children` for folders.
- Added `mode` (demo or normal) attribute for canvases.
- Added `/save` and `/restore` endpoints for canvases.
- Added `/preview` for canvases.
- Added API tokens management API.
- Added license management API.
- Added audit log API.
- Added `/server-config` endpoint.
- Applied permissions model to the Client API.
- Added `/open-canvas` endpoint for workspaces.
- Added `user-email` and `server-id` attributes to the `/workspace`. 