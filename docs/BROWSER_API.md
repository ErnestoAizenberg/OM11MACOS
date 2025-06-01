# Browser Management API Documentation

## Overview
This API provides endpoints for managing browser profiles and connections, including profile retrieval, browser session management, and status monitoring. The API integrates with a browser automation system through WebSocket connections.

---

## Base URL
`https://OM11MACOS.example.com/api/browser`

---

## Authentication
- All endpoints (except `/profiles`) require authentication via session cookie
- Invalid/expired sessions return `401 Unauthorized`

---

## Endpoints

### 1. Get Browser Profiles
**`GET /profiles`**  
Retrieves available browser profiles from a specified API endpoint.

#### Query Parameters
| Parameter | Type   | Required | Description                     |
|-----------|--------|----------|---------------------------------|
| `api_url` | string | ✅       | URL of the profiles API         |
| `type`    | string |          | Browser type filter (optional)  |

#### Responses
| Status Code | Response Body                                      | Description                     |
|-------------|---------------------------------------------------|---------------------------------|
| `200`       | `{"success": true, "profiles": [...]}`           | Profiles retrieved successfully |
| `400`       | `{"success": false, "error": "API URL..."}`      | Missing required parameter      |
| `500`       | `{"success": false, "error": "..."}`             | Server/network error            |

**Example Request:**
```
GET /api/browser/profiles?api_url=https://profiles.example.com&type=chrome
```

**Example Response:**
```json
{
  "success": true,
  "profiles": [
    {
      "id": "profile1",
      "name": "Work Profile",
      "type": "chrome",
      "created": "2023-01-01T00:00:00Z"
    }
  ]
}
```

---

### 2. Start Browser Profile
**`POST /start`**  
Initializes a browser session with the specified profile.

#### Request Body (JSON)
| Field       | Type   | Required | Description                     |
|-------------|--------|----------|---------------------------------|
| `api_url`   | string | ✅       | Profiles API URL                |
| `profile_id`| string | ✅       | Profile ID to launch            |
| `type`      | string | ✅       | Browser type                    |

#### Responses
| Status Code | Response Body                                      | Description                     |
|-------------|---------------------------------------------------|---------------------------------|
| `200`       | `{"success": true, "ws_url": "ws://..."}`        | Browser started successfully    |
| `400`       | `{"success": false, "error": "Missing..."}`      | Missing required fields         |
| `401`       | `{"success": false, "error": "User not..."}`     | Unauthenticated request         |
| `500`       | `{"success": false, "error": "..."}`             | Server/network error            |

**Example Request:**
```json
{
  "api_url": "https://profiles.example.com",
  "profile_id": "profile1",
  "type": "chrome"
}
```

**Example Response:**
```json
{
  "success": true,
  "ws_url": "ws://browser.example.com/session/abc123"
}
```

---

### 3. Check Browser Status
**`GET /status`**  
Checks the current browser connection status for the authenticated user.

#### Responses
| Status Code | Response Body                                      | Description                     |
|-------------|---------------------------------------------------|---------------------------------|
| `200`       | `{"connected": true, "active_profiles": 1}`      | Status retrieved                |
| `401`       | `{"success": false, "error": "User not..."}`     | Unauthenticated request         |
| `500`       | `{"success": false, "error": "..."}`             | Server error                    |

**Example Response:**
```json
{
  "connected": true,
  "active_profiles": 1
}
```

---

### 4. Disconnect All Browsers
**`POST /disconnect`**  
Terminates all active browser sessions for the authenticated user.

#### Responses
| Status Code | Response Body                                      | Description                     |
|-------------|---------------------------------------------------|---------------------------------|
| `200`       | `{"success": true, "message": "..."}`            | All sessions disconnected       |
| `401`       | `{"success": false, "error": "User not..."}`     | Unauthenticated request         |
| `500`       | `{"success": false, "error": "..."}`             | Server error                    |

**Example Response:**
```json
{
  "success": true,
  "message": "All profiles disconnected"
}
```

---

## Technical Details

### WebSocket Integration
- The `/start` endpoint initiates a WebSocket connection to the browser automation system
- WebSocket URLs follow the format: `ws://{agent_address}/session/{session_id}`

### Error Handling
- All endpoints include comprehensive error logging
- User-facing errors are sanitized while detailed errors are logged

### Session Management
- Browser sessions are tied to user accounts via `user_id`
- Multiple profiles can be active simultaneously per user

---

## Typical Workflow
1. **Get Profiles** → `GET /profiles`
2. **Start Browser** → `POST /start`
3. **Check Status** → `GET /status` (periodically)
4. **Disconnect** → `POST /disconnect` (when done)

---

## Rate Limits
- Default: 60 requests/minute per endpoint
- Adjustable via configuration

Note: This API is designed for secure, user-specific browser profile management with comprehensive logging and WebSocket integration.