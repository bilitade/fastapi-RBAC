# Security Best Practices Guide

## 🎯 Overview

This guide provides security best practices for using and extending the JWT + RBAC + AI Service project.

---

## 🔐 Authentication & Authorization

### JWT Token Management

#### ✅ DO:
- **Use short-lived access tokens** (15-60 minutes)
- **Implement token refresh** with rotation
- **Store tokens securely** on client side (httpOnly cookies or secure storage)
- **Validate token type** (access vs refresh)
- **Check token expiration** on every request
- **Revoke refresh tokens** on logout

#### ❌ DON'T:
- Store tokens in localStorage (XSS vulnerable)
- Use long-lived access tokens (>1 hour)
- Share tokens between users
- Log tokens in plain text
- Send tokens in URL parameters

### Password Security

#### ✅ DO:
- **Enforce strong passwords**: min 8 chars, uppercase, lowercase, digit
- **Use Argon2** for hashing (already implemented)
- **Implement password reset** with time-limited tokens
- **Rate limit** login attempts
- **Monitor** failed login attempts

#### ❌ DON'T:
- Store passwords in plain text
- Use weak hashing (MD5, SHA1)
- Allow common passwords (123456, password)
- Email passwords to users
- Reuse passwords across systems

### RBAC Implementation

#### ✅ DO:
- **Principle of least privilege**: Grant minimum required permissions
- **Use permissions** for fine-grained control
- **Use roles** for grouping permissions
- **Validate permissions** on every protected endpoint
- **Audit permission changes**

#### ❌ DON'T:
- Grant admin role by default
- Skip permission checks
- Hard-code role names in business logic
- Allow users to self-assign admin roles

---

## 🛡️ Input Validation & Sanitization

### General Input Handling

#### ✅ DO:
```python
from app.middleware.input_sanitizer import InputSanitizer

# Sanitize all user inputs
text = InputSanitizer.sanitize_text(user_input, max_length=1000)

# Validate field names
field = InputSanitizer.sanitize_field_name(field_name)

# Sanitize dictionaries
data = InputSanitizer.sanitize_dict(user_data)
```

#### ❌ DON'T:
```python
# Never trust user input directly
query = f"SELECT * FROM users WHERE name = '{user_input}'"  # SQL Injection!

# Never execute user input
eval(user_input)  # Code injection!

# Never use user input in file paths without validation
open(f"/data/{user_input}")  # Path traversal!
```

### AI Prompt Safety

#### ✅ DO:
- **Limit prompt length** (4000 chars for AI prompts)
- **Sanitize prompts** before sending to AI
- **Validate AI responses** before displaying
- **Monitor AI usage** for abuse
- **Set rate limits** on AI endpoints

#### ❌ DON'T:
- Send unlimited-length prompts
- Trust AI output without validation
- Expose AI API keys in client code
- Allow prompt injection attacks

---

## 🌐 API Security

### Endpoint Protection

#### ✅ DO:
```python
from app.middleware import require_permission, require_role
from app.core.dependencies import get_current_user

# Protect with permissions
@router.post("/sensitive-action")
def sensitive_action(
    _: bool = Depends(require_permission("sensitive_action"))
):
    pass

# Protect with roles
@router.get("/admin-panel")
def admin_panel(
    _: bool = Depends(require_role("admin"))
):
    pass

# Get current user
@router.get("/profile")
def get_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user
```

#### ❌ DON'T:
```python
# Never skip authentication
@router.post("/sensitive-action")
def sensitive_action():  # No auth check!
    pass

# Never trust client-provided user IDs
@router.get("/user/{user_id}")
def get_user(user_id: int):  # No ownership check!
    return db.query(User).filter(User.id == user_id).first()
```

### Rate Limiting

#### ✅ DO:
- **Use built-in rate limiting** (already configured)
- **Adjust limits** per endpoint sensitivity
- **Monitor rate limit hits**
- **Return proper 429 responses**

#### Configuration:
```python
# In main.py
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=60,
    requests_per_hour=1000
)

# Sensitive endpoints have stricter limits:
# - Login: 5/min, 20/hour
# - Registration: 3/min, 10/hour
# - Token refresh: 10/min, 50/hour
```

---

## 🔒 Data Protection

### Database Security

#### ✅ DO:
- **Use ORM** (SQLAlchemy) for parameterized queries
- **Encrypt sensitive data** at rest
- **Use SSL/TLS** for database connections
- **Implement backups** with encryption
- **Limit database user permissions**

#### ❌ DON'T:
```python
# Never use string formatting for SQL
db.execute(f"SELECT * FROM users WHERE id = {user_id}")  # SQL Injection!

# Never store sensitive data unencrypted
user.credit_card = request.credit_card  # Store encrypted!

# Never log sensitive data
logger.info(f"User password: {password}")  # Never log passwords!
```

### Sensitive Data Handling

#### ✅ DO:
```python
# Hash passwords
from app.core.security import hash_password
user.password = hash_password(plain_password)

# Hash tokens for storage
from app.core.security import hash_token
token_hash = hash_token(refresh_token)

# Exclude sensitive fields from responses
class UserResponse(BaseModel):
    id: int
    email: str
    # password field excluded!
```

#### ❌ DON'T:
- Return password hashes in API responses
- Log authentication tokens
- Store API keys in code
- Commit secrets to version control

