# Production Deployment Guide

## 🚀 Pre-Deployment Checklist

### 1. Environment Configuration

#### Required Environment Variables
```bash
# Generate a strong secret key (CRITICAL!)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set in .env file
SECRET_KEY="<generated-key-here>"
DEBUG=False
DATABASE_URL="postgresql://user:password@host:5432/dbname"
BACKEND_CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"

# Token Expiration (adjust as needed)
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Configuration (if using AI features)
AI_PROVIDER="openai"
OPENAI_API_KEY="your-openai-key"
AI_MODEL="gpt-3.5-turbo"
```

#### Security Validation
The application will **automatically validate** critical security settings on startup:
- ✅ SECRET_KEY must be at least 32 characters
- ✅ Default SECRET_KEY is blocked in production (DEBUG=False)
- ✅ Wildcard CORS origins (*) are blocked in production
- ✅ Localhost origins are blocked in production

### 2. Database Setup

```bash
# Install PostgreSQL (recommended for production)
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE rbac;
CREATE USER rbac_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE rbac TO rbac_user;
\q

# Update DATABASE_URL in .env
DATABASE_URL="postgresql://rbac_user:secure_password@localhost:5432/rbac"
```

### 3. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Initialize Database

```bash
# Run database initialization script
python -m app.scripts.init_db

# This will create:
# - Database tables
# - Default roles (admin, manager, user)
# - Default permissions
# - Admin user (check console output for credentials)
```

### 5. Security Hardening

#### Enable HTTPS
```bash
# Use a reverse proxy (Nginx/Caddy) with SSL/TLS
# Example Nginx configuration:

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Security headers (additional layer)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP (redirect to HTTPS)
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 6. Run Application

#### Using Uvicorn (Development/Small Scale)
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Using Gunicorn (Production)
```bash
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile -
```

#### Using Docker
```bash
# Build image
docker build -t rbac-api .

# Run container
docker run -d \
    --name rbac-api \
    -p 8000:8000 \
    --env-file .env \
    rbac-api
```

#### Using Docker Compose
```bash
docker-compose up -d
```

### 7. Systemd Service (Linux)

Create `/etc/systemd/system/rbac-api.service`:

```ini
[Unit]
Description=RBAC API Service
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/RBAC
Environment="PATH=/path/to/RBAC/venv/bin"
ExecStart=/path/to/RBAC/venv/bin/gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable rbac-api
sudo systemctl start rbac-api
sudo systemctl status rbac-api
```

---

## 🔒 Security Features

### Built-in Security Protections

1. **JWT Authentication**
   - Access tokens (short-lived)
   - Refresh tokens (long-lived, with rotation)
   - Token revocation support
   - Secure token storage (SHA256 hashing)

2. **RBAC Authorization**
   - Permission-based access control
   - Role-based access control
   - Flexible AND/OR logic
   - User status validation (is_active)

3. **Password Security**
   - Argon2 hashing (industry standard)
   - Password strength validation
   - Minimum requirements enforced

4. **Rate Limiting**
   - General: 60 requests/minute, 1000/hour
   - Login: 5 requests/minute, 20/hour
   - Registration: 3 requests/minute, 10/hour
   - Prevents brute force attacks

5. **Security Headers**
   - X-Content-Type-Options: nosniff
   - X-Frame-Options: DENY
   - X-XSS-Protection: enabled
   - Content-Security-Policy
   - Strict-Transport-Security (HTTPS)
   - Referrer-Policy
   - Permissions-Policy

6. **Input Sanitization**
   - AI prompt length limits (4000 chars)
   - XSS pattern detection
   - SQL injection pattern detection
   - Field name validation
   - Dictionary size limits

7. **CORS Protection**
   - Configurable allowed origins
   - Credentials support
   - Wildcard blocked in production

---

## 📊 Monitoring & Logging

### Application Logs
```bash
# View logs
sudo journalctl -u rbac-api -f

# Or if using Docker
docker logs -f rbac-api
```

### Health Check
```bash
curl https://yourdomain.com/health
```

### Metrics to Monitor
- Request rate and latency
- Authentication failures
- Rate limit hits
- Database connection pool
- Memory and CPU usage
- Error rates

### Recommended Tools
- **Sentry**: Error tracking
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **ELK Stack**: Log aggregation

---

## 🔄 Maintenance

### Database Backups
```bash
# Automated daily backup
pg_dump -U rbac_user rbac > backup_$(date +%Y%m%d).sql

# Restore from backup
psql -U rbac_user rbac < backup_20231018.sql
```

### Update Dependencies
```bash
# Check for security updates
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update all (test in staging first!)
pip install --upgrade -r requirements.txt
```

### Rotate Secret Keys
```bash
# Generate new key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env file
# Restart application
sudo systemctl restart rbac-api
```

### Clean Up Old Refresh Tokens
```sql
-- Delete expired refresh tokens (run periodically)
DELETE FROM refresh_tokens 
WHERE expires_at < NOW() OR revoked = true;
```

---

## 🧪 Testing in Production

### Smoke Tests
```bash
# Health check
curl https://yourdomain.com/health

# API docs
curl https://yourdomain.com/docs

# Login test
curl -X POST https://yourdomain.com/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=YourPassword"
```

### Load Testing
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test 1000 requests, 10 concurrent
ab -n 1000 -c 10 https://yourdomain.com/health
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. "Default SECRET_KEY detected"
**Solution**: Generate and set a strong SECRET_KEY in .env

#### 2. "Database connection failed"
**Solution**: Check DATABASE_URL, ensure PostgreSQL is running

#### 3. "CORS error in browser"
**Solution**: Add your frontend URL to BACKEND_CORS_ORIGINS

#### 4. "Rate limit exceeded"
**Solution**: Normal behavior, wait or adjust rate limits in main.py

#### 5. "Permission denied"
**Solution**: Ensure user has required role/permission

---

## 📞 Support & Security

### Report Security Issues
**DO NOT** open public issues for security vulnerabilities.
Contact: security@yourdomain.com

### Regular Security Audits
- Review access logs monthly
- Update dependencies quarterly
- Rotate secrets annually
- Penetration testing annually

---

## ✅ Post-Deployment Checklist

- [ ] SECRET_KEY is strong and unique
- [ ] DEBUG=False in production
- [ ] HTTPS is enabled and enforced
- [ ] Database backups are automated
- [ ] Monitoring is configured
- [ ] Error tracking is set up
- [ ] Firewall rules are configured
- [ ] Rate limiting is tested
- [ ] CORS origins are correct
- [ ] Admin user password is changed
- [ ] Documentation is updated
- [ ] Team is trained on security practices

---

**Your application is now secure and production-ready! 🎉**
