# Upgrade Guide - New Features

## 🎉 What's New

Your RBAC system now includes:

### ✅ **PATCH Instead of PUT**
- Partial updates - only send fields you want to change
- More RESTful and user-friendly
- No need to send all data every time

### ✅ **Public User Registration**
- Users can register themselves without admin
- Auto-assigned default "normal" role
- Optional approval workflow

### ✅ **User Approval Workflow**
- `is_active`: Account active/inactive status
- `is_approved`: Admin approval status
- Flexible control over user access

### ✅ **Self-Service Profile Updates**
- Users can update their own email/password
- Separate from admin user management
- No permission required for own profile

### ✅ **Hassle-Free User Experience**
- Register → Login → Use system
- Admins can approve/assign roles later
- Standard RBAC ready for any project

## 📦 Migration Required

If you're upgrading from the old version:

### Option 1: Fresh Database (Recommended)
```bash
# Drop old database
dropdb rbac
createdb rbac

# Initialize with new schema
python -m app.scripts.init_db
```

### Option 2: Migrate Existing Database
```bash
# Run migration script
python -m app.scripts.migrate_add_user_status

# Or manually in psql:
psql rbac
ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE NOT NULL;
ALTER TABLE users ADD COLUMN is_approved BOOLEAN DEFAULT FALSE NOT NULL;
UPDATE users SET is_active = TRUE, is_approved = TRUE;
```

## 🚀 New API Endpoints

### Public Registration
```bash
# Register new user (NO AUTH REQUIRED)
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123!"
  }'
```

### Self-Service Profile Update
```bash
# Update own profile (PATCH - partial update)
curl -X PATCH "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newemail@example.com"
  }'
# Only email is updated, password stays the same
```

### Admin User Management
```bash
# Admin: Update user (PATCH - partial)
curl -X PATCH "http://localhost:8000/api/v1/users/1" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "role_names": ["admin"],
    "is_approved": true
  }'
# Only updates roles and approval status

# Admin: Approve user quickly
curl -X PATCH "http://localhost:8000/api/v1/users/1/approve" \
  -H "Authorization: Bearer <admin_token>"
```

## 🔄 Changed Endpoints

### Users

| Old | New | Change |
|-----|-----|--------|
| `PUT /users/{id}` | `PATCH /users/{id}` | Partial updates |
| N/A | `POST /users/register` | Public registration |
| N/A | `PATCH /users/me` | Self-service update |
| N/A | `PATCH /users/{id}/approve` | Quick approval |

### Roles

| Old | New | Change |
|-----|-----|--------|
| `PUT /roles/{id}` | `PATCH /roles/{id}` | Partial updates |

## 📋 User Registration Flow

### Standard Flow (Auto-Approved Projects)
1. User registers at `/users/register`
2. Gets "normal" role automatically
3. Can login and use system immediately
4. Admin can change roles later

### Approval Flow (Controlled Access)
1. User registers at `/users/register`
2. Gets "normal" role but `is_approved=false`
3. Tries to login → success (but limited access)
4. Admin reviews and approves user
5. User gets full access

### Admin-Created Users
1. Admin creates user at `/users/` (POST)
2. Can assign roles immediately
3. User is pre-approved (`is_approved=true`)
4. Can login right away

## 🎯 Use Cases

### Public Website/App
```python
# User self-registration enabled
# Auto-approve with basic role
# Upgrade to premium roles by admin
```

### Internal Company System
```python
# User self-registration enabled
# Admin approval required
# Assign department roles after approval
```

### Invitation-Only Platform
```python
# Disable public registration
# Admin creates all users
# Pre-assign roles on creation
```

## 🔧 Configuration Options

### Disable Public Registration
Remove or protect the `/users/register` endpoint:

```python
# In app/api/v1/endpoints/users.py
# Comment out or remove:
# @router.post("/register", ...)
```

### Auto-Approve New Users
```python
# In app/api/v1/endpoints/users.py - register_user function
new_user = User(
    email=user_data.email,
    password=hash_password(user_data.password),
    is_active=True,
    is_approved=True  # Change to True for auto-approval
)
```

### Require Approval to Login
```python
# In app/core/dependencies.py - get_current_user function
# Add after is_active check:
if not user.is_approved:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Account pending approval",
    )
```

## 📊 Database Schema Changes

### User Model (NEW Fields)
```python
class User(Base):
    id: int
    email: str
    password: str
    is_active: bool      # NEW: Account active/inactive
    is_approved: bool    # NEW: Admin approval status
    roles: List[Role]
    refresh_tokens: List[RefreshToken]
```

## ✅ Benefits for Future Projects

### 1. Versatile
- Works for public and private systems
- Easy to customize approval flow
- Standard RBAC pattern

### 2. User-Friendly
- Self-registration available
- Self-service profile updates
- Partial updates (PATCH) save time

### 3. Admin-Friendly
- Control user access with is_active
- Approve users with is_approved
- Assign/change roles anytime

### 4. Production-Ready
- Follows REST standards (PATCH for partial)
- Secure password validation
- Flexible permission system

## 🎓 Examples

### User Journey
```bash
# 1. User registers
POST /api/v1/users/register
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}

# 2. User logs in
POST /api/v1/auth/login
username=john@example.com&password=SecurePass123!

# 3. User updates profile
PATCH /api/v1/users/me
{
  "email": "john.doe@example.com"
}

# 4. Admin approves and upgrades
PATCH /api/v1/users/5
{
  "is_approved": true,
  "role_names": ["premium"]
}
```

### Admin Actions
```bash
# Quick approval
PATCH /api/v1/users/5/approve

# Deactivate user
PATCH /api/v1/users/5
{"is_active": false}

# Change user role
PATCH /api/v1/users/5
{"role_names": ["manager"]}

# Update email only
PATCH /api/v1/users/5
{"email": "new@example.com"}
```

## 🚨 Breaking Changes

### If you have existing code:

**Old way (PUT - full update):**
```python
# Had to send ALL fields
PUT /api/v1/users/1
{
  "email": "user@example.com",
  "password": "pass",
  "role_names": ["user"]
}
```

**New way (PATCH - partial update):**
```python
# Only send what changes
PATCH /api/v1/users/1
{
  "role_names": ["admin"]
}
```

## 📝 Summary

✅ **PATCH endpoints** for partial updates  
✅ **Public registration** for user sign-up  
✅ **Self-service updates** for user profiles  
✅ **Approval workflow** for controlled access  
✅ **Versatile & standard** for any project  

Your RBAC system is now **production-ready for any type of project**! 🎉

