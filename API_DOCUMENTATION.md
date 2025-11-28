# ShareLib API Documentation

**Base URL:** `http://127.0.0.1:8000/api/`

**Authentication:** JWT Bearer Token (except for register/login)

---

## 🔐 Authentication Endpoints

### 1. Register User
**POST** `/api/auth/register/`

**No Authentication Required**

**Request Body:**
```json
{
  "username": "string (required, unique)",
  "email": "string (required, valid email)",
  "password": "string (required, min 8 chars)",
  "password2": "string (required, must match password)",
  "first_name": "string (optional)",
  "last_name": "string (optional)",
  "location": "string (optional)"
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "avatar": null,
    "location": "New York",
    "lender_rating": "0.00",
    "borrower_rating": "0.00"
  },
  "message": "User created successfully"
}
```

**Error Response (400):**
```json
{
  "username": ["This field is required."],
  "password": ["Password fields didn't match."]
}
```

---

### 2. Login
**POST** `/api/auth/login/`

**No Authentication Required**

**Request Body:**
```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Error Response (401):**
```json
{
  "detail": "No active account found with the given credentials"
}
```

---

### 3. Refresh Token
**POST** `/api/auth/refresh/`

**No Authentication Required**

**Request Body:**
```json
{
  "refresh": "string (required, refresh token)"
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 4. Get/Update User Profile
**GET/PUT** `/api/auth/register/profile/`

**Authentication Required**

**GET Response (200 OK):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "avatar": "/media/avatars/profile.jpg",
  "location": "New York",
  "lender_rating": "4.50",
  "borrower_rating": "4.75"
}
```

**PUT Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "newemail@example.com",
  "location": "Los Angeles",
  "avatar": null
}
```

**PUT Response (200 OK):** Same as GET response with updated fields

---

## 📦 Items Endpoints

### 5. List Items
**GET** `/api/items/`

**Authentication:** Optional (public can view, authenticated can filter)

**Query Parameters:**
- `category` - Filter by category ID
- `status` - Filter by status: `available`, `requested`, `borrowed`, `under_review`
- `condition` - Filter by condition: `new`, `good`, `used`, `damaged`
- `owner` - Filter by owner ID
- `search` - Search in title and description
- `ordering` - Order by: `created_at`, `-created_at`, `title`, `-title`
- `page` - Page number (pagination, 20 items per page)

**Response (200 OK):**
```json
{
  "count": 50,
  "next": "http://127.0.0.1:8000/api/items/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "owner": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "avatar": null,
        "location": "New York",
        "lender_rating": "4.50",
        "borrower_rating": "4.75"
      },
      "title": "Dell Laptop",
      "description": "Good condition laptop for work",
      "category": {
        "id": 1,
        "name": "Electronics",
        "description": "Electronic items",
        "created_at": "2025-11-28T10:00:00Z"
      },
      "condition": "good",
      "photos": "/media/items/laptop.jpg",
      "status": "available",
      "created_at": "2025-11-28T10:00:00Z",
      "updated_at": "2025-11-28T10:00:00Z"
    }
  ]
}
```

---

### 6. Create Item
**POST** `/api/items/`

**Authentication Required**

**Request Body (Form Data or JSON):**
```json
{
  "title": "string (required, max 255 chars)",
  "description": "string (required)",
  "category_id": 1,
  "condition": "new | good | used | damaged (default: good)",
  "photos": "file (optional, image file)",
  "status": "available | requested | borrowed | under_review (default: available)"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "owner": { /* user object */ },
  "title": "Dell Laptop",
  "description": "Good condition laptop",
  "category": { /* category object */ },
  "condition": "good",
  "photos": "/media/items/laptop.jpg",
  "status": "available",
  "created_at": "2025-11-28T10:00:00Z",
  "updated_at": "2025-11-28T10:00:00Z"
}
```

---

### 7. Get Item Details
**GET** `/api/items/{id}/`

**Authentication:** Optional

**Response (200 OK):** Same structure as item in list

---

### 8. Update Item
**PUT/PATCH** `/api/items/{id}/`

