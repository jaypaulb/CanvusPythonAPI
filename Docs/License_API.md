# License API

The License API allows managing the Canvus server license. You must authenticate as an administrator to use this endpoint.

---

## Get License Info

Gets the current license status.

```bash
GET /license
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `subscribe` (query) | boolean | no       | See Streaming                |

**Example cURL Request**:
```bash
curl -H "Private-Token: <access token>" https://canvus.example.com/api/v1/license
```

**Example Response**:
```json
{
  "edition": "",
  "has_expired": false,
  "is_valid": true,
  "max_clients": -1,
  "type": "",
  "valid_until": "2021-08-17"
}
```

## Activate License

Performs online activation of a new license using an activation key.

```bash
POST /license/activate
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `key`               | string  | yes      | License key                  |

**Example cURL Request**:
```bash
curl -X POST -H "Private-Token: <access token>" -d '{"key":"AAAA-BBBB-CCCC-DDDD"}' https://canvus.example.com/api/v1/license/activate
```

## Offline Activation Request

Generates an offline activation request.

```bash
GET /license/request
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `key` (query)       | string  | yes      | License key                  |

**Example cURL Request**:
```bash
curl -H "Private-Token: <access token>" https://canvus.example.com/api/v1/license/request?key=AAAA-BBBB-CCCC-DDDD
```

## Install License

Installs a new license obtained from offline activation.

```bash
POST /license
```

| Attribute           | Type    | Required | Description                  |
|---------------------|---------|----------|------------------------------|
| `license`           | string  | yes      | License data                 |

**Example cURL Request**:
```bash
curl -X POST -H "Private-Token: <access token>" -d '{"license":"..."}' https://canvus.example.com/api/v1/license
``` 