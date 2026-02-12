# api

workflow - ワークフローAPIドキュメント

## Overview

This document provides API documentation for the api module.

---

# api

workflow - ワークフローAPIドキュメント

## 概要

このドキュメントは api モジュールのAPIドキュメントを提供します。

## Base URL

```
http://localhost:8000
```

## Authentication

All API requests require authentication using a Bearer token:

```
Authorization: Bearer <your-token>
```

## Endpoints

### Get List

**GET** `/api/api/`

Retrieve a list of items.

**Response:**
```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "per_page": 20
}
```

### Get Item

**GET** `/api/api/{id}`

Retrieve a specific item by ID.

**Parameters:**
- `id` (path): Item ID

**Response:**
```json
{
  "id": 1,
  "name": "item",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Create Item

**POST** `/api/api/`

Create a new item.

**Request Body:**
```json
{
  "name": "item-name"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "item-name",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Update Item

**PUT** `/api/api/{id}`

Update an existing item.

**Parameters:**
- `id` (path): Item ID

**Request Body:**
```json
{
  "name": "updated-name"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "updated-name",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Delete Item

**DELETE** `/api/api/{id}`

Delete an item.

**Parameters:**
- `id` (path): Item ID

**Response:**
```json
{
  "success": true
}
```

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Error message description",
    "details": {}
  }
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `INVALID_REQUEST` | Request validation failed |
| `NOT_FOUND` | Resource not found |
| `UNAUTHORIZED` | Authentication required |
| `FORBIDDEN` | Access denied |
| `INTERNAL_ERROR` | Server error |

## Rate Limiting

- Rate limit: 100 requests per minute
- Rate limit headers are included in all responses:
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

## Examples

### cURL

```bash
# Get list
curl -H "Authorization: Bearer <token>" \
     http://localhost:8000/api/api/

# Create item
curl -X POST \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"name": "item-name"}' \
     http://localhost:8000/api/api/
```

### Python

```python
import requests

headers = {"Authorization": "Bearer <token>"}

# Get list
response = requests.get(
    "http://localhost:8000/api/api/",
    headers=headers
)
data = response.json()

# Create item
response = requests.post(
    "http://localhost:8000/api/api/",
    headers=headers,
    json={"name": "item-name"}
)
item = response.json()
```

### JavaScript

```javascript
const headers = {
  'Authorization': 'Bearer <token>',
  'Content-Type': 'application/json'
};

// Get list
fetch('http://localhost:8000/api/api/', {headers})
  .then(res => res.json())
  .then(data => console.log(data));

// Create item
fetch('http://localhost:8000/api/api/', {
  method: 'POST',
  headers,
  body: JSON.stringify({name: 'item-name'})
})
  .then(res => res.json())
  .then(data => console.log(data));
```

## Versioning

API versioning is done via the URL path:
- `/api/v1/api/` - Version 1 (current)
- `/api/v2/api/` - Version 2 (future)

## Changelog

### v1.0.0 (2024-01-01)
- Initial release
