# Video Outputs API

> **Important:**
> Video outputs are managed per client device, not per canvas. You must use the client ID of the device with the physical video output connection.

## List Video Outputs

Gets all video outputs for a specific client device.

```bash
GET /clients/:client_id/video-outputs
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `client_id` (path)  | uuid    | yes      | ID of the client device      |

**Example cURL Request**:
```bash
curl -H "Private-Token: <access token>" https://canvus.example.com/api/v1/clients/cf8b0fa0-6671-4f68-99df-8e38b010e84b/video-outputs
```

**Example Response**:
```json
[
  {
    "index": 0,
    "label": "Projector",
    "source": "workspace-0",
    "suspended": false
  }
]
```

### Field Descriptions
- `index`: The index of the video output channel on the client device.
- `label`: The label shown in Canvus menus.
- `source`: Can be either a workspace index (e.g., "workspace-0") or the ID of a VideoOutputAnchor widget.
- `suspended`: Boolean. `false` means output is active; `true` means output is suspended.

## Set Video Output Source / Suspend

To change the output or suspend it:

```bash
PATCH /clients/:client_id/video-outputs/:index
```

**Example PATCH Body**:
```json
{
  "suspended": true
}
```

### Source Options
- **Workspace Index:** Set `source` to "workspace-{index_number}" to output a workspace view.
- **VideoOutputAnchor Widget:** Set `source` to the ID of a VideoOutputAnchor widget (must be created in advance).

**Note:** Currently, due to a bug, it is not possible to change the source to a widget via the API. The workaround is to set the projection source in the UI, then enable/disable via API.

---

## VideoOutputAnchor Widgets

These widgets must be created in advance (currently not possible via API). Example widget from `/widgets`:
```json
    {
        "depth": 1217.2999267578125,
        "id": "cec81bf2-348e-431e-98df-b77fec1d1670",
        "location": {
            "x": 310.7367248535156,
            "y": 1982.11962890625
        },
        "parent_id": "762733ae-719a-448e-9c13-d1a92c9c3e2f",
        "pinned": false,
        "scale": 1.508918285369873,
        "size": {
            "height": 600,
            "width": 900
        },
        "state": "normal",
        "widget_type": "VideoOutputAnchor"
    }
```

## Update Video Output

Updates a video output.

```bash
PATCH /canvases/:id/video-outputs/:output_id
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | ID of the canvas             |
| `output_id` (path)  | string  | yes      | ID of the video output       |
| `name`              | string  | no       | Name of the video output     |
| `resolution`        | object  | no       | Output resolution            |

**Example cURL Request**:
```bash
curl -X PATCH -H "Private-Token: <access token>" -d '{"name":"HDMI Output 1"}' https://canvus.example.com/api/v1/canvases/78cfbcc8-aed9-4bbb-95ca-a0b9a5358d5a/video-outputs/output-1
```

**Example Response**:
```json
{
  "id": "output-1",
  "name": "HDMI Output 1",
  "resolution": { "width": 1920, "height": 1080 },
  "state": "active",
  "widget_type": "VideoOutput"
}
```
