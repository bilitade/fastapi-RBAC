# 🧪 Testing Guide - FastAPI RBAC API

Complete guide for testing and validating the RBAC API system.

---

## 🚀 Quick Start Testing

### 1. Start the Application

```bash
# Activate virtual environment
source .venv/bin/activate

# Start server
uvicorn app.main:app --reload

# Or with docker-compose
docker-compose up -d
```

### 2. Verify Server is Running

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","app":"RBAC API","version":"1.0.0"}
```

---

## 📋 Manual Testing Checklist

### ✅ Authentication Tests

#### Test 1: Login with Admin
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=Admin123!"
```

**Expected:** 200 OK with `access_token` and `refresh_token`

#### Test 2: Login with Invalid Credentials
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=wrong"
```

**Expected:** 401 Unauthorized

#### Test 3: Refresh Token
```bash
# Save access token from login
export ACCESS_TOKEN="your_access_token_here"
export REFRESH_TOKEN="your_refresh_token_here"

curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\":\"$REFRESH_TOKEN\"}"
```

**Expected:** 200 OK with new tokens

#### Test 4: Logout
```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\":\"$REFRESH_TOKEN\"}"
```

**Expected:** 200 OK

---

### ✅ Authorization Tests

#### Test 5: Access Protected Endpoint (Authenticated)
```bash
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Expected:** 200 OK with user data

#### Test 6: Access Protected Endpoint (No Token)
```bash
curl -X GET http://localhost:8000/api/v1/users/me
```

**Expected:** 401 Unauthorized

#### Test 7: Permission Check (Admin Only)
```bash
# Login as regular user
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=User123!"

# Try to delete user (requires delete_user permission)
curl -X DELETE http://localhost:8000/api/v1/users/5 \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN"
```

**Expected:** 403 Forbidden (user doesn't have delete_user permission)

---

### ✅ Password Management Tests

#### Test 8: Request Password Reset
```bash
curl -X POST http://localhost:8000/api/v1/password/request-reset \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com"}'
```

**Expected:** 200 OK (check email for reset link)

#### Test 9: Reset Password with Token
```bash
curl -X POST http://localhost:8000/api/v1/password/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "token":"reset_token_from_email",
    "new_password":"NewPassword123!"
  }'
```

**Expected:** 200 OK

#### Test 10: Change Password (Authenticated)
```bash
curl -X POST http://localhost:8000/api/v1/password/change-password \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password":"Admin123!",
    "new_password":"NewAdmin123!"
  }'
```

**Expected:** 200 OK

---

### ✅ RBAC Tests

#### Test 11: List Users (All Roles)
```bash
curl -X GET http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Expected:** 200 OK with user list (all roles have view_user permission)

#### Test 12: Create User (Admin/Manager Only)
```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email":"newuser@example.com",
    "password":"NewUser123!",
    "first_name":"New",
    "last_name":"User",
    "middle_name":"Test"
  }'
```

**Expected:** 
- Admin/Manager: 201 Created
- User/Guest: 403 Forbidden

#### Test 13: List Roles
```bash
curl -X GET http://localhost:8000/api/v1/roles \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Expected:** 200 OK with roles list

#### Test 14: List Permissions
```bash
curl -X GET http://localhost:8000/api/v1/permissions \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Expected:** 200 OK with permissions list

---

### ✅ Rate Limiting Tests

#### Test 15: Brute Force Protection
```bash
# Try to login 10 times rapidly
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin@example.com&password=wrong"
  echo ""
done
```

**Expected:** After 5 attempts, should get 429 Too Many Requests

---

### ✅ API Documentation Tests

#### Test 16: Swagger UI
```bash
# Open in browser
open http://localhost:8000/docs
```

**Expected:** Swagger UI loads correctly with all endpoints

#### Test 17: ReDoc
```bash
# Open in browser
open http://localhost:8000/redoc
```

**Expected:** ReDoc loads correctly

#### Test 18: OpenAPI Schema
```bash
curl http://localhost:8000/openapi.json | jq
```

**Expected:** Valid OpenAPI 3.0 JSON schema

---

## 🔬 Automated Testing

### Run Unit Tests

```bash
# Install pytest if not already
pip install pytest pytest-asyncio httpx

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
```

### Test Database Population

```bash
# Full reset
python3 app/scripts/init_database.py

# Just populate
python3 app/scripts/populate_database.py

# Verify
python3 -c "
from app.db.session import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission

db = SessionLocal()
print(f'Users: {db.query(User).count()}')
print(f'Roles: {db.query(Role).count()}')
print(f'Permissions: {db.query(Permission).count()}')

# Check admin permissions
admin = db.query(User).filter(User.email == 'admin@example.com').first()
if admin and admin.roles:
    print(f'Admin has {len(admin.roles[0].permissions)} permissions')
