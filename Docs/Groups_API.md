# Groups API

API for managing user groups. Read-only for regular users. You must authenticate as an administrator to have write access.

---

## List Groups

List all user groups.

```bash
GET /groups
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `subscribe` (query) | boolean | no       | See Streaming                |

**Example cURL Request**:
```bash
curl -H "Private-Token: <access token>" https://canvus.example.com/api/v1/groups
```

**Example Response**:
```json
[
  {
    "description": "All users on this server.",
    "id": 1,
    "name": "All Users"
  },
  {
    "description": "Group for developers",
    "id": 1000,
    "name": "R&D"
  }
]
```

## Single Group

Get a single user group.

```bash
GET /groups/:id
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | integer | yes      | ID of the group              |
| `subscribe` (query) | boolean | no       | See Streaming                |

**Example cURL Request**:
```bash
curl -H "Private-Token: <access token>" https://canvus.example.com/api/v1/groups/1000
```

**Example Response**:
```json
{
  "description": "Group for developers",
  "id": 1000,
  "name": "R&D"
}
```

## Create Group

Creates a new user group. You must authenticate as an administrator to use this endpoint.

```bash
POST /groups
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `name`              | string  | yes      | Name of the group. Must be unique. |
| `description`       | string  | no       | Description of the group     |

**Example cURL Request**:
```bash
curl -X POST -H "Private-Token: <access token>" -d '{"name":"My group","description":"Test group"}' https://canvus.example.com/api/v1/groups
```

**Example Response**:
```json
{
  "description": "Test group",
  "id": 1001,
  "name": "My group"
}
```

## Delete Group

Delete a user group. You must authenticate as an administrator to use this endpoint.

```bash
DELETE /groups/:id
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | integer | yes      | ID of the group              |

**Example cURL Request**:
```bash
curl -X DELETE -H "Private-Token: <access token>" https://canvus.example.com/api/v1/groups/1001
```

## Add User to Group

Adds a user to the group. You must authenticate as an administrator to use this endpoint.

```bash
POST /groups/:group_id/members
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `group_id` (path)   | integer | yes      | ID of the group              |
| `id` (body)         | integer | yes      | User ID                      |

**Example cURL Request**:
```bash
curl -X POST -H "Private-Token: <access token>" -d '{"id":100}' https://canvus.example.com/api/v1/groups/1000/members
```

## List Group Members

Lists users in the group.

```bash
GET /groups/:id/members
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | integer | yes      | ID of the group              |
| `subscribe` (query) | boolean | no       | See Streaming                |

**Example cURL Request**:
```bash
curl -H "Private-Token: <access token>" https://canvus.example.com/api/v1/groups/1000/members
```

**Example Response**:
```json
[
  {
    "admin": false,
    "approved": true,
    "blocked": false,
    "created_at": "2021-07-02T06:36:18.817Z",
    "email": "",
    "id": 100,
    "last_login": "2021-07-02T06:37:48.569Z",
    "name": "Guest",
    "state": "normal"
  }
]
```

## Remove User from Group

Removes a user from the group. You must authenticate as an administrator to use this endpoint.

```bash
DELETE /groups/:group_id/members/:user_id
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `group_id` (path)   | integer | yes      | ID of the group              |
| `user_id` (path)    | integer | yes      | User ID                      |

**Example cURL Request**:
```bash
curl -X DELETE -H "Private-Token: <access token>" https://canvus.example.com/api/v1/groups/1000/members/100
``` 