# Audit Log API

The Audit Log API provides access to the server audit events. You must authenticate as an administrator to use this endpoint.

---

## Get Audit Log

Gets the list of audit events that match filters. Output of this endpoint is paginated. The link to the next page of results is given in the response Link header. Events are sorted from newest to oldest.

```bash
GET /audit-log
```

| Attribute           | Type    | Required | Description                                   |
|---------------------|---------|----------|-----------------------------------------------|
| `created_after`     | string  | no       | Include only events created after given timestamp |
| `created_before`    | string  | no       | Include only events created before given timestamp |
| `target_type`       | string  | no       | Include only events for the given target type |
| `target_id`         | string  | no       | Include only events for the given target ID   |
| `author_id`         | string  | no       | Include only events for the given author ID   |
| `per_page`          | integer | no       | Number of results per page                    |
| `cursor`            | integer | no       | Current page offset (from Link header)        |

**Example cURL Request**:
```bash
curl -H "Private-Token: <access token>" https://canvus.example.com/api/v1/audit-log
```

## Export Audit Log as CSV

Exports the audit log as a CSV file. Accepts the same set of filters as the audit-log endpoint.

```bash
GET /audit-log/export-csv
```

| Attribute           | Type    | Required | Description                                   |
|---------------------|---------|----------|-----------------------------------------------|
| `created_after`     | string  | no       | Include only events created after given timestamp |
| `created_before`    | string  | no       | Include only events created before given timestamp |
| `target_type`       | string  | no       | Include only events for the given target type |
| `target_id`         | string  | no       | Include only events for the given target ID   |
| `author_id`         | string  | no       | Include only events for the given author ID   |

**Example cURL Request**:
```bash
curl -H "Private-Token: <access token>" https://canvus.example.com/api/v1/audit-log/export-csv
``` 