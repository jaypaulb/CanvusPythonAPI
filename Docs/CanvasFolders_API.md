# Canvas Folders API

The Folders API operates on canvas folders on the server.

---

## List Folders

Gets a list of all folders.

```bash
GET /canvas-folders
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `subscribe` (query) | boolean | no       | See Streaming                |

**Example cURL Request**:
```bash
curl -H "Private-Token: <access token>" https://canvus.example.com/api/v1/canvas-folders
```

**Example Response**:
```json
[
  {
    "access": "edit",
    "folder_id": "",
    "id": "4f517d91-7448-4810-87f2-f6b25e8dc3cd",
    "in_trash": false,
    "name": "",
    "state": "normal"
  },
  {
    "access": "edit",
    "folder_id": "4f517d91-7448-4810-87f2-f6b25e8dc3cd",
    "id": "100",
    "in_trash": false,
    "name": "Guest",
    "state": "normal"
  }
]
```

## Single Folder

Gets a single folder.

```bash
GET /canvas-folders/:id
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | The ID of the folder to get  |
| `subscribe` (query) | boolean | no       | See Streaming                |

**Example cURL Request**:
```bash
curl -H "Private-Token: <access token>" https://canvus.example.com/api/v1/canvas-folders/b574c9f9-2717-4c95-b6dd-c48d146c28f3
```

**Example Response**:
```json
{
  "access": "owner",
  "folder_id": "1000",
  "id": "b574c9f9-2717-4c95-b6dd-c48d146c28f3",
  "in_trash": false,
  "name": "Alice",
  "state": "normal"
}
```

## Create Folder

Creates a folder.

```bash
POST /canvas-folders
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `name`              | string  | no       | Name of the folder           |
| `folder_id`         | uuid    | no       | The ID of the parent folder  |

**Example cURL Request**:
```bash
curl -X POST -H "Private-Token: <access token>" -d '{"name":"Notes","folder_id":"b574c9f9-2717-4c95-b6dd-c48d146c28f3"}' https://canvus.example.com/api/v1/canvas-folders
```

**Example Response**:
```json
{
  "access": "owner",
  "folder_id": "b574c9f9-2717-4c95-b6dd-c48d146c28f3",
  "id": "293bddf1-8e0e-4306-823e-19e5be9b2349",
  "in_trash": false,
  "name": "Notes",
  "state": "normal"
}
```

## Rename Folder

Renames a folder.

```bash
PATCH /canvas-folders/:id
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | The ID of the folder to rename |
| `name`              | string  | no       | Name of the canvas           |

**Example cURL Request**:
```bash
curl -X PATCH -H "Private-Token: <access token>" -d '{"name":"Carol"}' https://canvus.example.com/api/v1/canvas-folders/7d7ef61a-9def-4de5-96bf-c0193252378d
```

**Example Response**:
```json
{
  "access": "owner",
  "folder_id": "1000",
  "id": "7d7ef61a-9def-4de5-96bf-c0193252378d",
  "in_trash": false,
  "name": "Carol",
  "state": "normal"
}
```

## Move Folder

Moves a folder inside another folder.

```bash
POST /canvas-folders/:id/move
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | The ID of the folder to move |
| `folder_id`         | uuid    | yes      | The ID of the destination folder |
| `conflicts`         | string  | no       | Conflict resolution strategy |

**Example cURL Request**:
```bash
curl -X POST -H "Private-Token: <access token>" -d '{"folder_id":"7d7ef61a-9def-4de5-96bf-c0193252378d","conflicts":"replace"}' https://canvus.example.com/api/v1/canvas-folders/b574c9f9-2717-4c95-b6dd-c48d146c28f3/move
```

**Example Response**:
```json
{
  "access": "owner",
  "folder_id": "7d7ef61a-9def-4de5-96bf-c0193252378d",
  "id": "b574c9f9-2717-4c95-b6dd-c48d146c28f3",
  "in_trash": false,
  "name": "Alice",
  "state": "normal"
}
```

**Conflict Resolution Values:**

| Value    | Description                                                      |
|----------|------------------------------------------------------------------|
| skip     | Skips conflicting items (default)                                |
| cancel   | Cancels the whole operation if any conflict would happen         |
| replace  | Replaces the destination item with the source one if a conflict  |

## Copy Folder

Copies a folder inside another folder.

```bash
POST /canvas-folders/:id/copy
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | The ID of the folder to copy |
| `folder_id`         | uuid    | yes      | The ID of the destination folder |
| `conflicts`         | string  | no       | Conflict resolution strategy |