db.close()
"
```

**Expected Output:**
```
Users: 5
Roles: 4
Permissions: 10
Admin has 10 permissions
```

---

## 🔐 Security Testing

### Test 1: SQL Injection Prevention
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin' OR '1'='1&password=anything"
```

**Expected:** 401 Unauthorized (not vulnerable)

### Test 2: XSS Prevention
```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email":"test@example.com",
    "password":"Test123!",
    "first_name":"<script>alert(1)</script>",
    "last_name":"User"
  }'
```

**Expected:** 400 Bad Request (script tags blocked)

### Test 3: Token Expiration
```bash
# Wait for token to expire (default: 60 minutes)
# Or use an old token
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer expired_token"
```

**Expected:** 401 Unauthorized

### Test 4: CORS Headers
```bash
curl -X OPTIONS http://localhost:8000/api/v1/users \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -v
```

**Expected:** CORS headers present in response

---

## 📊 Performance Testing

### Load Test with Apache Bench

```bash
# Install apache bench
sudo apt-get install apache2-utils  # Ubuntu/Debian
brew install httpd  # macOS

# Test health endpoint
ab -n 1000 -c 10 http://localhost:8000/health

# Test login endpoint
ab -n 100 -c 5 -p login.json -T application/x-www-form-urlencoded \
  http://localhost:8000/api/v1/auth/login
```

**Expected Metrics:**
- Requests per second: > 100
- Mean response time: < 100ms
- Failed requests: 0

### Load Test with Locust

```bash
# Install locust
pip install locust

# Create locustfile.py
cat > locustfile.py << 'EOF'
from locust import HttpUser, task, between

class RBACUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post("/api/v1/auth/login", data={
            "username": "user@example.com",
            "password": "User123!"
        })
        if response.status_code == 200:
            self.token = response.json()["access_token"]
    
    @task(3)
    def get_users(self):
        self.client.get("/api/v1/users", headers={
            "Authorization": f"Bearer {self.token}"
        })
    
    @task(1)
    def get_me(self):
        self.client.get("/api/v1/users/me", headers={
            "Authorization": f"Bearer {self.token}"
        })
EOF

# Run load test
locust -f locustfile.py --host=http://localhost:8000
```

Open http://localhost:8089 and configure test parameters.

---

## 🐳 Docker Testing

### Test Docker Build
```bash
# Build image
docker build -t rbac-api .

# Run container
docker run -p 8000:8000 --env-file .env rbac-api

# Test health
curl http://localhost:8000/health
```

### Test docker-compose
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# Check logs
docker-compose logs app

# Test connectivity
curl http://localhost:8000/health

# Stop services
docker-compose down
```

---

## ✅ Validation Checklist

### Before Deployment

- [ ] All authentication tests pass
- [ ] All authorization tests pass
- [ ] Password reset working
- [ ] Rate limiting functional
- [ ] Database populated correctly
- [ ] Admin has all permissions
- [ ] Swagger UI loads
- [ ] Health check returns 200
- [ ] Docker build succeeds
- [ ] docker-compose starts all services
- [ ] No security vulnerabilities
- [ ] Load test passes (>100 req/sec)
- [ ] All endpoints documented
- [ ] Environment variables configured
- [ ] Logs are readable

### Production Readiness

- [ ] Database migrations tested
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] Alerts set up
- [ ] SSL certificates configured
- [ ] Secrets management configured
- [ ] Load balancer configured
- [ ] Auto-scaling configured
- [ ] Disaster recovery plan documented
- [ ] Rollback procedure tested

---

## 🔍 Troubleshooting

### Issue: Server won't start
```bash
# Check logs
tail -f uvicorn.log

# Check database connection
psql -U postgres -d rbac

# Check environment variables
cat .env
```

### Issue: Tests failing
```bash
# Reinitialize database
python3 app/scripts/init_database.py

# Check test database
pytest tests/ -v --tb=short
```

### Issue: Authentication not working
```bash
# Verify user exists
python3 -c "
from app.db.session import SessionLocal
from app.models.user import User
db = SessionLocal()
user = db.query(User).filter(User.email == 'admin@example.com').first()
print(f'User found: {user is not None}')
print(f'Is active: {user.is_active if user else False}')
print(f'Is approved: {user.is_approved if user else False}')
db.close()
"

# Test password verification
python3 -c "
from app.core.security import verify_password, hash_password
hashed = hash_password('Admin123!')
print(f'Password matches: {verify_password(\"Admin123!\", hashed)}')
"
```

---

## 📚 Additional Resources

- **API Documentation:** http://localhost:8000/docs
- **Project Status:** `PROJECT_STATUS.md`
- **Deployment Guide:** `DEPLOYMENT_GUIDE.md`
- **Security Practices:** `SECURITY_BEST_PRACTICES.md`

---

**Happy Testing! 🧪**
