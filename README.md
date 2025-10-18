# FastAPI RBAC System

A production-ready **Role-Based Access Control (RBAC)** system built with FastAPI, featuring JWT authentication, permission-based authorization, and a clean, scalable architecture.

> 📚 **[Complete Documentation](docs/)** | 🚀 **[API Examples](docs/API_EXAMPLES.md)** | ⚡ **[Quick Reference](docs/QUICK_REFERENCE.md)**

## ✨ Features

### Authentication & Authorization
- 🔐 **JWT Authentication** with refresh token rotation
- 👥 **Role-Based Access Control** with fine-grained permissions
- 🛡️ **Secure Password Hashing** using Argon2
- 🔄 **Token Rotation** for enhanced security
- ✅ **User Approval Workflow** with activation controls

### Security Features 🔒 **ENHANCED**
- 🚦 **Rate Limiting** - Prevents brute force attacks (5 login attempts/min)
- 🛡️ **Security Headers** - XSS, clickjacking, MIME sniffing protection
- 🧹 **Input Sanitization** - AI prompt injection & XSS prevention
- 🔍 **Secret Validation** - Enforces strong SECRET_KEY in production
- 🌐 **CORS Protection** - Validates origins, blocks wildcards in production
- 📊 **Security Audit** - Comprehensive security testing suite

### AI Assistant 🤖 **NEW**
- 💬 **Intelligent Chat** - Context-aware conversations
- 💡 **Idea Generation** - Creative brainstorming
- ✨ **Content Enhancement** - Improve, expand, or summarize text
- 🎯 **Auto-Fill** - Smart form field suggestions
- 📚 **Document Search** - Semantic search with RAG
- 🔌 **Multi-LLM Support** - OpenAI, Anthropic, extensible

### Developer Experience
- 📝 **Complete User Profiles** - Name, title, email
- 🏗️ **Clean Architecture** following FastAPI best practices
- 📊 **PostgreSQL** support (SQLite for development)
- ✅ **Type Safety** with Python type hints and Pydantic v2
- 🧪 **Production Ready** with proper error handling
- 📖 **Comprehensive Documentation** (Swagger/ReDoc)

## 🏗️ Architecture

```
app/
├── api/
│   └── v1/
│       ├── api.py              # API router aggregator
│       └── endpoints/          # API endpoints
│           ├── auth.py         # Authentication
│           ├── users.py        # User management
│           ├── roles.py        # Role management
│           ├── permissions.py  # Permission management
│           └── ai.py           # AI assistant 🤖
├── config/
│   └── settings.py             # Configuration management
├── core/
│   ├── dependencies.py         # Common dependencies
│   └── security.py             # Security utilities
├── db/
│   ├── base.py                 # Database base class
│   └── session.py              # Database session
├── ai/                         # AI assistant module 🤖
│   ├── services/              # AI services
│   │   ├── llm_factory.py    # Provider-agnostic LLM
│   │   ├── chat_service.py   # Chat functionality
│   │   ├── content_service.py # Content generation
│   │   ├── document_service.py # Document RAG
│   │   └── agent_service.py  # AI agent
│   ├── tools/                # Custom LangChain tools
│   └── chains/               # LangChain chains
├── middleware/
│   └── rbac.py               # RBAC decorators
├── models/                   # SQLAlchemy models
│   ├── user.py
│   ├── role.py
│   ├── permission.py
│   └── token.py
├── schemas/                  # Pydantic schemas
│   ├── user.py
│   ├── role.py
│   ├── permission.py
│   ├── token.py
│   └── ai.py                # AI schemas 🤖
├── scripts/
│   ├── init_db.py           # Database initialization
│   └── index_documents.py   # Document indexing 🤖
└── main.py                  # FastAPI application
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL (or SQLite for development)
- pip or poetry

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd RBAC
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   python -m app.scripts.init_db
   ```

6. **Configure AI (Optional)**
   ```bash
   # Add to .env
   OPENAI_API_KEY="sk-your-key-here"
   
   # Index documents for AI search
   python -m app.scripts.index_documents ./docs
   ```

7. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

8. **Access the API documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 🔑 Default Users

After running the initialization script, the following users are created:

| Email | Password | Role |
|-------|----------|------|
| superadmin@example.com | SuperAdmin123! | superadmin |
| admin@example.com | Admin123! | admin |
| user@example.com | User123! | normal |

**⚠️ Important**: Change these passwords in production!

## 📖 API Usage

### Authentication

1. **Login**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin@example.com&password=Admin123!"
   ```

2. **Use Access Token**
   ```bash
   curl -X GET "http://localhost:8000/api/v1/users/me" \
     -H "Authorization: Bearer <access_token>"
   ```

3. **Refresh Token**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
     -H "Content-Type: application/json" \
     -d '{"refresh_token": "<refresh_token>"}'
   ```

