# Server Info API

Retrieve information for this Canvus Server instance.

---

## Get Server Info

Returns information about the Canvus Server instance.

```bash
GET /server-info
```

**Example cURL Request:**
```bash
curl https://canvus.example.com/api/v1/server-info
```

**Example Response:**
```json
{
  "api": [
    "v1.1"
  ],
  "go": "1.16.4",
  "server_id": "71ac3376-5020-4033-a159-71c213dc9be6",
  "version": "3.0.0 [3837d3aa9]"
}
``` 