# 🔗 URL Shortener API Documentation for Frontend Integration

## 📋 Base Information

**Base URL**: `http://127.0.0.1:8000` (Development) / `https://your-domain.com` (Production)  
**API Documentation**: `{BASE_URL}/docs` (Swagger UI)  
**Authentication**: Bearer Token (JWT)

---

## 🔐 Authentication APIs

### 1. User Registration
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "Password123"
}
```

**Response (201)**:
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "is_active": true,
    "created_at": "2025-08-04T10:30:00Z"
  }
}
```

### 2. User Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "Password123"
}
```

**Response (200)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 3. OAuth2 Token (For Swagger/API Tools)
```http
POST /auth/token
Content-Type: application/x-www-form-urlencoded

grant_type=password&username=user@example.com&password=Password123
```

### 4. Refresh Token
```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## 🔗 Link Management APIs

**Note**: All link management endpoints require `Authorization: Bearer {access_token}` header except link creation which can be anonymous.

### 1. Create Short Link
```http
POST /links/create
Content-Type: application/json
Authorization: Bearer {access_token} # Optional for anonymous links

{
  "url": "https://www.example.com/very-long-url",
  "alias": "my-custom-alias" // Optional
}
```

**Response (200)**:
```json
{
  "id": 1,
  "url": "https://www.example.com/very-long-url",
  "short_code": "abc123",
  "short_url": "http://127.0.0.1:8000/abc123",
  "user_id": 1,
  "click_count": 0,
  "unique_clicks": 0,
  "last_clicked": null,
  "created_at": "2025-08-04T10:30:00Z",
  "updated_at": "2025-08-04T10:30:00Z"
}
```

### 2. Get User's Links
```http
GET /links/my-links
Authorization: Bearer {access_token}
```

**Response (200)**:
```json
[
  {
    "id": 1,
    "url": "https://www.example.com",
    "short_code": "abc123",
    "short_url": "http://127.0.0.1:8000/abc123",
    "user_id": 1,
    "click_count": 42,
    "unique_clicks": 28,
    "last_clicked": "2025-08-04T15:30:00Z",
    "created_at": "2025-08-04T10:30:00Z",
    "updated_at": "2025-08-04T15:30:00Z"
  }
]
```

### 3. Update Link
```http
PUT /links/{link_id}
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "url": "https://www.new-url.com", // Optional
  "alias": "new-alias" // Optional
}
```

### 4. Delete Link
```http
DELETE /links/{link_id}
Authorization: Bearer {access_token}
```

**Response (200)**:
```json
{
  "message": "Link 'abc123' deleted successfully"
}
```

### 5. Bulk Delete Links
```http
DELETE /links/bulk-delete
Content-Type: application/json
Authorization: Bearer {access_token}

[1, 2, 3, 4] // Array of link IDs
```

### 6. Get Single Link Details
```http
GET /links/{link_id}
Authorization: Bearer {access_token}
```

---

## 📊 Analytics APIs

**Note**: All analytics endpoints require authentication.

### 1. Analytics Dashboard
```http
GET /analytics/dashboard?days=7
Authorization: Bearer {access_token}
```

**Response (200)**:
```json
{
  "user_id": 1,
  "period_days": 7,
  "total_links": 5,
  "total_clicks": 234,
  "total_unique_clicks": 156,
  "average_clicks_per_link": 46.8,
  "top_performing_links": [
    {
      "id": 1,
      "short_code": "abc123",
      "url": "https://example.com...",
      "total_clicks": 89,
      "unique_clicks": 67,
      "created_at": "2025-08-04T10:30:00Z"
    }
  ],
  "recent_activity": [
    {
      "link_short_code": "abc123",
      "clicked_at": "2025-08-04T15:30:00Z",
      "location": "New York, United States",
      "device": "Mobile",
      "browser": "Chrome"
    }
  ]
}
```

### 2. Link Analytics Overview
```http
GET /analytics/{link_id}/overview?days=30
Authorization: Bearer {access_token}
```

**Response (200)**:
```json
{
  "link_id": 1,
  "period_days": 30,
  "total_clicks": 150,
  "unique_clicks": 89,
  "click_through_rate": 59.33,
  "link_info": {
    "id": 1,
    "url": "https://example.com",
    "short_code": "abc123",
    "created_at": "2025-08-04T10:30:00Z",
    "total_clicks_lifetime": 150,
    "unique_clicks_lifetime": 89
  },
  "devices": {
    "types": {
      "Mobile": {"count": 95, "percentage": 63.3},
      "Desktop": {"count": 55, "percentage": 36.7}
    },
    "brands": {
      "Apple": {"count": 67, "percentage": 44.7},
      "Samsung": {"count": 23, "percentage": 15.3}
    }
  },
  "geography": {
    "countries": {
      "United States": {"count": 67, "percentage": 44.7},
      "India": {"count": 45, "percentage": 30.0}
    },
    "cities": {
      "New York, United States": {"count": 34, "percentage": 22.7}
    }
  },
  "browsers": {
    "browsers": {
      "Chrome": {"count": 89, "percentage": 59.3},
      "Safari": {"count": 34, "percentage": 22.7}
    },
    "operating_systems": {
      "iOS": {"count": 67, "percentage": 44.7},
      "Android": {"count": 45, "percentage": 30.0}
    }
  },
  "timeline": {
    "daily": {
      "2025-08-01": 12,
      "2025-08-02": 18,
      "2025-08-03": 25
    },
    "hourly": {
      "9": 5,
      "10": 8,
      "11": 12
    }
  }
}
```