---

## 🌍 CORS & Headers

### CORS Configuration

#### ✅ DO:
```python
# In .env
BACKEND_CORS_ORIGINS="https://app.example.com,https://www.example.com"

# The app validates:
# - No wildcards in production
# - No localhost in production
```

#### ❌ DON'T:
```python
# Never use wildcard in production
BACKEND_CORS_ORIGINS="*"  # Blocked by validation!

# Never allow all origins
allow_origins=["*"]  # Security risk!
```

### Security Headers

The app automatically adds security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Content-Security-Policy`
- `Strict-Transport-Security` (HTTPS only)

---

## 🔍 Monitoring & Auditing

### Logging Best Practices

#### ✅ DO:
```python
import logging

logger = logging.getLogger(__name__)

# Log security events
logger.warning(f"Failed login attempt for user: {email}")
logger.info(f"User {user.id} accessed sensitive resource")
logger.error(f"Permission denied for user {user.id}")

# Log with context
logger.info(f"Action performed", extra={
    "user_id": user.id,
    "action": "delete_user",
    "target_id": target_user_id
})
```

#### ❌ DON'T:
```python
# Never log sensitive data
logger.info(f"User logged in with password: {password}")  # NO!
logger.debug(f"Token: {access_token}")  # NO!
logger.info(f"Credit card: {card_number}")  # NO!
```

### Audit Trail

#### ✅ DO:
- Log all authentication events
- Log permission changes
- Log sensitive data access
- Log failed authorization attempts
- Store logs securely with retention policy

---

## 🚀 Deployment Security

### Environment Variables

#### ✅ DO:
```bash
# Use strong random values
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Set production mode
DEBUG=False

# Use environment-specific configs
DATABASE_URL="postgresql://user:pass@prod-db:5432/rbac"
```

#### ❌ DON'T:
```bash
# Never use default values
SECRET_KEY="your-secret-key-change-in-production"  # Blocked!

# Never enable debug in production
DEBUG=True  # Exposes sensitive info!

# Never commit .env files
git add .env  # Use .env.example instead!
```

### HTTPS/TLS

#### ✅ DO:
- **Use HTTPS** in production (required)
- **Use TLS 1.2+** minimum
- **Use strong cipher suites**
- **Enable HSTS** (Strict-Transport-Security)
- **Use valid SSL certificates** (Let's Encrypt)

#### ❌ DON'T:
- Use HTTP in production
- Use self-signed certificates in production
- Allow weak ciphers (RC4, DES)
- Ignore certificate warnings

---

## 🧪 Security Testing

### Regular Testing

#### ✅ DO:
```bash
# Run security tests
pytest tests/test_security.py -v

# Check for vulnerabilities
pip install safety
safety check

# Scan for secrets in code
pip install detect-secrets
detect-secrets scan

# Static analysis
pip install bandit
bandit -r app/
```

### Penetration Testing

#### ✅ DO:
- Test authentication bypass
- Test authorization bypass
- Test SQL injection
- Test XSS vulnerabilities
- Test CSRF vulnerabilities
- Test rate limiting
- Test session management

---

## 📋 Security Checklist

### Development
- [ ] All inputs are validated
- [ ] All outputs are sanitized
- [ ] Sensitive data is encrypted
- [ ] Secrets are not in code
- [ ] Dependencies are up to date
- [ ] Security tests pass

### Deployment
- [ ] HTTPS is enabled
- [ ] DEBUG is False
- [ ] Strong SECRET_KEY is set
- [ ] CORS is properly configured
- [ ] Rate limiting is enabled
- [ ] Security headers are active
- [ ] Database is secured
- [ ] Backups are configured

### Operations
- [ ] Logs are monitored
- [ ] Failed logins are tracked
- [ ] Dependencies are updated
- [ ] Security patches are applied
- [ ] Audit logs are reviewed
- [ ] Incident response plan exists

---

## 🆘 Incident Response

### If You Detect a Security Issue

1. **Assess the severity**
   - Critical: Data breach, authentication bypass
   - High: Authorization bypass, injection vulnerabilities
   - Medium: Information disclosure, DoS
   - Low: Minor configuration issues

2. **Contain the issue**
   - Disable affected endpoints
   - Revoke compromised tokens
   - Block malicious IPs

3. **Investigate**
   - Check logs for extent of breach
   - Identify affected users
   - Determine root cause

4. **Remediate**
   - Apply security patch
   - Update dependencies
   - Rotate secrets if compromised

5. **Notify**
   - Inform affected users
   - Report to authorities if required
   - Document the incident

6. **Prevent recurrence**
   - Add security tests
   - Update documentation
   - Train team members

---

## 📚 Additional Resources

### Security Standards
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- OWASP API Security: https://owasp.org/www-project-api-security/
- CWE Top 25: https://cwe.mitre.org/top25/

### Tools
- **OWASP ZAP**: Web application security scanner
- **Burp Suite**: Security testing toolkit
- **SQLMap**: SQL injection testing
- **Nmap**: Network security scanner

### Learning
- OWASP WebGoat: Hands-on security training
- PortSwigger Web Security Academy
- HackTheBox: Penetration testing practice

---

**Remember: Security is not a one-time task, it's an ongoing process! 🔒**
