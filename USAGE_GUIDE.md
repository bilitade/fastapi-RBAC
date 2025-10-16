# RBAC System - Usage Guide

## Quick Start

### 1. Installation & Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Edit .env with your settings (especially DATABASE_URL and SECRET_KEY)
nano .env

# Initialize database with default data
python -m app.scripts.init_db

# Start the server
uvicorn app.main:app --reload
```

### 2. Access the API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Using the RBAC System

### Authentication Flow

#### 1. Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=Admin123!"
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

#### 2. Use Access Token
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <your_access_token>"
```

#### 3. Refresh Token (when access token expires)
```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<your_refresh_token>"}'
```

#### 4. Logout
```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<your_refresh_token>"}'
```

## Permission System

### Default Roles & Permissions

| Role | Permissions |
|------|-------------|
| **superadmin** | All permissions |
| **admin** | create_user, view_user, edit_user, create_board, edit_board, view_board, create_task, edit_task, view_task |
| **normal** | view_board, view_task, create_task |

### Default Permissions

**User Management:**
- `create_user` - Create new users
- `delete_user` - Delete users
- `view_user` - View user details
- `edit_user` - Edit user information

**Role & Permission Management:**
- `manage_roles` - Manage roles
- `manage_permissions` - Manage permissions

**Example Application Permissions:**
- `create_board`, `edit_board`, `delete_board`, `view_board`
- `create_task`, `edit_task`, `delete_task`, `view_task`

## Common Operations

### User Management

#### Create a User
```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123!"
  }'
```

#### Get Current User Profile
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <token>"
```

#### Update User
```bash
curl -X PUT "http://localhost:8000/api/v1/users/1" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "updated@example.com",
    "role_names": ["admin"]
  }'
```

#### Delete User
```bash
curl -X DELETE "http://localhost:8000/api/v1/users/1" \
  -H "Authorization: Bearer <token>"
```

### Role Management

#### Create a Role
```bash
curl -X POST "http://localhost:8000/api/v1/roles/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "manager",
    "permission_names": ["view_user", "create_task", "edit_task"]
  }'
```

#### List All Roles
```bash
curl -X GET "http://localhost:8000/api/v1/roles/" \
  -H "Authorization: Bearer <token>"
```

#### Update Role Permissions
```bash
curl -X PUT "http://localhost:8000/api/v1/roles/1" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "permission_names": ["view_user", "edit_user", "create_task"]
  }'
```

### Permission Management

#### Create a Permission
```bash
curl -X POST "http://localhost:8000/api/v1/permissions/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "approve_document"}'
```

#### List All Permissions
```bash
curl -X GET "http://localhost:8000/api/v1/permissions/" \
  -H "Authorization: Bearer <token>"
```

## Integrating into Your Application

### 1. Protect Endpoints with Permissions

```python
from fastapi import APIRouter, Depends
from app.middleware import require_permission

router = APIRouter()

@router.post("/documents/")
def create_document(
    _: bool = Depends(require_permission("create_document"))
):
    # Only users with 'create_document' permission can access
    return {"message": "Document created"}
```

### 2. Protect Endpoints with Roles

```python
from app.middleware import require_role

@router.get("/admin/dashboard")
def admin_dashboard(
    _: bool = Depends(require_role("admin"))
):
    # Only users with 'admin' role can access
    return {"message": "Admin dashboard"}
```

### 3. Require Multiple Permissions

```python
from app.middleware import require_permissions

@router.delete("/documents/{doc_id}")
def delete_document(
    doc_id: int,
    _: bool = Depends(require_permissions(["delete_document", "manage_documents"]))
):
    # User must have ALL specified permissions
    return {"message": f"Document {doc_id} deleted"}
```

### 4. Require Any of Multiple Permissions

```python
from app.middleware import require_permissions

@router.get("/reports/")
def view_reports(
    _: bool = Depends(
        require_permissions(["view_reports", "admin_access"], require_all=False)
    )
):
    # User needs at least ONE of the specified permissions
    return {"message": "Reports"}
```

### 5. Get Current User

```python
from app.core.dependencies import get_current_user
from app.models.user import User

@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "roles": [role.name for role in current_user.roles]
    }
```

## Adding New Features

### Add New Permissions

1. **Edit `app/scripts/init_db.py`**
   ```python
   DEFAULT_PERMISSIONS = [
       # ... existing permissions
       "your_new_permission",
       "another_permission",
   ]
   ```

2. **Assign to roles**
   ```python
   role_permission_map = {
       "admin": [
           # ... existing permissions
           "your_new_permission",
       ]
   }
   ```

3. **Re-run initialization**
   ```bash
   python -m app.scripts.init_db
   ```

### Add New Endpoints

1. **Create endpoint file** in `app/api/v1/endpoints/`
   ```python
   # app/api/v1/endpoints/documents.py
   from fastapi import APIRouter, Depends
   from app.middleware import require_permission
   
   router = APIRouter()
   
   @router.post("/")
   def create_document(
       _: bool = Depends(require_permission("create_document"))
   ):
       return {"message": "Document created"}
   ```

2. **Register in API router** (`app/api/v1/api.py`)
   ```python
   from app.api.v1.endpoints import documents
   
   api_router.include_router(
       documents.router,
       prefix="/documents",
       tags=["Documents"]
   )
   ```

## Environment Variables

Key configuration options in `.env`:

```bash
# Change this to a secure random value in production
SECRET_KEY="your-secret-key-change-in-production"

# Database connection
DATABASE_URL="postgresql+psycopg2://user:pass@localhost:5432/rbac"

# Token expiration
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (comma-separated)
BACKEND_CORS_ORIGINS="http://localhost:3000,http://localhost:8000"
```

## Troubleshooting

### Database Connection Error
- Verify PostgreSQL is running
- Check DATABASE_URL in `.env`
- Ensure database exists: `createdb rbac`

### Permission Denied Errors
- Verify user has the required role/permission
- Check token is valid and not expired
- Ensure Authorization header is set: `Bearer <token>`

### Invalid Token
- Token may have expired (refresh it)
- SECRET_KEY may have changed
- Token type mismatch (access vs refresh)

## Production Deployment

1. **Generate secure SECRET_KEY**
   ```bash
   openssl rand -hex 32
   ```

2. **Set DEBUG=false**

3. **Use production database** (PostgreSQL)

4. **Configure CORS** properly

5. **Change default passwords**

6. **Use HTTPS**

7. **Run with production server**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

## API Testing with Swagger UI

1. Go to http://localhost:8000/docs
2. Click **Authorize** button (top right)
3. Login at `/api/v1/auth/login` endpoint
4. Copy the `access_token` from response
5. Paste in Authorization popup: `Bearer <token>`
6. Click **Authorize**
7. All requests will now include the token

## Best Practices

1. ✅ Always validate input with Pydantic schemas
2. ✅ Use type hints everywhere
3. ✅ Create granular permissions (not just "admin")
4. ✅ Use refresh token rotation
5. ✅ Log authentication/authorization events
6. ✅ Implement rate limiting (future enhancement)
7. ✅ Use HTTPS in production
8. ✅ Regularly rotate SECRET_KEY
9. ✅ Monitor failed login attempts
10. ✅ Keep dependencies updated

---

For more details, check the [main README](README.md) or the [API documentation](http://localhost:8000/docs).

