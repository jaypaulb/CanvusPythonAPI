# Mipmaps & Assets API

## Overview
The Mipmaps & Assets API allows you to retrieve mipmap information and asset files by hash, typically for canvas previews and asset management. This API enables efficient, bandwidth-saving access to asset previews and is required for WebGL-based PDF/image viewing.

## Key Concepts
- **Mipmap Levels:** Level 0 is the original size; each higher level halves the dimensions. The maximum level is where both width and height are ≤128 pixels and ≥2 pixels.
- **File Format:** All mipmap images are returned as WebP, regardless of the original asset type or alpha channel.
- **Asset Types Supported:** Images and PDF files.
- **Caching:** All endpoints return `Cache-control: private, max-age=157680000, immutable` to enable long-term client caching.
- **Page Numbering:** For multi-page assets (e.g., PDFs), the first page is page zero.
- **Asset Hash Location:**
  - For `Image` widgets, use the `hash` field.
  - For `CanvasBackground` widgets, use the `image.hash` field.
- **Authentication:**
  - `canvas-id` is required as an HTTP header for all endpoints (not as a query parameter or in the path).
  - `Private-Token` is required as an HTTP header for authentication. (Note: As of current implementation, the API does not enforce 401 Unauthorized for missing/invalid tokens; it may return 200 with data instead.)

## Endpoints

### Get Mipmap Info
- **Endpoint:** `/api/v1/mipmaps/{publicHashHex}`
- **Method:** `GET`
- **Description:** Retrieve mipmap information for a given asset hash and page.
- **Headers:**
  - `canvas-id` (required): Canvas ID for access control.
  - `Private-Token` (required): API key for authentication.
- **Query Parameters:**
  - `page` (integer, optional): Page number (for multi-page assets; first page is 0).

#### Example Request
```http
GET /api/v1/mipmaps/abcdef123456?page=1
Header: canvas-id: 123
Header: Private-Token: <api-key>
```

#### Example Response
```json
{
  "resolution": { "width": 1024, "height": 768 },
  "max_level": 4,
  "pages": 1
}
```

### Get Mipmap Level
- **Endpoint:** `/api/v1/mipmaps/{publicHashHex}/{level}`
- **Method:** `GET`
- **Description:** Retrieve a specific mipmap level image (WebP format).
- **Headers:**
  - `canvas-id` (required): Canvas ID for access control.
  - `Private-Token` (required): API key for authentication.
- **Query Parameters:**
  - `page` (integer, optional): Page number (for multi-page assets; first page is 0).

#### Example Request
```http
GET /api/v1/mipmaps/abcdef123456/2?page=1
Header: canvas-id: 123
Header: Private-Token: <api-key>
```

#### Example Response
- Returns image data in WebP format for the requested mipmap level and page.

### Get Asset by Hash
- **Endpoint:** `/api/v1/assets/{publicHashHex}`
- **Method:** `GET`
- **Description:** Retrieve an asset file by its hash.
- **Headers:**
  - `canvas-id` (required): Canvas ID for access control.
  - `Private-Token` (required): API key for authentication.

#### Example Request
```http
GET /api/v1/assets/abcdef123456
Header: canvas-id: 123
Header: Private-Token: <api-key>
```

#### Example Response
- Returns the asset file (e.g., image, PDF, etc.) as binary data.

## Error Codes
- **400 Bad Request:** Mipmap level is outside the valid range.
- **401 Unauthorized:** Private token is missing. (Note: As of current implementation, the API may return 200 with data instead of 401.)
- **403 Forbidden:** User is blocked or otherwise unusable.
- **404 Not Found:** Asset not found or user has no access.
- **501 Not Implemented:** Asset type is not supported by the mipmap code.

## Notes
- All endpoints are designed for efficient WebGL rendering and optimal bandwidth usage.
- Mipmap levels are generated lazily and cached; there is no endpoint to list available levels (they are generated on demand).
- The original asset can always be downloaded using the `/assets` endpoint.
- The API paths are not canvas-relative; always use the global `/api/v1/mipmaps/` and `/api/v1/assets/` endpoints with the required headers. 