**Example cURL Request**:
```bash
curl -X POST -H "Private-Token: <access token>" -d '{"folder_id":"7d7ef61a-9def-4de5-96bf-c0193252378d","conflicts":"replace"}' https://canvus.example.com/api/v1/canvas-folders/b574c9f9-2717-4c95-b6dd-c48d146c28f3/copy
```

**Example Response**:
```json
{
  "access": "owner",
  "folder_id": "7d7ef61a-9def-4de5-96bf-c0193252378d",
  "id": "b574c9f9-2717-4c95-b6dd-c48d146c28f3",
  "in_trash": false,
  "name": "Alice",
  "state": "normal"
}
```

**Conflict Resolution Values:**

| Value    | Description                                                      |
|----------|------------------------------------------------------------------|
| skip     | Skips conflicting items (default)                                |
| cancel   | Cancels the whole operation if any conflict would happen         |
| replace  | Replaces the destination item with the source one if a conflict  |

## Trash Folder

Trash a folder by moving it to the trash folder. The `conflicts` parameter is ignored when moving to trash. You cannot move items to other users' trash folder.

```bash
POST /canvas-folders/:id/move
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | The ID of the folder to trash |
| `folder_id`         | uuid    | yes      | The ID of the trash folder   |

**Example cURL Request**:
```bash
curl -X POST -H "Private-Token: <access token>" -d '{"folder_id":"trash.1000"}' https://canvus.example.com/api/v1/canvas-folders/b574c9f9-2717-4c95-b6dd-c48d146c28f3/move
```

**Example Response**:
```json
{
  "access": "owner",
  "folder_id": "trash.1000",
  "id": "b574c9f9-2717-4c95-b6dd-c48d146c28f3",
  "in_trash": true,
  "name": "Alice",
  "state": "normal"
}
```

## Delete Folder

Permanently deletes a folder.

```bash
DELETE /canvas-folders/:id
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | The ID of the folder to delete |

**Example cURL Request**:
```bash
curl -X DELETE -H "Private-Token: <access token>" https://canvus.example.com/api/v1/canvas-folders/b574c9f9-2717-4c95-b6dd-c48d146c28f3
```

## Delete Folder Contents

Deletes all children of a folder, but not the folder itself.

```bash
DELETE /canvas-folders/:id/children
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | The ID of the folder         |

**Example cURL Request**:
```bash
curl -X DELETE -H "Private-Token: <access token>" https://canvus.example.com/api/v1/canvas-folders/trash.1000/children
```

## Get Permissions

Gets the permission overrides on a folder.

```bash
GET /canvas-folders/:id/permissions
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | The ID of the folder         |
| `subscribe` (query) | boolean | no       | See Streaming                |

**Example cURL Request**:
```bash
curl -H "Private-Token: <access token>" https://canvus.example.com/api/v1/canvas-folders/7d7ef61a-9def-4de5-96bf-c0193252378d/permissions
```

**Example Response**:
```json
{
  "editors_can_share": true,
  "groups": [],
  "users": [
    {
      "id": 1000,
      "inherited": false,
      "permission": "owner"
    }
  ]
}
```

## Set Permissions

Sets permission overrides on a folder.

```bash
POST /canvas-folders/:id/permissions
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | The ID of the folder         |
| `editors_can_share` | boolean | no       | If true, users with edit access can change permissions |
| `users`             | array   | no       | The list of users permissions |
| `groups`            | array   | no       | The list of groups permissions |

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

**Example cURL Request**:
```bash
curl -X POST -H "Private-Token: <access token>" -d '{"editors_can_share":false,"users":[{"id":100,"permission":"edit"}]}' https://canvus.example.com/api/v1/canvas-folders/7d7ef61a-9def-4de5-96bf-c0193252378d/permissions
```

**Example Response**:
```json
{
  "editors_can_share": false,
  "groups": [],
  "users": [
    {
      "id": 100,
      "inherited": false,
      "permission": "edit"
    },
    {
      "id": 1000,
      "inherited": false,
      "permission": "owner"
    }
  ]
}
``` 