**Authentication Required** (only owner can update)

**Request Body:** Same as Create Item (all fields optional for PATCH)

**Response (200 OK):** Updated item object

---

### 9. Delete Item
**DELETE** `/api/items/{id}/`

**Authentication Required** (only owner can delete)

**Response (204 No Content)**

---

## 📚 Categories Endpoints

### 10. List Categories
**GET** `/api/items/categories/`

**Authentication:** Optional

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Electronics",
    "description": "Electronic items and gadgets",
    "created_at": "2025-11-28T10:00:00Z"
  }
]
```

---

### 11. Create Category
**POST** `/api/items/categories/`

**Authentication Required**

**Request Body:**
```json
{
  "name": "string (required, unique, max 100 chars)",
  "description": "string (optional)"
}
```

**Response (201 Created):** Category object

---

### 12. Get/Update/Delete Category
**GET/PUT/PATCH/DELETE** `/api/items/categories/{id}/`

**Authentication:** Required for write operations

---

## 📋 Borrow Requests Endpoints

### 13. List Borrow Requests
**GET** `/api/borrows/requests/`

**Authentication Required**

**Returns:** Requests where user is borrower OR owner of the item

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "item": { /* full item object */ },
    "item_id": 1,
    "borrower": { /* user object */ },
    "status": "pending | approved | rejected | cancelled",
    "request_date": "2025-11-28T10:00:00Z",
    "message": "I need this for 2 weeks"
  }
]
```

---

### 14. Create Borrow Request
**POST** `/api/borrows/requests/`

**Authentication Required**

**Request Body:**
```json
{
  "item_id": 1,
  "message": "string (optional)"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "item": { /* full item object */ },
  "borrower": { /* current user object */ },
  "status": "pending",
  "request_date": "2025-11-28T10:00:00Z",
  "message": "I need this for 2 weeks"
}
```

---

### 15. Get/Update Borrow Request
**GET/PUT/PATCH** `/api/borrows/requests/{id}/`

**Authentication Required** (borrower or item owner)

**PUT/PATCH Request Body:**
```json
{
  "status": "approved | rejected | cancelled"
}
```

**Note:** Only item owner can approve/reject. Borrower can cancel.

---

### 16. Delete Borrow Request
**DELETE** `/api/borrows/requests/{id}/`

**Authentication Required** (borrower or item owner)

---

## 📖 Borrow Records Endpoints

### 17. List Borrow Records
**GET** `/api/borrows/records/`

**Authentication Required**

**Returns:** Records where user is borrower OR owner

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "request": { /* full borrow request object */ },
    "start_date": "2025-11-28T10:00:00Z",
    "due_date": "2025-12-12T10:00:00Z",
    "return_date": null,
    "status": "borrowed | returned | late | overdue",
    "created_at": "2025-11-28T10:00:00Z"
  }
]
```

---

### 18. Create Borrow Record
**POST** `/api/borrows/records/`

**Authentication Required**

**Request Body:**
```json
{
  "request": 1,
  "start_date": "2025-11-28T10:00:00Z",
  "due_date": "2025-12-12T10:00:00Z",
  "status": "borrowed"
}
```

**Response (201 Created):** Borrow record object

---

### 19. Update Borrow Record (Mark as Returned)
**PUT/PATCH** `/api/borrows/records/{id}/`

**Authentication Required** (borrower or owner)

**Request Body:**
```json
{
  "return_date": "2025-12-10T10:00:00Z",
  "status": "returned"
}
```

---

## 🔔 Notifications Endpoints

### 20. List Notifications
**GET** `/api/notifications/`

**Authentication Required**

**Returns:** Current user's notifications

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user": 1,
    "type": "request | approved | rejected | due_soon | overdue | returned | rating",
    "message": "You have a new borrow request",
    "read": false,
    "created_at": "2025-11-28T10:00:00Z"
  }
]
```

---

### 21. Create Notification
**POST** `/api/notifications/`

**Authentication Required**

**Request Body:**
```json
{
  "type": "request | approved | rejected | due_soon | overdue | returned | rating",
  "message": "string (required)"
}
```

