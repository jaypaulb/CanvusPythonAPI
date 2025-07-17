# Canvases API

The Canvases API operates on canvases on the server.

---

## Shared Links

Canvus 3.1 introduced shared links. If enabled, this feature allows unauthenticated access to a canvas without providing an access token for API requests.

The shared links have a defined format:
{serverAddress}/open/{canvasId}

https://example.com/open/0cb6639f-042b-42a3-9e97-74818d2fb09d

canvus+ssl://ise2025.canvusmultisite.com/cedff5c2-d6ae-4d71-ae13-d9d8b5fb4f6f


If a canvas has `link_permission` attribute equal to `edit` or `view`, the `Private-Token` header in the API requests may be omitted. In this case, the regular permission checks are ignored and access to the canvas is granted as Guest user with `edit` or `view` permission correspondingly. If the Guest user is blocked on the server, this unauthenticated access will not be available.

A valid `Private-Token` may be given as usual when accessing a canvas with a shared link. In this case the user associated with the token is used to access the canvas, but the effective permission granted is at least as allowed by the `link_permission` attribute.

You can find out or modify the `link_permission` value using the `/permissions` endpoint.

---

## List Canvases

Gets a list of all canvases.

```bash
GET /canvases
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `subscribe` (query) | boolean | no       | See Streaming                |

**Example cURL Request**:
```bash
curl -H "Private-Token: <access token>" https://canvus.example.com/api/v1/canvases
```

**Example Response**:
```json
[
  {
    "access": "owner",
    "asset_size": 0,
    "created_at": "2021-10-28T12:27:39.426Z",
    "folder_id": "1034",
    "id": "020b063d-0086-49a5-8dd0-965b8e117216",
    "in_trash": false,
    "mode": "normal",
    "modified_at": "2021-10-28T12:27:39.426Z",
    "name": "New canvas",
    "preview_hash": "",
    "state": "normal"
  }
]
```

## Single Canvas

Gets a single canvas.

```bash
GET /canvases/:id
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | The ID of the canvas to get  |
| `subscribe` (query) | boolean | no       | See Streaming                |

**Example cURL Request**:
```bash
curl -H "Private-Token: <access token>" https://canvus.example.com/api/v1/canvases/020b063d-0086-49a5-8dd0-965b8e117216
```

**Example Response**:
```json
{
  "access": "owner",
  "asset_size": 0,
  "created_at": "2021-10-28T12:27:39.426Z",
  "folder_id": "1034",
  "id": "020b063d-0086-49a5-8dd0-965b8e117216",
  "in_trash": false,
  "mode": "normal",
  "modified_at": "2021-10-28T12:27:39.426Z",
  "name": "New canvas",
  "preview_hash": "",
  "state": "normal"
}
```

## Get Canvas Preview

Downloads the preview of the canvas, if available.

```bash
GET /canvases/:id/preview
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | The ID of the canvas         |

**Example cURL Request**:
```bash
curl -H "Private-Token: <access token>" https://canvus.example.com/api/v1/canvases/020b063d-0086-49a5-8dd0-965b8e117216/preview
```

**Example Response**:
```json
{
  "msg": "Canvas 020b063d-0086-49a5-8dd0-965b8e117216 doesn't have preview"
}
```

## Create Canvas

Creates a canvas.

```bash
POST /canvases
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `name`              | string  | no       | Name of the canvas           |
| `folder_id`         | uuid    | no       | The ID of the parent folder  |

**Example cURL Request**:
```bash
curl -X POST -H "Private-Token: <access token>" https://canvus.example.com/api/v1/canvases
```

**Example Response**:
```json
{
  "access": "owner",
  "asset_size": 0,
  "created_at": "2021-10-28T12:27:39.656Z",
  "folder_id": "1034",
  "id": "70c54ca9-a31d-45d8-af84-bacc9b708caf",
  "in_trash": false,
  "mode": "normal",
  "modified_at": "2021-10-28T12:27:39.656Z",
  "name": "New canvas (2)",
  "preview_hash": "",
  "state": "normal"
}
```

## Change Canvas

Can be used to rename a canvas or change it from regular to demo and vice versa.

