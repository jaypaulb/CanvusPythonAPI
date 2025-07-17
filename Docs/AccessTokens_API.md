# Access Tokens API

Access Tokens API is used to manage personal access tokens for the API. Access tokens never expire unless revoked.

---

## List Tokens

Gets the access tokens of a user. Regular users can see only their own tokens, administrators can list access tokens of other users. The actual tokens are not returned.

```bash
GET /users/:id/access-tokens
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | integer | yes      | The ID of the user           |
| `subscribe` (query) | boolean | no       | See Streaming                |

**Example cURL Request**:
```bash
curl -H "Private-Token: <access token>" https://canvus.example.com/api/v1/users/1001/access-tokens
```

**Example Response**:
```json
[
  {
    "created_at": "2021-07-02T06:38:36.025",
    "description": "First token",
    "id": "JDJhJDA0JENKTWJDT0g1QVNYSkFQTXh3NlhNWi5CWjlqT05yR2h0cXJ1d1VQZW9sZWlsWkJneXRXbTRp"
  }
]
```

## Single Token

Gets info about a single access token.

```bash
GET /users/:id/access-tokens/:token-id
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | integer | yes      | The ID of the user           |
| `token-id` (path)   | string  | yes      | The ID of the token          |
| `subscribe` (query) | boolean | no       | See Streaming                |

**Example cURL Request**:
```bash
curl -H "Private-Token: <access token>" https://canvus.example.com/api/v1/users/1001/access-tokens/JDJhJDA0JENKTWJDT0g1QVNYSkFQTXh3NlhNWi5CWjlqT05yR2h0cXJ1d1VQZW9sZWlsWkJneXRXbTRp
```

**Example Response**:
```json
{
  "created_at": "2021-07-02T06:38:36.025",
  "description": "First token",
  "id": "JDJhJDA0JENKTWJDT0g1QVNYSkFQTXh3NlhNWi5CWjlqT05yR2h0cXJ1d1VQZW9sZWlsWkJneXRXbTRp"
}
```

## Create Token

Creates a new access token. The return value includes the plain text token. It is not possible to retrieve the plain text token afterwards.

```bash
POST /users/:id/access-tokens
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | integer | yes      | The ID of the user           |
| `description`       | string  | yes      | Description of the new token |

**Example cURL Request**:
```bash
curl -X POST -H "Private-Token: W1bns7ZYuN_u7fQTR3i6L0JopiRCGsbNjXRw7Z-yX0E" -d '{"description":"Second token"}' https://canvus.example.com/api/v1/users/1001/access-tokens
```

**Example Response**:
```json
{
  "created_at": "2021-07-02T09:38:36.193",
  "description": "Second token",
  "id": "JDJhJDA0JENKTWJDT0g1QVNYSkFQTXh3NlhNWi44SUR3aHJaY2E1UUVaOGZUeTRDejB2ZnQzWGovclQ2",
  "plain_token": "QbhGvPSeh0hLSgfJb120I6by4ao1J5RRd59XmNOQq2g"
}
```

## Change Token Description

Changes an access token description.

```bash
PATCH /users/:id/access-tokens/:token-id
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | integer | yes      | The ID of the user           |
| `token-id` (path)   | string  | yes      | The ID of the token          |
| `description`       | string  | yes      | New description              |

**Example cURL Request**:
```bash
curl -X PATCH -H "Private-Token: W1bns7ZYuN_u7fQTR3i6L0JopiRCGsbNjXRw7Z-yX0E" -d '{"description":"Updated description"}' https://canvus.example.com/api/v1/users/1001/access-tokens/JDJhJDA0JENKTWJDT0g1QVNYSkFQTXh3NlhNWi5CWjlqT05yR2h0cXJ1d1VQZW9sZWlsWkJneXRXbTRp
```

**Example Response**:
```json
{
  "created_at": "2021-07-02T06:38:36.025",
  "description": "Updated description",
  "id": "JDJhJDA0JENKTWJDT0g1QVNYSkFQTXh3NlhNWi5CWjlqT05yR2h0cXJ1d1VQZW9sZWlsWkJneXRXbTRp"
}
```

## Delete Token

Deletes an access token. The token is revoked and can not be used anymore.

```bash
DELETE /users/:id/access-tokens/:token-id
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | integer | yes      | The ID of the user           |
| `token-id` (path)   | string  | yes      | The ID of the token          |

**Example cURL Request**:
```bash
curl -X DELETE -H "Private-Token: W1bns7ZYuN_u7fQTR3i6L0JopiRCGsbNjXRw7Z-yX0E" https://canvus.example.com/api/v1/users/1001/access-tokens/JDJhJDA0JENKTWJDT0g1QVNYSkFQTXh3NlhNWi5CWjlqT05yR2h0cXJ1d1VQZW9sZWlsWkJneXRXbTRp
``` 