**Response (201 Created):** Notification object

---

### 22. Mark Notification as Read
**PATCH** `/api/notifications/{id}/`

**Authentication Required**

**Request Body:**
```json
{
  "read": true
}
```

---

## ⭐ Ratings Endpoints

### 23. List Ratings
**GET** `/api/ratings/`

**Authentication Required**

**Returns:** Ratings user gave OR received

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "from_user": "john_doe",
    "to_user": "jane_smith",
    "item": 1,
    "stars": 5,
    "message": "Great borrower, returned on time!",
    "created_at": "2025-11-28T10:00:00Z"
  }
]
```

---

### 24. Create Rating
**POST** `/api/ratings/`

**Authentication Required**

**Request Body:**
```json
{
  "to_user": 2,
  "item": 1,
  "stars": 5,
  "message": "string (optional)"
}
```

**Response (201 Created):** Rating object

**Note:** `from_user` is automatically set to current user

---

### 25. Get/Update/Delete Rating
**GET/PUT/PATCH/DELETE** `/api/ratings/{id}/`

**Authentication Required**

---

## 🔑 Authentication Header Format

For all authenticated endpoints, include JWT token in headers:

```
Authorization: Bearer <access_token>
```

**Example:**
```javascript
fetch('http://127.0.0.1:8000/api/items/', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGc...',
    'Content-Type': 'application/json'
  }
})
```

---

## 📝 Common Response Codes

- **200 OK** - Success
- **201 Created** - Resource created successfully
- **204 No Content** - Success (usually for DELETE)
- **400 Bad Request** - Validation errors
- **401 Unauthorized** - Authentication required or invalid token
- **403 Forbidden** - Permission denied
- **404 Not Found** - Resource not found
- **500 Internal Server Error** - Server error

---

## 🎯 Frontend Integration Tips

### 1. Token Management
```javascript
// Store tokens after login
localStorage.setItem('access_token', response.access);
localStorage.setItem('refresh_token', response.refresh);

// Use in API calls
const token = localStorage.getItem('access_token');
headers['Authorization'] = `Bearer ${token}`;

// Refresh token when expired
if (error.status === 401) {
  // Call /api/auth/refresh/ with refresh token
  // Update access token
}
```

### 2. File Upload (for item photos)
```javascript
const formData = new FormData();
formData.append('title', 'Item Title');
formData.append('description', 'Description');
formData.append('photos', fileInput.files[0]);
formData.append('category_id', 1);

fetch('/api/items/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
    // Don't set Content-Type for FormData
  },
  body: formData
});
```

### 3. Pagination
```javascript
// First page
fetch('/api/items/')

// Next page
fetch(response.next)

// Previous page
fetch(response.previous)
```

### 4. Filtering & Search
```javascript
// Search items
fetch('/api/items/?search=laptop')

// Filter by category
fetch('/api/items/?category=1&status=available')

// Multiple filters
fetch('/api/items/?category=1&status=available&condition=good&ordering=-created_at')
```

---

## 📚 API Documentation UI

Visit these URLs in your browser for interactive API documentation:

- **Swagger UI:** `http://127.0.0.1:8000/api/docs/`
- **ReDoc:** `http://127.0.0.1:8000/api/redoc/`
- **Schema (JSON):** `http://127.0.0.1:8000/api/schema/`

---

## 🚀 Quick Start Example

```javascript
// 1. Register
const registerResponse = await fetch('http://127.0.0.1:8000/api/auth/register/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'john_doe',
    email: 'john@example.com',
    password: 'securepass123',
    password2: 'securepass123'
  })
});

// 2. Login
const loginResponse = await fetch('http://127.0.0.1:8000/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'john_doe',
    password: 'securepass123'
  })
});

const { access, refresh } = await loginResponse.json();

// 3. Get Items
const itemsResponse = await fetch('http://127.0.0.1:8000/api/items/', {
  headers: {
    'Authorization': `Bearer ${access}`
  }
});

const items = await itemsResponse.json();
```

---

**Last Updated:** November 28, 2025