```bash
PATCH /canvases/:id
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | The ID of the canvas to update |
| `name`              | string  | no       | Name of the canvas           |
| `mode`              | string  | no       | Demo-state of the canvas     |

**Mode Values:**

| Value   | Description                  |
|---------|------------------------------|
| normal  | Canvas is not a demo canvas  |
| demo    | Canvas is a demo canvas      |

**Example cURL Request**:
```bash
curl -X PATCH -H "Private-Token: <access token>" -d '{"name":"Hello"}' https://canvus.example.com/api/v1/canvases/020b063d-0086-49a5-8dd0-965b8e117216
```

**Example Response**:
```json
{
  "access": "owner",
  "asset_size": 0,
  "created_at": "2021-10-28T12:27:39.426Z",
  "folder_id": "1034",
  "id": "020b063d-0086-49a5-8dd0-965b8e117216",
  "in_trash": false,
  "mode": "normal",
  "modified_at": "2021-10-28T12:27:39.426Z",
  "name": "Hello",
  "preview_hash": "",
  "state": "normal"
}
```

## Restore Demo Canvas

Restores the state of a demo canvas to the last saved state.

```bash
POST /canvases/:id/restore
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | The ID of the canvas         |

**Example cURL Request**:
```bash
curl -X POST -H "Private-Token: <access token>" https://canvus.example.com/api/v1/canvases/9c21f153-ac8b-4ad3-83c5-60c282ee9359/restore
```

## Save Demo State

Updates the saved demo canvas state with the current changes.

```bash
POST /canvases/:id/save
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | The ID of the canvas         |

**Example cURL Request**:
```bash
curl -X POST -H "Private-Token: <access token>" https://canvus.example.com/api/v1/canvases/9c21f153-ac8b-4ad3-83c5-60c282ee9359/save
```

## Move Canvas

Moves a canvas to another folder.

```bash
POST /canvases/:id/move
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | The ID of the canvas to move |
| `folder_id`         | uuid    | yes      | The ID of the destination folder |
| `conflicts`         | string  | no       | Conflict resolution strategy |

**Conflict Resolution Values:**

| Value    | Description                                                      |
|----------|------------------------------------------------------------------|
| skip     | Synonym for cancel (default)                                     |
| cancel   | Cancels the operation if a conflict would happen as a result     |
| replace  | Replaces the destination canvas with the source one if a conflict happens |

**Example cURL Request**:
```bash
curl -X POST -H "Private-Token: <access token>" -d '{"folder_id":"47c0e2cb-a299-4f3b-ac9a-810cc7c242d3","conflicts":"replace"}' https://canvus.example.com/api/v1/canvases/020b063d-0086-49a5-8dd0-965b8e117216/move
```

**Example Response**:
```json
{
  "access": "owner",
  "asset_size": 0,
  "created_at": "2021-10-28T12:27:39.426Z",
  "folder_id": "47c0e2cb-a299-4f3b-ac9a-810cc7c242d3",
  "id": "020b063d-0086-49a5-8dd0-965b8e117216",
  "in_trash": false,
  "mode": "normal",
  "modified_at": "2021-10-28T12:27:39.426Z",
  "name": "Hello",
  "preview_hash": "",
  "state": "normal"
}
```

## Copy Canvas

Copies a canvas to another folder.

```bash
POST /canvases/:id/copy
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | The ID of the canvas to copy |
| `folder_id`         | uuid    | yes      | The ID of the destination folder |
| `conflicts`         | string  | no       | Conflict resolution strategy |

**Conflict Resolution Values:**

| Value    | Description                                                      |
|----------|------------------------------------------------------------------|
| skip     | Synonym for cancel (default)                                     |
| cancel   | Cancels the operation if a conflict would happen as a result     |
| replace  | Replaces the destination canvas with the source one if a conflict happens |

**Example cURL Request**:
```bash
curl -X POST -H "Private-Token: <access token>" -d '{"folder_id":"47c0e2cb-a299-4f3b-ac9a-810cc7c242d3","conflicts":"replace"}' https://canvus.example.com/api/v1/canvases/020b063d-0086-49a5-8dd0-965b8e117216/copy
```

**Example Response**:
```json
{
  "access": "owner",
  "asset_size": 0,
  "created_at": "2021-10-28T12:27:39.426Z",
  "folder_id": "47c0e2cb-a299-4f3b-ac9a-810cc7c242d3",
  "id": "020b063d-0086-49a5-8dd0-965b8e117216",
  "in_trash": false,
  "mode": "normal",
  "modified_at": "2021-10-28T12:27:39.426Z",
  "name": "Hello",
  "preview_hash": "",
  "state": "normal"
}
```

Copying a canvas to the same folder duplicates a canvas.

## Trash Canvas

Trash a canvas by moving it to the trash folder. The `conflicts` parameter is ignored when moving to trash. You cannot move items to other users' trash folder.

```bash
POST /canvases/:id/move
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | The ID of the canvas to trash |
| `folder_id`         | uuid    | yes      | The ID of the trash folder   |