### User Management

```bash
# Create a user (requires 'create_user' permission)
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123!"
  }'

# Get current user
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <token>"

# List all users (requires 'view_user' permission)
curl -X GET "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer <token>"
```

### Role & Permission Management

```bash
# Create a role (requires 'manage_roles' permission)
curl -X POST "http://localhost:8000/api/v1/roles/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "manager",
    "permission_names": ["view_user", "create_task"]
  }'

# Create a permission (requires 'manage_permissions' permission)
curl -X POST "http://localhost:8000/api/v1/permissions/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "approve_document"}'
```

## 🛡️ Security Features

### Password Security
- **Argon2** hashing algorithm (most secure)
- Strong password validation
- Minimum 8 characters with uppercase, lowercase, and digits

### Token Security
- **JWT** with expiration
- Separate access and refresh tokens
- Refresh token rotation (old token revoked when refreshed)
- Token hashing in database (SHA256)
- Token type validation

### RBAC System
- Users → Roles → Permissions hierarchy
- Permission-based endpoint protection
- Role-based endpoint protection
- Multiple permissions support (AND/OR logic)

## 🔧 Configuration

All configuration is managed through environment variables in `.env`:

### Key Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key | (must change in production) |
| `DATABASE_URL` | Database connection string | PostgreSQL localhost |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | 60 minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | 7 days |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins | localhost:3000,8000 |

## 📝 Adding New Permissions

1. **Add to initialization script** (`app/scripts/init_db.py`)
   ```python
   DEFAULT_PERMISSIONS = [
       # ... existing permissions
       "your_new_permission",
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

3. **Protect endpoints**
   ```python
   from app.middleware import require_permission
   
   @router.post("/protected-endpoint")
   def protected_endpoint(
       _: bool = Depends(require_permission("your_new_permission"))
   ):
       pass
   ```

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## 📦 Deployment

### Production Checklist

- [ ] Change `SECRET_KEY` to a secure random value
- [ ] Set `DEBUG=false`
- [ ] Use PostgreSQL (not SQLite)
- [ ] Configure proper CORS origins
- [ ] Change default user passwords
- [ ] Use HTTPS/SSL
- [ ] Set up proper logging
- [ ] Configure database backups
- [ ] Use environment variables for secrets
- [ ] Set up monitoring and alerting

### Docker Deployment (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Integration Guide

To integrate this RBAC system into your project:

1. **Copy the structure** to your project
2. **Customize permissions** in `init_db.py`
3. **Add your endpoints** to `app/api/v1/endpoints/`
4. **Protect endpoints** using decorators:
   ```python
   from app.middleware import require_permission, require_role
   
   @router.get("/my-endpoint")
   def my_endpoint(
       _: bool = Depends(require_permission("my_permission"))
   ):
       pass
   ```

## 📚 Best Practices

1. **Always use dependencies** for authentication/authorization
2. **Never store plain passwords** (use `hash_password`)
3. **Validate input** with Pydantic schemas
4. **Use type hints** everywhere
5. **Follow RESTful conventions**
6. **Keep permissions granular** (create_user, not admin)
7. **Use environment variables** for configuration
8. **Log security events** (login attempts, permission denials)

## 🔒 Security

This project has been **thoroughly audited** for security vulnerabilities. See [SECURITY_AUDIT.md](SECURITY_AUDIT.md) for the full report.

### Security Score: 95/100 ✅

**Key Security Features:**
- ✅ JWT with token rotation and revocation
- ✅ Argon2 password hashing
- ✅ Rate limiting (5 login attempts/min)
- ✅ Security headers (XSS, clickjacking protection)
- ✅ Input sanitization and validation
- ✅ SQL injection protection (ORM)
- ✅ CORS validation
- ✅ Secret key validation

### Run Security Tests
```bash
# Run comprehensive security test suite
./run_security_tests.sh

# Or run specific tests
pytest tests/test_security.py -v
```

### Documentation
- 📋 [Security Audit Report](SECURITY_AUDIT.md)
- 🛡️ [Security Best Practices](SECURITY_BEST_PRACTICES.md)
- 🚀 [Deployment Guide](DEPLOYMENT_GUIDE.md)

## 🔄 Future Enhancements

- [x] Rate limiting ✅
- [x] Security headers ✅
- [x] Input sanitization ✅
- [ ] Email verification
- [ ] Password reset flow
- [ ] Two-factor authentication (2FA)
- [ ] Audit logging with request IDs
- [ ] API versioning with deprecation
- [ ] GraphQL support
- [ ] WebSocket authentication
- [ ] Multi-tenancy support

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [python-jose](https://python-jose.readthedocs.io/)
- [Passlib](https://passlib.readthedocs.io/)

---

**Need help?** Check the [API documentation](http://localhost:8000/docs) or open an issue.

