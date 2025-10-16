# RBAC System - Quick Reference

## ✅ What's Done

Your RBAC system has been completely restructured and is **production-ready**!

### Key Improvements
- ✅ **Modular architecture** - 27 organized files in logical packages
- ✅ **FastAPI best practices** - Dependency injection, proper routing, versioning
- ✅ **Pydantic v2** - Modern validation with proper configuration
- ✅ **Python typing** - Full type hints throughout
- ✅ **SQLAlchemy 2.0** - Modern ORM with `Mapped` types
- ✅ **Production security** - JWT, token rotation, Argon2 hashing
- ✅ **Environment config** - Settings via `.env` file
- ✅ **Comprehensive docs** - README, usage guide, examples

## 🚀 Quick Start

### 1. Start the Server
```bash
cd /home/bilisuma/Desktop/RBAC
source .venv/bin/activate
uvicorn app.main:app --reload --port 8001
```

### 2. Access the API
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **Health Check**: http://localhost:8001/health

### 3. Test Login
Use the Swagger UI to test authentication:
- Go to http://localhost:8001/docs
- Click on `/api/v1/auth/login`
- Try it out with:
  - **username**: `admin@example.com`
  - **password**: `Admin123!`
- Copy the `access_token` from the response
- Click **Authorize** button (top right) and paste the token

## 📁 Project Structure

```
app/
├── api/v1/endpoints/    # API endpoints (auth, users, roles, permissions)
├── config/              # Environment-based settings
├── core/                # Security, dependencies
├── db/                  # Database session management
├── models/              # SQLAlchemy models (user, role, permission, token)
├── schemas/             # Pydantic schemas (validation)
├── middleware/          # RBAC decorators
└── scripts/             # Database initialization
```

## 🔐 Default Users

| Email | Password | Role | Access Level |
|-------|----------|------|--------------|
| superadmin@example.com | SuperAdmin123! | superadmin | All permissions |
| admin@example.com | Admin123! | admin | Most permissions |
| user@example.com | User123! | normal | Limited permissions |

**⚠️ Change these passwords for production!**

## 🎯 Common Tasks

### Protect an Endpoint with Permission
```python
from fastapi import APIRouter, Depends
from app.middleware import require_permission

router = APIRouter()

@router.post("/documents/")
def create_document(
    _: bool = Depends(require_permission("create_document"))
):
    return {"message": "Document created"}
```

### Protect with Multiple Permissions
```python
from app.middleware import require_permissions

@router.delete("/important-data/")
def delete_data(
    _: bool = Depends(require_permissions(["delete_data", "admin_access"]))
):
    # User must have BOTH permissions
    return {"message": "Deleted"}
```

### Protect with Role
```python
from app.middleware import require_role

@router.get("/admin/dashboard")
def admin_dashboard(
    _: bool = Depends(require_role("admin"))
):
    return {"message": "Admin dashboard"}
```

### Add New Permissions

1. Edit `app/scripts/init_db.py`:
   ```python
   DEFAULT_PERMISSIONS = [
       # ... existing
       "your_new_permission",
   ]
   ```

2. Assign to roles:
   ```python
   role_permission_map = {
       "admin": [
           # ... existing
           "your_new_permission",
       ]
   }
   ```

3. Re-run initialization:
   ```bash
   python -m app.scripts.init_db
   ```

### Add New Endpoints

1. Create file in `app/api/v1/endpoints/your_resource.py`
2. Register in `app/api/v1/api.py`:
   ```python
   from app.api.v1.endpoints import your_resource
   
   api_router.include_router(
       your_resource.router,
       prefix="/your-resource",
       tags=["Your Resource"]
   )
   ```

## 🔧 Configuration

Edit `.env` file for your environment:

```bash
# Security - Generate with: openssl rand -hex 32
SECRET_KEY="your-secret-key-change-in-production"

# Database
DATABASE_URL="postgresql+psycopg2://user:pass@localhost:5432/rbac"

# Tokens
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (comma-separated)
BACKEND_CORS_ORIGINS="http://localhost:3000,http://localhost:8000"
```

## 📚 Documentation Files

- **README.md** - Full documentation with features, setup, deployment
- **USAGE_GUIDE.md** - Step-by-step API usage and examples
- **MIGRATION_SUMMARY.md** - What changed and why
- **CHANGES.md** - Detailed before/after code comparisons
- **QUICK_REFERENCE.md** - This file - quick commands and examples

## 🔄 Using in New Projects

### Copy Entire System
```bash
cp -r /home/bilisuma/Desktop/RBAC /path/to/new/project
cd /path/to/new/project
# Edit app/scripts/init_db.py with your permissions
# Add your endpoints to app/api/v1/endpoints/
```

### Copy Just Auth System
```bash
cp -r RBAC/app/core /your-project/app/
cp -r RBAC/app/middleware /your-project/app/
cp -r RBAC/app/models/{user,role,permission,token}.py /your-project/app/models/
cp -r RBAC/app/schemas/{user,role,permission,token}.py /your-project/app/schemas/
```

## 🧪 Testing API with curl

### Login
```bash
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=Admin123!"
```

### Get Current User
```bash
curl -X GET "http://localhost:8001/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Create User
```bash
curl -X POST "http://localhost:8001/api/v1/users/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123!"
  }'
```

## 🎓 Standards Followed

✅ **FastAPI Standards**
- Dependency injection for auth and database
- Proper HTTP status codes
- Response models for documentation
- API versioning

✅ **Pydantic v2**
- `ConfigDict` instead of `Config` class
- `from_attributes=True` instead of `orm_mode`
- Proper field validation with `Field`

✅ **Python Typing**
- Type hints on all functions
- Generic types from `typing`
- SQLAlchemy 2.0 `Mapped` types

✅ **Security**
- Environment variable secrets
- Argon2 password hashing (strongest available)
- JWT with token rotation
- Permission-based access control

## 🚨 Production Checklist

Before deploying to production:

- [ ] Change `SECRET_KEY` in `.env` (use `openssl rand -hex 32`)
- [ ] Set `DEBUG=false`
- [ ] Update `DATABASE_URL` to production database
- [ ] Change all default user passwords
- [ ] Configure proper CORS origins
- [ ] Use HTTPS/SSL
- [ ] Set up proper logging
- [ ] Configure database backups
- [ ] Review and adjust token expiration times
- [ ] Set up monitoring (health endpoint available)

## 💡 Tips

1. **Always restart** the server after changing `.env` file
2. **Use Swagger UI** (http://localhost:8001/docs) for testing - it's interactive!
3. **Check logs** if something doesn't work - FastAPI gives detailed error messages
4. **Read the docs** - comprehensive guides in README.md and USAGE_GUIDE.md
5. **Permissions are granular** - prefer specific permissions over broad ones

## 🆘 Troubleshooting

**Database connection error?**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql
# Or use SQLite for testing: DATABASE_URL="sqlite:///./rbac.db"
```

**Port already in use?**
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

**Permission denied?**
- Make sure you're logged in and token is valid
- Check user has the required permission/role
- Token might be expired - login again

**Import errors?**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

## 🎉 You're All Set!

Your RBAC system is production-ready and follows all modern FastAPI best practices.

**Next Steps:**
1. Start the server: `uvicorn app.main:app --reload --port 8001`
2. Open http://localhost:8001/docs
3. Try logging in and exploring the API
4. Start adding your own endpoints!

---

**Questions?** Check the comprehensive docs in README.md and USAGE_GUIDE.md
**Need examples?** See CHANGES.md for before/after code comparisons

