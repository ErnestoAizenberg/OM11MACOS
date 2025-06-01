# Telegram Integration API Documentation

## Overview
This API provides endpoints for managing Telegram bot connections, including webhook setup, message sending, and connection status monitoring. The service acts as a bridge between your application and the Telegram Bot API.

---

## Base URL
`https://OM11MACOS.example.com/api/telegram`

---

## Authentication
- All endpoints require authenticated sessions via `user_id` in session cookies
- Invalid/expired sessions return `401 Unauthorized`

---

## Endpoints

### 1. Connect Telegram Bot
**`POST /connect`**  
Sets up a webhook for a Telegram bot and establishes connection.

#### Request Body (JSON)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `bot_token` | string | ✅ | Telegram bot token (from @BotFather) |
| `chat_id` | string | ✅ | Target chat ID for messages |

#### Responses
| Status Code | Response | Description |
|-------------|----------|-------------|
| `200` | `{"success": true, "message": "Webhook set successfully"}` | Connection established |
| `400` | `{"success": false, "error": "Bot token and chat ID are required"}` | Missing parameters |
| `500` | `{"success": false, "error": "Failed to set webhook"}` | Telegram API error |

**Example Request:**
```json
{
  "bot_token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
  "chat_id": "-1001234567890"
}
```

**Example Response:**
```json
{
  "success": true,
  "message": "Webhook set successfully"
}
```

---

### 2. Disconnect Telegram Bot
**`POST /disconnect`**  
Removes webhook and disconnects the Telegram bot.

#### Responses
| Status Code | Response | Description |
|-------------|----------|-------------|
| `200` | `{"success": true, "message": "Disconnected successfully"}` | Disconnection successful |
| `500` | `{"success": false, "error": "Failed to disconnect"}` | Disconnection failed |

---

### 3. Check Connection Status
**`GET /status`**  
Checks the current Telegram connection status.

#### Rate Limit: 20 requests/second

#### Responses
| Status Code | Response | Description |
|-------------|----------|-------------|
| `200` | `{"success": true, "status": "connected", ...}` | Connection status info |
| `401` | `{"error": "Unauthorized"}` | Invalid session |

**Example Response:**
```json
{
  "success": true,
  "status": "connected",
  "user_id": "user123",
  "last_activity": "2023-06-15T14:30:00Z"
}
```

---

## Client Methods

The `TelegramClient` class provides these core methods:

### `set_webhook(bot_token: str, user_id: str, chat_id: str) -> bool`
- Configures Telegram webhook URL
- Stores connection parameters
- Returns `True` on success

### `test_connection(bot_token: str, chat_id: str) -> bool`
- Verifies Telegram API accessibility
- Validates bot token and chat ID
- Returns `True` if connection test passes

### `send_message(message: str, user_uuid: str) -> bool`
- Sends message to configured Telegram chat
- Handles message formatting
- Returns `True` on successful delivery

### `disconnect(user_id: str) -> bool`
- Removes webhook configuration
- Clears connection settings
- Returns `True` on success

### `get_status(user_id: str) -> dict`
- Returns current connection status
- Includes last activity timestamp
- Returns detailed status dictionary

---

## Error Handling
The API provides comprehensive error logging:
- Connection errors are logged with service URL
- Failed requests include Telegram API responses
- User-facing errors are sanitized

---

## Security Considerations
1. **Bot Tokens**: Always handle securely, never expose in client-side code
2. **Rate Limiting**: Status endpoint limited to 20 requests/second
3. **Session Validation**: All endpoints validate `user_id` from session
4. **Error Messages**: Detailed errors logged internally, generic messages returned to clients

---

## Typical Workflow
1. **Connect** → `POST /connect` with bot credentials
2. **Send Messages** → Use client's `send_message()` method
3. **Monitor** → Check status with `GET /status`
4. **Disconnect** → `POST /disconnect` when done

For implementation details, see the `TelegramClient` class documentation.