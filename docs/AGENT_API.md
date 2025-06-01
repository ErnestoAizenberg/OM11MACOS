# Agent Management API Documentation

## Overview
This API provides endpoints for managing and interacting with user agents, including command execution, history tracking, and agent lifecycle management. The API requires authenticated sessions via the `login_required` decorator.

---

## Base URL
`https://OM11MACOS.example.com/api`

---

## Authentication
- All endpoints require authentication via session cookie
- Invalid/expired sessions return `401 Unauthorized`

---

## Endpoints

### 1. Execute Command
**`POST /command`**  
Executes a command through the user's connected agent and logs results.

#### Request Body (JSON)
| Field       | Type   | Required | Description                     |
|-------------|--------|----------|---------------------------------|
| `command`   | string | ✅       | Command to execute              |

#### Responses
| Status Code | Response Body                                      | Description                     |
|-------------|---------------------------------------------------|---------------------------------|
| `200`       | `{"success": true, "output": "<command output>"}` | Command executed successfully   |
| `400`       | `{"success": false, "error": "Invalid data"}`     | Malformed request               |
| `400`       | `{"success": false, "error": "Connected browser..."}` | No active browser session    |
| `500`       | `{"success": false, "error": "Internal..."}`      | Server error                    |

**Example Request:**
```json
{
  "command": "ls -la"
}
```

**Example Response:**
```json
{
  "success": true,
  "output": "total 16\ndrwxr-xr-x  4 user  staff  128 Jan 1 12:34 .\ndrwxr-xr-x  5 user  staff  160 Jan 1 12:30 .."
}
```

---

### 2. Get Command History
**`GET /command/history`**  
Retrieves the user's command execution history.

#### Responses
| Status Code | Response Body                                      | Description                     |
|-------------|---------------------------------------------------|---------------------------------|
| `200`       | `{"success": true, "command_history": [...]}`     | History retrieved               |
| `500`       | `{"success": false, "error": "Internal..."}`      | Server error                    |

**Example Response:**
```json
{
  "success": true,
  "command_history": [
    {
      "timestamp": "2023-01-01T12:34:56Z",
      "command": "ls -la",
      "is_user": true
    },
    {
      "timestamp": "2023-01-01T12:34:57Z",
      "command": "total 16\ndrwxr-xr-x...",
      "is_user": false
    }
  ]
}
```

---

### 3. Start Agent
**`POST /agent/start`**  
Initializes a new agent instance for the user.

#### Responses
| Status Code | Response Body                                      | Description                     |
|-------------|---------------------------------------------------|---------------------------------|
| `200`       | `{"success": true, "pid": 12345}`                 | Agent started                   |
| `400`       | `{"success": false, "error": "Agent already..."}` | Agent already running           |
| `500`       | `{"success": false, "error": "Internal..."}`      | Server error                    |

**Example Response:**
```json
{
  "success": true,
  "pid": 12345
}
```

---

### 4. Stop Agent
**`POST /agent/stop`**  
Terminates the user's active agent.

#### Responses
| Status Code | Response Body                                      | Description                     |
|-------------|---------------------------------------------------|---------------------------------|
| `200`       | `{"success": true}`                               | Agent stopped                   |
| `400`       | `{"success": false, "error": "Agent not..."}`     | No active agent                 |
| `500`       | `{"success": false, "error": "Internal..."}`      | Server error                    |

---

### 5. Get Agent Status
**`GET /agent/status`**  
Checks the current status of the user's agent.

#### Responses
| Status Code | Response Body                                      | Description                     |
|-------------|---------------------------------------------------|---------------------------------|
| `200`       | `{"success": true, "status": "running", "pid": 12345}` | Agent status            |
| `500`       | `{"success": false, "error": "Internal..."}`      | Server error                    |

**Possible Status Values:**
- `"running"` - Active with PID
- `"stopped"` - Not running
- `"error"` - In error state

**Example Response:**
```json
{
  "success": true,
  "status": "running",
  "pid": 12345
}
```

---

## Additional Features

### Telegram Integration
- Successful command executions automatically send output to Telegram if connected
- Telegram notifications include command output chunks

### Error Handling
- All endpoints include comprehensive error logging
- User-facing errors are sanitized while detailed errors are logged

### Security
- All operations are user-scoped via session `user_id`
- Command history persists per user
- Agent processes are isolated per user

---

## Typical Workflow
1. **Check Status** → `GET /agent/status`
2. **Start Agent** → `POST /agent/start` (if not running)
3. **Execute Command** → `POST /command`
4. **Review History** → `GET /command/history`
5. **Stop Agent** → `POST /agent/stop` (when done)

---

## Rate Limits
- Default: 60 requests/minute per endpoint
- Adjustable via configuration

Note: This API is designed for authenticated, user-specific agent management with comprehensive logging and Telegram integration.