### 3. Device Analytics
```http
GET /analytics/{link_id}/devices?days=30
Authorization: Bearer {access_token}
```

### 4. Geographic Analytics
```http
GET /analytics/{link_id}/geography?days=30
Authorization: Bearer {access_token}
```

### 5. Timeline Analytics
```http
GET /analytics/{link_id}/timeline?days=30&granularity=daily
Authorization: Bearer {access_token}
```

**Query Parameters**:
- `granularity`: `hourly`, `daily`, `weekly`

### 6. Raw Click Data
```http
GET /analytics/{link_id}/clicks?limit=100&offset=0
Authorization: Bearer {access_token}
```

### 7. Export Analytics
```http
GET /analytics/{link_id}/export?format=json&days=30
Authorization: Bearer {access_token}
```

**Query Parameters**:
- `format`: `json` or `csv`

---

## 👤 Profile Management APIs

### 1. Get User Profile
```http
GET /profile/me
Authorization: Bearer {access_token}
```

**Response (200)**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "provider": "local",
  "is_active": true,
  "created_at": "2025-08-04T10:30:00Z",
  "updated_at": "2025-08-04T10:30:00Z"
}
```

### 2. Update Profile
```http
PUT /profile/update
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "first_name": "John",
  "last_name": "Doe",
  "email": "newemail@example.com" // Optional
}
```

### 3. Change Password
```http
POST /profile/change-password
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "current_password": "OldPassword123",
  "new_password": "NewPassword123"
}
```

---

## 🌐 Public APIs (No Authentication Required)

### 1. Redirect Short URL
```http
GET /{short_code}
```

**Response**: `301 Redirect` to original URL

### 2. API Health Check
```http
GET /health
```

**Response (200)**:
```json
{
  "status": "healthy",
  "database": "connected",
  "environment": "development",
  "timestamp": 1722771000.123
}
```

### 3. API Information
```http
GET /
```

**Response (200)**:
```json
{
  "title": "URL Shortener API",
  "description": "A secure and fast API for shortening URLs...",
  "version": "1.0.0",
  "environment": "development",
  "message": "Welcome to URL Shortener API",
  "endpoints": {
    "create_link": "/links/create",
    "my_links": "/links/my-links",
    "redirect": "/{short_code}",
    "auth": "/auth/*",
    "profile": "/profile/*",
    "docs": "/docs",
    "health": "/health"
  }
}
```

---

## 🔑 Authentication Flow for Frontend

### 1. User Registration/Login Flow
```javascript
// 1. Register/Login
const loginResponse = await fetch('/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'Password123'
  })
});

const { access_token, refresh_token } = await loginResponse.json();

// 2. Store tokens (localStorage, sessionStorage, or cookies)
localStorage.setItem('access_token', access_token);
localStorage.setItem('refresh_token', refresh_token);

// 3. Use token in subsequent requests
const response = await fetch('/links/my-links', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
```

### 2. Token Refresh Flow
```javascript
const refreshToken = async () => {
  const refresh_token = localStorage.getItem('refresh_token');
  
  const response = await fetch('/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token })
  });
  
  if (response.ok) {
    const { access_token } = await response.json();
    localStorage.setItem('access_token', access_token);
    return access_token;
  } else {
    // Redirect to login
    window.location.href = '/login';
  }
};
```

---

## ⚠️ Error Responses

### Common Error Formats
```json
{
  "detail": "Error message description"
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

### Example Validation Error (422)
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 🎯 Frontend Implementation Examples

### React/JavaScript Examples

#### Creating a Short Link
```javascript
const createShortLink = async (url, alias = null) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('/links/create', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    },
    body: JSON.stringify({ url, alias })
  });
  
  return await response.json();
};
```

#### Getting Analytics Dashboard
```javascript
const getAnalyticsDashboard = async (days = 7) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`/analytics/dashboard?days=${days}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
};
```

#### Getting User's Links
```javascript
const getUserLinks = async () => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('/links/my-links', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
};
```

---

## 📱 Mobile App Integration

### React Native / Flutter Examples
Same API endpoints, use appropriate HTTP clients:
- React Native: `fetch()` or `axios`
- Flutter: `http` package or `dio`
- iOS: `URLSession`
- Android: `OkHttp` or `Retrofit`

---

## 🔧 Testing the APIs

### Using Swagger UI
1. Visit: `http://127.0.0.1:8000/docs`
2. Click "Authorize" button
3. Enter: `Bearer {your_access_token}`
4. Test all endpoints interactively

### Using Postman
Import the API collection from Swagger UI or manually create requests with proper authentication headers.

---

This comprehensive API documentation provides everything your frontend developer needs to integrate with your URL shortener system! 🚀
