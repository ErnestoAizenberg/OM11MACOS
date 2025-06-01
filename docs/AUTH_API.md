# Authentication API Documentation  

## **Overview**  
This API provides endpoints for **user authentication**, including:  
✅ Email/password login  
✅ User registration with email verification  
✅ Session-based authentication  
✅ Account verification  

---

## **Base URL**  
`https://OM11MACOS.example.com/api`  

---

## **Endpoints**  

### **1. User Login**  
**`POST /login`**  
Authenticates a user and creates a session.  

#### **Request Body (JSON)**  
| Field      | Type   | Required | Description          |  
|------------|--------|----------|----------------------|  
| `email`    | string | ✅       | User's email         |  
| `password` | string | ✅       | User's password      |  

#### **Responses**  
| Status Code | Response Body                                  | Description                     |  
|-------------|-----------------------------------------------|---------------------------------|  
| `200`       | `{"message": "Login successful", "user": {...}}` | Success                         |  
| `400`       | `{"message": "Email and password are required"}` | Missing fields                 |  
| `401`       | `{"message": "Invalid credentials"}`           | Wrong email/password            |  
| `401`       | `{"message": "User is not verified"}`          | Email not verified              |  
| `500`       | `{"message": "Server error"}`                  | Internal error                  |  

**Example Request:**  
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Example Response:**  
```json
{
  "message": "Login successful",
  "user": {
    "id": 123,
    "name": "John Doe",
    "email": "user@example.com"
  }
}
```

---

### **2. User Registration**  
**`POST /signup`**  
Creates a new user account and sends a verification email.  

#### **Request Body (JSON)**  
| Field      | Type   | Required | Description          |  
|------------|--------|----------|----------------------|  
| `name`     | string | ✅       | User's name          |  
| `email`    | string | ✅       | User's email         |  
| `password` | string | ✅       | User's password      |  

#### **Responses**  
| Status Code | Response Body                                      | Description                     |  
|-------------|---------------------------------------------------|---------------------------------|  
| `201`       | `{"message": "Account created", "user": {...}}`    | Success                         |  
| `400`       | `{"message": "Name, email and password required"}` | Missing fields                 |  
| `400`       | `{"message": "Email already in use"}`             | Duplicate email                |  
| `500`       | `{"message": "Server error"}`                     | Internal error                  |  

**Example Request:**  
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "securepassword123"
}
```

**Example Response:**  
```json
{
  "message": "Account created successfully",
  "user": {
    "id": 124,
    "name": "Jane Doe",
    "email": "jane@example.com"
  }
}
```

---

### **3. Email Verification**  
**`GET /verify/<token>`**  
Verifies a user's email address using a token sent via email.  

#### **URL Parameters**  
| Parameter | Type   | Required | Description          |  
|-----------|--------|----------|----------------------|  
| `token`   | string | ✅       | Verification token   |  

#### **Responses**  
| Status Code | Description                     |  
|-------------|---------------------------------|  
| `302`       | Redirects to `/` on success     |  
| `403`       | Invalid/expired token           |  

**Verification Email Content:**  
```text
Click to verify your email: 
https://yourdomain.com/verify/abc123token456xyz
```

---

### **4. Check Authentication Status**  
**`GET /check-auth`**  
Checks if the current session is authenticated.  

#### **Responses**  
| Status Code | Response Body                                  | Description                     |  
|-------------|-----------------------------------------------|---------------------------------|  
| `200`       | `{"authenticated": true, "user": {...}}`      | User is logged in               |  
| `200`       | `{"authenticated": false}`                    | No active session               |  

**Example Response (Authenticated):**  
```json
{
  "authenticated": true,
  "user": {
    "id": 123,
    "name": "John Doe",
    "email": "user@example.com"
  }
}
```

---

## **Session Management**  
- Sessions last **31 days** (`session.permanent = True`).  
- Sessions are stored via `user_id` in encrypted cookies.  
- Use `session.clear()` to log out (commented in code but available).  

---

## **Security Notes**  
🔒 **Password Storage:**  
- Hashed with `werkzeug.security.generate_password_hash()` (PBKDF2-HMAC-SHA256).  

📧 **Email Verification:**  
- Tokens are **32-character URL-safe strings** (`secrets.token_urlsafe(32)`).  
- Tokens are **single-use** and cleared after verification.  

---

## **Error Handling**  
| Status Code | Scenario                          | Recommended Action              |  
|-------------|-----------------------------------|---------------------------------|  
| `4xx`       | Client-side errors (invalid data) | Check request format           |  
| `5xx`       | Server errors                     | Retry or contact support       |  

---

## **Example Workflow**  
1. **Sign Up** → `POST /signup`  
2. **Check Email** → Click verification link  
3. **Log In** → `POST /login`  
4. **Check Status** → `GET /check-auth`  

---

🚀 **Pro Tip:**  
For production, add:  
- Rate limiting (`flask-limiter`)  
- CSRF protection (`flask-wtf`)  
- HTTPS enforcement