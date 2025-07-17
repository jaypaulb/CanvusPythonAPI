# Canvas Backgrounds API

## Get Canvas Background

Gets the background settings for a specified canvas.

```bash
GET /canvases/:id/background
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | ID of the canvas             |
| `subscribe` (query) | boolean | no       | See Streaming                |

**Example cURL Request**:
```bash
curl -H "Private-Token: <access token>" https://canvus.example.com/api/v1/canvases/<canvas_id>/background
```

**Example Response**:
```json
{
  "type": "haze",
  "haze": {
    "color1": "#e0e0e0",
    "color2": "#f0f0f0",
    "speed": 0.5,
    "scale": 1.0
  },
  "grid": {
    "visible": true,
    "color": "#cccccc"
  },
  "image": {
    "hash": "863b0937ee95",
    "fit": "fill"
  }
}
```

## Set Canvas Background

Sets the background settings for a specified canvas.

### Set to Solid Color

```bash
PATCH /canvases/:id/background
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | ID of the canvas             |
| `type` (body)       | string  | yes      | Background type (solid_color) |
| `background_color` (body) | string | no   | Background color (hex)       |
| `grid` (body)       | object  | no       | Grid settings                |

**Example PATCH Body**:
```json
{
  "type": "solid_color",
  "background_color": "#000000"
}
```

### Set to Haze

```bash
PATCH /canvases/:id/background
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | ID of the canvas             |
| `type` (body)       | string  | yes      | Background type (haze)       |
| `haze` (body)       | object  | yes      | Haze settings                |
| `grid` (body)       | object  | no       | Grid settings                |

**Example PATCH Body**:
```json
{
  "type": "haze",
  "haze": {
    "color1": "#e0e0e0",
    "color2": "#f0f0f0",
    "speed": 0.5,
    "scale": 1.0
  }
}
```

### Set to Image

To set the background to an image, you must upload the image file using a multipart POST request, similar to uploading an image widget.

```bash
POST /canvases/:id/background
```

- The request must be a multipart POST with a `data` part containing the image file and an optional `json` part for additional parameters (e.g., fit, grid).

**Example cURL Request**:
```bash
curl -X POST -H "Private-Token: <access token>" -F 'data=@background.jpg' -F 'json={"type":"image","fit":"fill"}' https://canvus.example.com/api/v1/canvases/<canvas_id>/background
```

---

**Note:** The background can be a solid color, image, or haze. Additional fields may be present depending on the type. When setting an image background, use a multipart POST to upload the image file. 