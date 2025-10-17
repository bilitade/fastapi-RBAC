# Documentation Style Guide

## ✅ Documentation Updates Applied

All code documentation has been refined to be **professional, concise, and purposeful**.

## Documentation Philosophy

### ✅ What We Do
- **Focus on "why"** not "what" (code is self-explanatory)
- **Brief and clear** docstrings
- **Professional tone** without verbosity
- **Usage examples** where helpful
- **Minimal inline comments** (clean code speaks for itself)

### ❌ What We Avoid
- Obvious comments explaining what code does
- Verbose multi-paragraph explanations
- Repetitive parameter descriptions
- Over-documentation of simple operations

## Examples

### Module Docstrings

**Before:**
```python
"""
Authentication endpoints: login, logout, refresh token.
Provides comprehensive authentication functionality including
user login, logout, and token refresh operations with full
JWT token management and secure token rotation capabilities.
"""
```

**After:**
```python
"""Authentication endpoints for login, logout, and token refresh."""
```

### Function Docstrings

**Before:**
```python
def create_user(...) -> Any:
    """
    Create a new user. Requires 'create_user' permission.
    
    This endpoint allows authenticated users with the appropriate
    permission to create new user accounts in the system.
    
    - **email**: Unique email address for the new user
    - **password**: Password that will be hashed before storage
    
    Returns:
        UserResponse: The newly created user object
        
    Raises:
        HTTPException: If user already exists or permission denied
    """
```

**After:**
```python
def create_user(...) -> Any:
    """Create new user (requires 'create_user' permission)."""
```

### Class Docstrings

**Before:**
```python
class User(Base):
    """
    User model representing authenticated users in the system.
    
    This model stores user information including their email,
    hashed password, and relationships to roles and refresh tokens.
    
    Attributes:
        id: Primary key identifier for the user
        email: Unique email address for authentication purposes
        password: Hashed password (never store plain text passwords)
        roles: List of roles assigned to this user for authorization
        refresh_tokens: List of active refresh tokens for this user
    """
```

**After:**
```python
class User(Base):
    """
    Authenticated user with role-based permissions.
    
    Relationships:
        roles: Assigned roles (many-to-many)
        refresh_tokens: Active JWT refresh tokens
    """
```

### Inline Comments

**Before:**
```python
# Check if user already exists in the database
existing_user = db.query(User).filter(User.email == user_data.email).first()

# If user exists, raise an error
if existing_user:
    raise HTTPException(...)

# Hash the password before storing it
user.password = hash_password(user_data.password)
```

**After:**
```python
existing_user = db.query(User).filter(User.email == user_data.email).first()
if existing_user:
    raise HTTPException(...)

user.password = hash_password(user_data.password)
```

**Only keep comments when they explain "why":**
```python
# JWT spec requires 'sub' claim to be string
if sub is not None and not isinstance(sub, str):
    to_encode["sub"] = str(sub)
```

## Updated Files

### Core Modules
- ✅ `app/main.py` - Concise app description
- ✅ `app/config/settings.py` - Clear configuration docs
- ✅ `app/core/security.py` - Brief function purposes
- ✅ `app/core/dependencies.py` - Usage-focused docs

### Database & Models
- ✅ `app/db/base.py` - Simple base documentation
- ✅ `app/db/session.py` - Clear session management docs
- ✅ `app/models/user.py` - Relationship-focused docs
- ✅ `app/models/role.py` - Concise model purpose
- ✅ `app/models/permission.py` - Brief permission docs
- ✅ `app/models/token.py` - Security-focused docs

### API Endpoints
- ✅ `app/api/v1/api.py` - Clean router aggregation
- ✅ `app/api/v1/endpoints/auth.py` - Action-focused docs
- ✅ `app/api/v1/endpoints/users.py` - Permission-focused docs
- ✅ `app/api/v1/endpoints/roles.py` - Clear operation docs
- ✅ `app/api/v1/endpoints/permissions.py` - Brief endpoint docs

### Middleware
- ✅ `app/middleware/rbac.py` - Usage example docs

## Benefits

### For Developers
- **Faster comprehension** - Less reading, more coding
- **Clear intent** - Understand purpose immediately
- **Professional appearance** - Industry-standard documentation
- **Easier maintenance** - Less documentation to update

### For API Users
- **Swagger UI clarity** - Clean, readable API docs
- **Quick reference** - Essential info at a glance
- **Professional impression** - Well-organized documentation

## Guidelines for Future Code

### 1. Module Docstrings
```python
"""Brief description of module purpose."""
```

### 2. Class Docstrings
```python
class MyClass:
    """
    One-line purpose.
    
    Relationships (if any):
        field: Description
    """
```

### 3. Function Docstrings

**Simple functions:**
```python
def simple_function(...):
    """Brief description of action."""
```

**Complex functions with usage:**
```python
def complex_function(...):
    """
    Brief description.
    
    Usage:
        result = complex_function(param)
    """
```

### 4. Inline Comments
Only when explaining **why**, not **what**:

```python
# Good: Explains rationale
# Token rotation required for security compliance
stored_token.revoked = True

# Bad: States the obvious
# Set revoked to True
stored_token.revoked = True
```

### 5. Type Hints Over Comments
Let type hints do the documentation:

```python
# Bad
def get_user(user_id):  # user_id: integer
    """Get a user by ID."""
    
# Good
def get_user(user_id: int) -> User:
    """Get user by ID."""
```

## Quick Checklist

When writing documentation, ask:

- [ ] Is this explaining "why" or just "what"?
- [ ] Would a developer understand without this comment?
- [ ] Does the function name already convey this?
- [ ] Are type hints sufficient?
- [ ] Is this adding value or just noise?

## Result

✅ **Professional, production-ready documentation**  
✅ **Clear and concise code comments**  
✅ **Self-documenting code structure**  
✅ **Industry-standard practices**  

Your RBAC system now has **enterprise-grade documentation** that is clear, professional, and maintainable! 🎯

