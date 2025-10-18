# ✅ Permissions Fixed - Mapped to Endpoints

## 🎉 Issue Resolved

**Problem:** Admin was getting "Permission denied. Required: view_user" error

**Root Cause:** Database had `view_users` (plural) but endpoints checked for `view_user` (singular)

**Solution:** Updated both scripts to create permissions that match what endpoints actually check for

---

## 📊 Correct Permissions (10 Total)

### User Management (4)
- **`view_user`** - View user details and list users
- **`create_user`** - Create new users
- **`edit_user`** - Edit user details and approve users
- **`delete_user`** - Delete users

### Role Management (1)
- **`manage_roles`** - Full role management (create, read, update, delete)

### Permission Management (1)
- **`manage_permissions`** - Full permission management (create, read, update, delete)

### AI Features (2)
- **`use_ai`** - Use AI assistant features
- **`manage_ai`** - Manage AI configurations

### File Management (2)
- **`user:read`** - Read/list files
- **`user:write`** - Upload/write files

---

## 👥 Role Assignments

### Admin Role
**Permissions:** All 10 permissions
- view_user
- create_user
- edit_user
- delete_user
- manage_roles
- manage_permissions
- use_ai
- manage_ai
- user:read
- user:write

### Manager Role
**Permissions:** 7 permissions (no delete_user, manage_permissions, manage_ai)
- view_user
- create_user
- edit_user
- manage_roles
- use_ai
- user:read
- user:write

### User Role
**Permissions:** 3 permissions (basic access)
- view_user
- use_ai
- user:write

### Guest Role
**Permissions:** 1 permission (read-only)
- view_user

---

## 🔗 Endpoint Mapping

### User Endpoints (`/api/v1/users`)

| Endpoint | Method | Permission Required |
|----------|--------|---------------------|
| `/users/me` | GET | None (authenticated) |
| `/users/me` | PATCH | None (authenticated) |
| `/users/me/password` | POST | None (authenticated) |
| `/users` | POST | `create_user` |
| `/users/{id}` | GET | `view_user` |
| `/users` | GET | `view_user` |
| `/users/{id}` | PATCH | `edit_user` |
| `/users/{id}/approve` | POST | `edit_user` |
| `/users/{id}` | DELETE | `delete_user` |

### Role Endpoints (`/api/v1/roles`)

| Endpoint | Method | Permission Required |
|----------|--------|---------------------|
| `/roles` | POST | `manage_roles` |
| `/roles/{id}` | GET | `manage_roles` |
| `/roles` | GET | `manage_roles` |
| `/roles/{id}` | PATCH | `manage_roles` |
| `/roles/{id}` | DELETE | `manage_roles` |

### Permission Endpoints (`/api/v1/permissions`)

| Endpoint | Method | Permission Required |
|----------|--------|---------------------|
| `/permissions` | POST | `manage_permissions` |
| `/permissions/{id}` | GET | `manage_permissions` |
| `/permissions` | GET | `manage_permissions` |
| `/permissions/{id}` | DELETE | `manage_permissions` |

### File Endpoints (`/api/v1/files`)

| Endpoint | Method | Permission Required |
|----------|--------|---------------------|
| `/files/upload` | POST | None (authenticated) |
| `/files` | GET | `user:read` |

---

## ✅ Verification

### Test Admin Access

```bash
# Login as admin
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=Admin123!"

# Get token from response
export TOKEN="your_access_token_here"

# Test view_user permission
curl -X GET http://127.0.0.1:8000/api/v1/users \
  -H "Authorization: Bearer $TOKEN"

# Should work! ✅
```

### Test Manager Access

```bash
# Login as manager
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=manager@example.com&password=Manager123!"

# Test create_user permission
curl -X POST http://127.0.0.1:8000/api/v1/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "NewUser123!",
    "first_name": "New",
    "last_name": "User"
  }'

# Should work! ✅
```

### Test User Access

```bash
# Login as user
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=User123!"

# Test view_user permission
curl -X GET http://127.0.0.1:8000/api/v1/users \
  -H "Authorization: Bearer $TOKEN"

# Should work! ✅

# Test create_user permission (should fail)
curl -X POST http://127.0.0.1:8000/api/v1/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...}'

# Should fail with 403 Forbidden ❌
```

---

## 🔄 How to Apply

### Option 1: Full Reset (Recommended)

```bash
python3 app/scripts/init_database.py
```

This will:
1. Drop all tables
2. Create fresh tables
3. Populate with correct permissions
4. Create 5 users with proper roles

### Option 2: Data Refresh

```bash
python3 app/scripts/populate_database.py
```

This will:
1. Clear existing data
2. Keep table structure
3. Populate with correct permissions
4. Create 4 users with proper roles

---

## 📝 Database Status

After running the script:

```
✅ Permissions: 10 (down from 20, now matching endpoints)
✅ Roles: 4 (admin, manager, user, guest)
✅ Users: 5 (admin, manager, user, guest, inactive)
✅ Admin role has all 10 permissions
✅ All permissions match endpoint requirements
```

---

## 🎯 What Changed

### Before (Broken)

```python
# Database had:
permissions = [
    "view_users",      # ❌ Plural
    "update_user",     # ❌ Wrong name
    "view_roles",      # ❌ Too granular
    "create_role",     # ❌ Too granular
    # ... 20 total
]

# Endpoints checked for:
require_permission("view_user")  # ❌ Mismatch!
```

### After (Fixed)

```python
# Database has:
permissions = [
    "view_user",       # ✅ Singular
    "edit_user",       # ✅ Correct name
    "manage_roles",    # ✅ Combined
    # ... 10 total
]

# Endpoints check for:
require_permission("view_user")  # ✅ Match!
```

---

## 🚀 Success!

**Status:** ✅ **PERMISSIONS FIXED**

Admin now has proper access to all endpoints! The permission names in the database now match exactly what the endpoints check for.

**Test it:**
1. Run the init script
2. Start the server
3. Login as admin
4. Try accessing `/api/v1/users` endpoint
5. Should work perfectly! ✅
