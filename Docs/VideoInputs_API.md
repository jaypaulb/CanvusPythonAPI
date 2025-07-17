# Video Inputs API

Video input functionality in Canvus is split into two distinct areas:

1. **Video Input Windows (Canvas Widgets):**
   - These are widgets on a canvas that display the video feed from a capture device.
   - You can create, list, and manage these windows via the `/canvases/:id/video-inputs` endpoint.

2. **Video Input Sources (Capture Devices):**
   - These are the physical or virtual video capture devices attached to a client device (e.g., USB webcams, capture cards).
   - You can enumerate available sources on a client using the `/clients/:client_id/video-inputs` endpoint.

To create a video input window, you must first discover the available sources on the relevant client device, then use the `source` value from the desired device when creating the window on a canvas.

The following sections describe each endpoint in detail.

## Part 1: Video Input Windows (Canvas Widgets)

> **Important:**
> This API endpoint allows you to manage (list, create, update, delete) video input widgets on a canvas. To create a new video input window, you must first enumerate available video input sources on the relevant client device using the `/clients/:client_id/video-inputs` endpoint. The `source` value from the client endpoint is then used in the creation payload for the video input window.

### List Video Input Windows

Gets all video input widgets currently active on the specified canvas.

```bash
GET /canvases/:id/video-inputs
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | ID of the canvas             |

**Example cURL Request**:
```bash
curl -H "Private-Token: <access token>" https://canvus.example.com/api/v1/canvases/<canvas_id>/video-inputs
```

**Example Response**:
```json
{
        "depth": 1217.39990234375,
        "host-id": "cf8b0fa0-6671-4f68-99df-8e38b010e84b",
        "id": "7a5f53f2-f6a5-4c9b-9c1a-022f0cee95cc",
        "location": {
            "x": 1228.38330078125,
            "y": 1416.197021484375
        },
        "parent_id": "762733ae-719a-448e-9c13-d1a92c9c3e2f",
        "pinned": false,
        "scale": 4.78245735168457,
        "size": {
            "height": 600,
            "width": 800
        },
        "source": "video=@device_pnp_\\\\?\\usb#vid_3277&pid_0031&mi_00#6&399d7860&0&0000#{65e8773d-8f56-11d0-a3b9-00a0c9223196}\\global",
        "state": "normal",
        "widget_type": "VideoInput"
    }
```

### Create Video Input Window

Creates a new video input widget. You must use a valid `source` value obtained from the `/clients/:client_id/video-inputs` endpoint. The `host-id` field represents the client ID of the device that has the input physically connected to it.

```bash
POST /canvases/:id/video-inputs
```

| Field       | Type    | Required | Description                                      |
|-------------|---------|----------|--------------------------------------------------|
| `source`    | string  | yes      | Device source string (from client endpoint)       |
| `host-id`   | string  | yes      | Client ID of the device with the input            |
| `location`  | object  | no       | {x, y} coordinates                               |
| `size`      | object  | no       | {width, height}                                  |
| `scale`     | number  | no       | Widget scale                                     |
| `pinned`    | bool    | no       | Whether the widget is pinned                     |
| `floating`  | bool    | no       | (TODO) Floating/not floating option              |
| `muted`     | bool    | no       | (TODO) Mute/unmute option                        |

**Example JSON Payload:**
```json
{
  "source": "video=@device_pnp_\\?\usb#vid_3277&pid_0031&mi_00#6&399d7860&0&0000#{65e8773d-8f56-11d0-a3b9-00a0c9223196}\\global",
  "host-id": "cf8b0fa0-6671-4f68-99df-8e38b010e84b",
  "location": { "x": 100, "y": 200 },
  "size": { "width": 800, "height": 600 },
  "scale": 1.0,
  "pinned": false
}
```

**Example cURL Request:**
```bash
curl -X POST -H "Private-Token: <access token>" -H "Content-Type: application/json" \
  -d '{
    "source": "video=@device_pnp_\\?\usb#vid_3277&pid_0031&mi_00#6&399d7860&0&0000#{65e8773d-8f56-11d0-a3b9-00a0c9223196}\\global",
    "host-id": "cf8b0fa0-6671-4f68-99df-8e38b010e84b",
    "location": { "x": 100, "y": 200 },
    "size": { "width": 800, "height": 600 },
    "scale": 1.0,
    "pinned": false
  }' \
  https://canvus.example.com/api/v1/canvases/<canvas_id>/video-inputs
```

---

### Delete Video Input Window

Deletes a video input widget from the canvas.

```bash
DELETE /canvases/:id/video-inputs/:input_id
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | ID of the canvas             |
| `input_id` (path)   | string  | yes      | ID of the video input widget |

**Example cURL Request:**
```bash
curl -X DELETE -H "Private-Token: <access token>" \
  https://canvus.example.com/api/v1/canvases/<canvas_id>/video-inputs/<input_id>
```

## Part 2: Video Input Sources (Capture Devices)

To enumerate available video input (capture) devices on a client, use the following endpoint:

```bash
GET /clients/:client_id/video-inputs
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `client_id` (path)  | uuid    | yes      | ID of the client device      |

**Example cURL Request**:
```bash
curl -H "Private-Token: <access token>" https://canvus.example.com/api/v1/clients/<client_id>/video-inputs
```

**Example Response**:
```json
[
  {
    "name": "video=OV13B10",
    "resolution": { "height": 0, "width": 0 },
    "source": "video=@device_pnp_\?display#int3480#4&5884d88&0&uid144512#{65e8773d-8f56-11d0-a3b9-00a0c9223196}\{38b3b36b-80a9-4dad-94a3-bf51efedb4de}"
  },
  {
    "name": "video=USB2.0 5M UVC WebCam",
    "resolution": { "height": 0, "width": 0 },
    "source": "video=@device_pnp_\?usb#vid_3277&pid_0031&mi_00#6&399d7860&0&0000#{65e8773d-8f56-11d0-a3b9-00a0c9223196}\global"
  }
]
```

### Field Descriptions
- `name`: Human-readable name of the capture device.
- `resolution`: Reported resolution (may be 0 if unknown).
- `source`: Device source string to use when creating a video input window.

**Usage:**
- Use this endpoint to enumerate available capture devices on a client.
- Use the `source` value from the desired device as the `source` when creating a video input window via the `/canvases/:id/video-inputs` endpoint.

---

**TODO:**
- Add mute/unmute support for video-inputs.
- Add floating/not floating option for video-input windows.
- Change `host-id` to `client_id` for consistency. 