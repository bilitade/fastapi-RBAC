# API Examples - Complete Guide

## 🎯 Quick Reference

### Public Endpoints (No Auth)
- `POST /api/v1/users/register` - Self-registration
- `POST /api/v1/auth/login` - Login

### User Endpoints (Auth Required)
- `GET /api/v1/users/me` - Get own profile
- `PATCH /api/v1/users/me` - Update own profile

### Admin Endpoints (Permission Required)
- `POST /api/v1/users/` - Create user with roles
- `GET /api/v1/users/` - List users
- `PATCH /api/v1/users/{id}` - Update user
- `PATCH /api/v1/users/{id}/approve` - Approve user
- `DELETE /api/v1/users/{id}` - Delete user

## 📝 Complete Examples

### 1. User Registration (Public)

**No authentication required!**

```bash
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123!"
  }'
```

**Response:**
```json
{
  "id": 5,
  "email": "newuser@example.com",
  "is_active": true,
  "is_approved": false,
  "roles": [
    {
      "id": 3,
      "name": "normal",
      "permissions": [
        {"id": 10, "name": "view_board"},
        {"id": 14, "name": "view_task"},
        {"id": 11, "name": "create_task"}
      ]
    }
  ]
}
```

### 2. User Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=newuser@example.com&password=SecurePass123!"
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### 3. Get Own Profile

```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "id": 5,
  "email": "newuser@example.com",
  "is_active": true,
  "is_approved": false,
  "roles": [...]
}
```

### 4. Update Own Profile (PATCH)

**Only update email:**
```bash
curl -X PATCH "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "updated@example.com"
  }'
```

**Only update password:**
```bash
curl -X PATCH "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "NewSecurePass123!"
  }'
```

**Update both:**
```bash
curl -X PATCH "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "updated@example.com",
    "password": "NewSecurePass123!"
  }'
```

### 5. Admin: Create User with Roles

```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "manager@example.com",
    "password": "SecurePass123!",
    "role_names": ["admin"]
  }'
```

**Response:**
```json
{
  "id": 6,
  "email": "manager@example.com",
  "is_active": true,
  "is_approved": true,
  "roles": [
    {
      "id": 2,
      "name": "admin",
      "permissions": [...]
    }
  ]
}
```

### 6. Admin: List All Users

```bash
curl -X GET "http://localhost:8000/api/v1/users/?skip=0&limit=10" \
  -H "Authorization: Bearer <admin_token>"
```

### 7. Admin: Update User (PATCH - Partial)

**Only approve user:**
```bash
curl -X PATCH "http://localhost:8000/api/v1/users/5" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "is_approved": true
  }'
```

**Only change roles:**
```bash
curl -X PATCH "http://localhost:8000/api/v1/users/5" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "role_names": ["admin"]
  }'
```

**Deactivate user:**
```bash
curl -X PATCH "http://localhost:8000/api/v1/users/5" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": false
  }'
```

**Update multiple fields:**
```bash
curl -X PATCH "http://localhost:8000/api/v1/users/5" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "is_approved": true,
    "role_names": ["admin"],
    "email": "promoted@example.com"
  }'
```

### 8. Admin: Quick Approve User

```bash
curl -X PATCH "http://localhost:8000/api/v1/users/5/approve" \
  -H "Authorization: Bearer <admin_token>"
```

### 9. Admin: Delete User

```bash
curl -X DELETE "http://localhost:8000/api/v1/users/5" \
  -H "Authorization: Bearer <admin_token>"
```

### 10. Refresh Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<your_refresh_token>"
  }'
```

### 11. Logout

```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<your_refresh_token>"
  }'
```

## 🎭 Role Management

### Create Role

```bash
curl -X POST "http://localhost:8000/api/v1/roles/" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "manager",
    "permission_names": ["view_user", "create_task", "edit_task"]
  }'
```

### Update Role (PATCH - Partial)

**Only change name:**
```bash
curl -X PATCH "http://localhost:8000/api/v1/roles/4" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "senior_manager"
  }'
```

**Only change permissions:**
```bash
curl -X PATCH "http://localhost:8000/api/v1/roles/4" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "permission_names": ["view_user", "edit_user", "create_task"]
  }'
```

### List Roles

```bash
curl -X GET "http://localhost:8000/api/v1/roles/" \
  -H "Authorization: Bearer <admin_token>"
```

### Delete Role

```bash
curl -X DELETE "http://localhost:8000/api/v1/roles/4" \
  -H "Authorization: Bearer <admin_token>"
```

## 🔐 Permission Management

### Create Permission

```bash
curl -X POST "http://localhost:8000/api/v1/permissions/" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "approve_document"
  }'
```

### List Permissions

```bash
curl -X GET "http://localhost:8000/api/v1/permissions/" \
  -H "Authorization: Bearer <admin_token>"
```

## 🔄 Common Workflows

### New User Workflow

```bash
# 1. User self-registers
POST /api/v1/users/register
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}

# 2. User logs in (can use system with basic role)
POST /api/v1/auth/login
username=john@example.com&password=SecurePass123!

# 3. User accesses their profile
GET /api/v1/users/me
Authorization: Bearer <token>

# 4. Admin reviews and approves
PATCH /api/v1/users/5/approve
Authorization: Bearer <admin_token>

# 5. Admin upgrades user role
PATCH /api/v1/users/5
{
  "role_names": ["premium"]
}
Authorization: Bearer <admin_token>
```

### User Profile Update Workflow

```bash
# 1. User wants to change email
PATCH /api/v1/users/me
{
  "email": "newemail@example.com"
}
Authorization: Bearer <token>

# 2. User wants to change password
PATCH /api/v1/users/me
{
  "password": "NewSecurePass123!"
}
Authorization: Bearer <token>

# 3. Re-login with new credentials
POST /api/v1/auth/login
username=newemail@example.com&password=NewSecurePass123!
```

### Admin User Management Workflow

```bash
# 1. List pending users
GET /api/v1/users/?skip=0&limit=100
Authorization: Bearer <admin_token>

# 2. Approve user
PATCH /api/v1/users/5/approve
Authorization: Bearer <admin_token>

# 3. Assign role
PATCH /api/v1/users/5
{
  "role_names": ["manager"]
}
Authorization: Bearer <admin_token>

# 4. If needed, deactivate user
PATCH /api/v1/users/5
{
  "is_active": false
}
Authorization: Bearer <admin_token>
```

## 💡 Tips

### PATCH vs PUT
- **PATCH**: Send only what changes ✅
- **PUT**: Send all fields ❌ (not used)

### Password Requirements
- Minimum 8 characters
- At least one digit
- At least one uppercase letter
- At least one lowercase letter

### Default Roles
- New registered users get "normal" role
- Admin-created users can have any role
- Roles can be changed anytime

### Approval Flow
- `is_approved=false`: User registered, pending review
- `is_approved=true`: User approved, full access
- Can be customized in code

## 🚨 Error Handling

### 400 - Bad Request
```json
{
  "detail": "User with this email already exists"
}
```

### 401 - Unauthorized
```json
{
  "detail": "Invalid authentication credentials"
}
```

### 403 - Forbidden
```json
{
  "detail": "Permission denied. Required: create_user"
}
```

### 404 - Not Found
```json
{
  "detail": "User not found"
}
```

---

**For interactive testing, use Swagger UI at: http://localhost:8000/docs** 🎉

