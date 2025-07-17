> **Caveat:**
> 
> As of this writing, the `annotation` (inking) and `connector` color-presets are **not currently being correctly polled and shown in the Canvus UI**, even though the server returns a `200 OK` response and the correct data. This means updates to these presets via the API will not be reflected in the UI. The `note_background` color-presets **are** working as expected and changes are visible in the UI.
> 
> **Endpoint Note:**
> The color-presets API is canvas-specific and is accessed via `/api/v1/canvases/[canvasId]/color-presets`.
> Both `GET` and `PATCH` methods work as described below, but UI support is currently incomplete for some keys.

# Color Presets API

## Overview
The Color Presets API allows you to manage color presets for individual canvas elements. This API is canvas-specific.

## Endpoints

### Get Color Presets for a Canvas
- **Endpoint:** `/api/v1/canvases/[canvasId]/color-presets`
- **Method:** `GET`
- **Description:** Retrieve the color presets for the specified canvas.

#### Example Response
```json
{
  "annotation": ["#00338dff", "#005eb8ff", "#0091daff", "#470a68ff", "#6d2077ff", "#00a3a1ff"],
  "connector": ["#00338dff", "#005eb8ff", "#0091daff", "#470a68ff", "#6d2077ff", "#00a3a1ff"],
  "note_background": ["#00338dff", "#005eb8ff", "#0091daff", "#470a68ff", "#6d2077ff", "#00a3a1ff"],
  "note_text": []
}
```

### Update Color Presets for a Canvas
- **Endpoint:** `/api/v1/canvases/[canvasId]/color-presets`
- **Method:** `PATCH`
- **Description:** Update the color presets for the specified canvas.
- **Parameters (JSON body):**
  - Each key (`annotation`, `connector`, `note_background`, `note_text`) maps to an array of color strings.

#### Example Request
```http
PATCH /api/v1/canvases/cedff5c2-d6ae-4d71-ae13-d9d8b5fb4f6f/color-presets
Content-Type: application/json
{
  "note_background": ["#123456", "#654321"],
  "annotation": ["#abcdef"]
}
```

#### Example Response
```json
{
  "annotation": ["#abcdef"],
  "connector": ["#00338dff", "#005eb8ff", "#0091daff", "#470a68ff", "#6d2077ff", "#00a3a1ff"],
  "note_background": ["#123456", "#654321"],
  "note_text": []
}
```

---