# Clients API

The Clients API operates on Canvus clients connected to the server.

> **Note:** Clients will not expose themselves for API access by default. This has to be enabled on each client explicitly.

---

## List Clients

Gets all clients connected to the server.

```bash
GET /clients
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `subscribe` (query) | boolean | no       | See Streaming                |

**Example cURL Request**:
```bash
curl -H "Private-Token: <access token>" https://canvus.example.com/api/v1/clients
```

**Example Response**:
```json
[
  {
    "access": "rw",
    "id": "e5cad8d4-7051-4051-97bc-13e41fd81ca7",
    "installation_name": "hp-z420",
    "state": "normal",
    "version": "3.0.0 [3837d3aa9]"
  }
]
```

## Single Client

Gets a single client.

```bash
GET /clients/:id
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `id` (path)         | uuid    | yes      | The ID of the client to get  |

**Example cURL Request**:
```bash
curl -H "Private-Token: <access token>" https://canvus.example.com/api/v1/clients/e5cad8d4-7051-4051-97bc-13e41fd81ca7
```

**Example Response**:
```json
{
  "access": "rw",
  "id": "e5cad8d4-7051-4051-97bc-13e41fd81ca7",
  "installation_name": "hp-z420",
  "state": "normal",
  "version": "3.0.0 [3837d3aa9]"
}
``` 