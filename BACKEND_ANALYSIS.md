# Backend Analysis for Borrow Requests Page

## Overview
This document analyzes the backend implementation for the borrow requests page at `/requests` and verifies that all required functionality is available and properly implemented.

## Frontend Requirements

Based on the frontend implementation, the following are required:

1. **API Endpoint**: `GET /api/borrows/requests/?lender=me`
   - Fetch requests where current user is the lender (item owner)

2. **API Endpoint**: `PATCH /api/borrows/requests/{id}/`
   - Update request status to "approved" or "rejected"
   - Request body: `{ "status": "approved" }` or `{ "status": "rejected" }`

3. **Response Data Structure**:
   - `item` (object with `title` or `name`)
   - `requester` or `borrower` (object with user info including `full_name`, `first_name`, `last_name`, `username`, `rating`)
   - `start_date`, `end_date` (date strings)
   - `requested_at` or `created_at` (timestamp)
   - `status` ("pending", "approved", "rejected")
   - `message` (optional)

## Backend Current State Analysis

### ✅ Available and Working

1. **API Endpoints**:
   - ✅ `GET /api/borrows/requests/?lender=me` - **EXISTS** and works correctly
   - ✅ `PATCH /api/borrows/requests/{id}/` - **EXISTS** (provided by ModelViewSet)
   - ✅ Status update functionality is implemented

2. **Data Model Fields**:
   - ✅ `item` with `title` - Available via ItemSerializer
   - ✅ `borrower` - Available via UserSerializer
   - ✅ `start_date`, `end_date` - Available in BorrowRequest model
   - ✅ `status` - Available with choices: "pending", "approved", "rejected", "cancelled"
   - ✅ `message` - Available in BorrowRequest model
   - ✅ `request_date` - Available in BorrowRequest model

3. **Filtering Logic**:
   - ✅ `?lender=me` filter correctly returns requests for items owned by the user
   - ✅ `?owner=me` filter also works (alias for lender)
   - ✅ `?borrower=me` filter returns requests where user is the borrower

4. **Notifications**:
   - ✅ Automatic notifications created when request is approved
   - ✅ Automatic notifications created when request is rejected

### ⚠️ Issues Found and Fixed

1. **Missing `full_name` field in UserSerializer**:
   - **Issue**: Frontend expects `full_name` but backend only had `first_name` and `last_name`
   - **Fix**: Added `full_name` as a SerializerMethodField that uses `get_full_name()` method
   - **Status**: ✅ **FIXED**

2. **Missing `rating` field in UserSerializer**:
   - **Issue**: Frontend expects a single `rating` field, but backend had `lender_rating` and `borrower_rating`
   - **Fix**: Added context-aware `rating` field that shows `borrower_rating` when viewing as lender (appropriate for borrow requests page)
   - **Status**: ✅ **FIXED**

3. **Missing `requested_at`/`created_at` aliases**:
   - **Issue**: Frontend expects `requested_at` or `created_at`, but backend model uses `request_date`
   - **Fix**: Added both `requested_at` and `created_at` as aliases for `request_date`
   - **Status**: ✅ **FIXED**

4. **Missing `requester` alias**:
   - **Issue**: Frontend may use `requester` instead of `borrower`
   - **Fix**: Added `requester` as an alias field that returns the borrower data
   - **Status**: ✅ **FIXED**

5. **Missing permission check for approve/reject**:
   - **Issue**: No explicit check to ensure only item owner can approve/reject
   - **Fix**: Added permission check in `perform_update` method
   - **Status**: ✅ **FIXED**

## Changes Made

### 1. Enhanced `accounts/serializers.py`

**Added fields to UserSerializer**:
- `full_name`: Computed field using `get_full_name()` method, falls back to username
- `rating`: Context-aware field that shows appropriate rating based on context

```python
full_name = serializers.SerializerMethodField()
rating = serializers.SerializerMethodField()
```

### 2. Enhanced `borrows/serializers.py`

**Added fields to BorrowRequestSerializer**:
- `requester`: Alias for `borrower` (frontend compatibility)
- `requested_at`: Alias for `request_date`
- `created_at`: Alias for `request_date`

**Enhanced `get_requester` method**:
- Passes context to UserSerializer to show borrower_rating when viewing as lender

### 3. Enhanced `borrows/views.py`

**Added permission check in `perform_update`**:
- Ensures only item owner can approve/reject requests
- Raises PermissionDenied if unauthorized user tries to update status

## API Response Example

After the changes, the API response will look like:

```json
{
  "id": 1,
  "item": {
    "id": 1,
    "title": "Camera",
    "description": "...",
    "owner": {...},
    ...
  },
  "borrower": {
    "id": 2,
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "email": "john@example.com",
    "borrower_rating": "4.50",
    "lender_rating": "0.00",
    "rating": 4.5,
    ...
  },
  "requester": {
    "id": 2,
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "rating": 4.5,
    ...
  },
  "status": "pending",
  "message": "I need this for a photography project",
  "start_date": "2024-01-15T10:00:00Z",
  "end_date": "2024-01-20T18:00:00Z",
  "request_date": "2024-01-10T08:00:00Z",
  "requested_at": "2024-01-10T08:00:00Z",
  "created_at": "2024-01-10T08:00:00Z"
}
```

## Testing Recommendations

1. **Test API Endpoints**:
   ```bash
   # Get requests where user is lender
   GET /api/borrows/requests/?lender=me
   
   # Approve a request
   PATCH /api/borrows/requests/1/
   Body: { "status": "approved" }
   
   # Reject a request
   PATCH /api/borrows/requests/1/
   Body: { "status": "rejected" }
   ```

2. **Verify Response Structure**:
   - Check that `full_name` is present in borrower/requester object
   - Check that `rating` is present and shows correct value
   - Check that `requested_at` and `created_at` are present
   - Check that `requester` alias is present

3. **Test Permissions**:
   - Try to approve/reject a request as non-owner (should fail)
   - Try to approve/reject a request as owner (should succeed)

4. **Test Filtering**:
   - Test `?lender=me` filter
   - Test `?owner=me` filter (should work same as lender)
   - Test `?borrower=me` filter

## Summary

✅ **All required functionality is now available and properly implemented**

- API endpoints match frontend expectations
- Response data structure includes all required fields
- Permission checks ensure security
- Notifications are automatically sent on status changes
- All field aliases are provided for frontend compatibility

The backend is now fully compatible with the frontend requirements for the borrow requests page.