**Example cURL Request**:
```bash
curl -X POST -H "Private-Token: <access token>" -d '{"folder_id":"trash.1034"}' https://canvus.example.com/api/v1/canvases/020b063d-0086-49a5-8dd0-965b8e117216/move
```

**Example Response**:
```json
{
  "access": "owner",
  "asset_size": 0,
  "created_at": "2021-10-28T12:27:39.426Z",
  "folder_id": "trash.1034",
  "id": "020b063d-0086-49a5-8dd0-965b8e117216",
  "in_trash": true,
  "mode": "normal",
  "modified_at": "2021-10-28T12:27:39.426Z",
  "name": "Hello",
  "preview_hash": "",
  "state": "normal"
}
```

## Delete Canvas

Permanently deletes a canvas.

```bash
DELETE /canvases/:id
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | The ID of the canvas to delete |

**Example cURL Request**:
```bash
curl -X DELETE -H "Private-Token: <access token>" https://canvus.example.com/api/v1/canvases/020b063d-0086-49a5-8dd0-965b8e117216
```

## Get Permissions

Gets the permission overrides on a canvas.

```bash
GET /canvases/:id/permissions
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | The ID of the canvas         |
| `subscribe` (query) | boolean | no       | See Streaming                |

**Example cURL Request**:
```bash
curl -H "Private-Token: <access token>" https://canvus.example.com/api/v1/canvases/9c21f153-ac8b-4ad3-83c5-60c282ee9359/permissions
```

**Example Response**:
```json
{
  "editors_can_share": true,
  "groups": [],
  "link_permission": "none",
  "users": [
    {
      "id": 1034,
      "inherited": false,
      "permission": "owner"
    }
  ]
}
```

## Set Permissions

Sets permission overrides on a canvas.

```bash
POST /canvases/:id/permissions
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | The ID of the canvas         |
| `editors_can_share` | boolean | no       | If true, users with edit access can change permissions |
| `users`             | array   | no       | The list of users permissions |
| `groups`            | array   | no       | The list of groups permissions |
| `link_permission`   | string  | no       | Shared link permission for the canvas |

**Permission Object Attributes:**

| Attribute     | Type    | Required | Description                        |
|---------------|---------|----------|------------------------------------|
| `id`          | integer | yes      | The ID of the user or group        |
| `permission`  | string  | yes      | Permission string                  |

**Permission Values:**

| Value   | Description                                 |
|---------|---------------------------------------------|
| none    | The principal has no access to the resource |
| view    | The principal has read-only access          |
| edit    | The principal has edit access               |
| owner   | The principal owns the resource             |

**Link Permission Values:**

| Value   | Description                                 |
|---------|---------------------------------------------|
| none    | Canvas is not shared with link              |
| view    | Canvas is shared with a link in read-only   |
| edit    | Canvas is shared with a link in read-write  |

**Example cURL Request**:
```bash
curl -X POST -H "Private-Token: <access token>" -d '{"editors_can_share":false,"link_permission":"view","users":[{"id":100,"permission":"edit"}]}' https://canvus.example.com/api/v1/canvases/9c21f153-ac8b-4ad3-83c5-60c282ee9359/permissions
```

**Example Response**:
```json
{
  "editors_can_share": false,
  "groups": [],
  "link_permission": "view",
  "users": [
    {
      "id": 100,
      "inherited": false,
      "permission": "edit"
    },
    {
      "id": 1034,
      "inherited": false,
      "permission": "owner"
    }
  ]
}
``` 