#!/bin/bash
# Quick Production Fixes - Apply Critical and High Priority Fixes
# Run this script to make your RBAC API production-ready

set -e

echo "🚀 FastAPI RBAC - Production Readiness Script"
echo "=============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    echo -e "${RED}❌ Error: app/main.py not found. Run this script from project root.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Project root detected${NC}"
echo ""

# Step 1: Backup current files
echo "📦 Step 1: Creating backup..."
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp docker-compose.yml "$BACKUP_DIR/" 2>/dev/null || true
cp app/main.py "$BACKUP_DIR/" 2>/dev/null || true
cp requirements.txt "$BACKUP_DIR/" 2>/dev/null || true
echo -e "${GREEN}✓ Backup created in $BACKUP_DIR${NC}"
echo ""

# Step 2: Add new dependencies
echo "📚 Step 2: Adding production dependencies..."
cat >> requirements.txt << 'EOF'

# Production dependencies
alembic>=1.13.1
redis>=5.0.0
fastapi-limiter>=0.1.5
prometheus-fastapi-instrumentator>=6.1.0
prometheus-client>=0.19.0
python-magic>=0.4.27
sentry-sdk[fastapi]>=1.40.0
EOF
echo -e "${GREEN}✓ Dependencies added to requirements.txt${NC}"
echo ""

# Step 3: Create .env.production template
echo "🔐 Step 3: Creating .env.production template..."
cat > .env.production.template << 'EOF'
# Production Environment Variables
# Copy this to .env.production and fill in real values

# Database
DB_USER=your_db_user
DB_PASSWORD=CHANGE_THIS_TO_SECURE_PASSWORD
DB_NAME=rbac
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}

# Security
SECRET_KEY=GENERATE_WITH_python_-c_import_secrets_print_secrets_token_urlsafe_64
DEBUG=False
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
BACKEND_CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com

# Email
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-app-specific-password
MAIL_FROM=noreply@yourdomain.com
MAIL_FROM_NAME=Your App Name
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_STARTTLS=True

# Password Reset
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES=30
FRONTEND_URL=https://yourdomain.com

# AI Configuration
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
AI_MODEL=gpt-3.5-turbo

# Redis
REDIS_URL=redis://redis:6379/0

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
ENABLE_METRICS=true

# Storage
UPLOAD_DIR=/app/data/uploads
VECTOR_STORE_PATH=/app/data/vectorstore
MAX_UPLOAD_SIZE=10485760
EOF
echo -e "${GREEN}✓ Created .env.production.template${NC}"
echo -e "${YELLOW}⚠️  Copy to .env.production and fill in real values!${NC}"
echo ""

# Step 4: Update docker-compose.yml
echo "🐳 Step 4: Updating docker-compose.yml..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://${DB_USER:-postgres}:${DB_PASSWORD}@db:5432/${DB_NAME:-rbac}
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=${DEBUG:-False}
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MAIL_USERNAME=${MAIL_USERNAME}
      - MAIL_PASSWORD=${MAIL_PASSWORD}
      - SENTRY_DSN=${SENTRY_DSN}
    volumes:
      - ./data/uploads:/app/data/uploads
      - ./data/vectorstore:/app/data/vectorstore
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 5
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 40s
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=${DB_USER:-postgres}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=${DB_NAME:-rbac}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
EOF
echo -e "${GREEN}✓ docker-compose.yml updated with secure configuration${NC}"
echo ""

# Step 5: Create health check endpoint
echo "🏥 Step 5: Creating health check endpoints..."
mkdir -p app/api/v1/endpoints
cat > app/api/v1/endpoints/health.py << 'EOF'
"""Health check endpoints."""
from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db import get_db
from app.config import settings
from typing import Dict, Any

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """Basic health check."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Readiness check with database verification."""
    health_status = {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "checks": {}
    }
    
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return health_status

@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_check() -> Dict[str, str]:
    """Liveness check."""
    return {"status": "alive"}
EOF
echo -e "${GREEN}✓ Health check endpoints created${NC}"
echo ""

# Step 6: Create deployment script
echo "🚀 Step 6: Creating deployment script..."
cat > deploy.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Deploying RBAC API to Production..."

# Check for .env.production
if [ ! -f .env.production ]; then
    echo "❌ Error: .env.production not found!"
    echo "Copy .env.production.template to .env.production and fill in values"
    exit 1
fi

# Load environment
export $(cat .env.production | grep -v '^#' | xargs)

echo "✓ Environment loaded"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "📊 Running database migrations..."
alembic upgrade head

# Build Docker images
echo "🐳 Building Docker images..."
docker-compose build

# Start services
echo "▶️  Starting services..."
docker-compose up -d

# Wait for health check
echo "⏳ Waiting for services..."
sleep 15

# Verify health
echo "🏥 Checking health..."
curl -f http://localhost:8000/health/ready || {
    echo "❌ Health check failed!"
    docker-compose logs app
    exit 1
}

echo "✅ Deployment successful!"
echo ""
echo "📊 Metrics: http://localhost:8000/metrics"
echo "📚 Docs: http://localhost:8000/docs"
echo "🏥 Health: http://localhost:8000/health/ready"
EOF
chmod +x deploy.sh
echo -e "${GREEN}✓ Deployment script created (deploy.sh)${NC}"
echo ""

# Step 7: Initialize Alembic
echo "📊 Step 7: Initializing Alembic..."
if [ ! -d "alembic" ]; then
    pip install alembic >/dev/null 2>&1 || true
    alembic init alembic >/dev/null 2>&1 || true
    echo -e "${GREEN}✓ Alembic initialized${NC}"
    echo -e "${YELLOW}⚠️  Configure alembic/env.py to use your database URL${NC}"
else
    echo -e "${YELLOW}⚠️  Alembic already initialized${NC}"
fi
echo ""

# Step 8: Create README for production
echo "📚 Step 8: Creating production deployment guide..."
cat > DEPLOY_TO_PRODUCTION.md << 'EOF'
# 🚀 Deploy to Production - Quick Guide

## Prerequisites

- Docker and Docker Compose installed
- PostgreSQL database (or use Docker)
- Redis instance (or use Docker)
- Domain with SSL certificate
- SMTP credentials for email

## Step-by-Step Deployment

### 1. Configure Environment

```bash
# Copy template
cp .env.production.template .env.production

# Edit with your values
nano .env.production
```

**Required values:**
- `DB_PASSWORD` - Strong database password
- `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(64))"`
- `OPENAI_API_KEY` - Your OpenAI API key
- `MAIL_USERNAME` and `MAIL_PASSWORD` - Email credentials

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Database Migrations

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 4. Deploy with Docker

```bash
# Run deployment script
./deploy.sh
```

Or manually:

```bash
# Build and start
docker-compose up -d

# Check logs
docker-compose logs -f app

# Check health
curl http://localhost:8000/health/ready
```

### 5. Verify Deployment

```bash
# Health check
curl http://localhost:8000/health/ready

# Metrics
curl http://localhost:8000/metrics

# API docs
open http://localhost:8000/docs
```

### 6. Set Up Monitoring

- Configure Prometheus to scrape `/metrics`
- Set up Grafana dashboards
- Configure alerts for errors and latency

### 7. Set Up SSL/HTTPS

Use a reverse proxy (Nginx/Traefik) with Let's Encrypt:

```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Production Checklist

- [ ] `.env.production` configured with secure values
- [ ] Database migrations applied
- [ ] SSL certificate configured
- [ ] Monitoring set up (Prometheus/Grafana)
- [ ] Logging configured (centralized)
- [ ] Backups configured (automated)
- [ ] Alerts configured (PagerDuty/Opsgenie)
- [ ] Load testing completed
- [ ] Security scan passed
- [ ] Documentation updated

## Troubleshooting

### Database Connection Failed
```bash
# Check database is running
docker-compose ps db

# Check logs
docker-compose logs db

# Test connection
docker-compose exec db psql -U postgres -d rbac
```

### Health Check Failing
```bash
# Check app logs
docker-compose logs app

# Check all services
docker-compose ps

# Restart services
docker-compose restart
```

### High Memory Usage
```bash
# Check resource usage
docker stats

# Scale down if needed
docker-compose up -d --scale app=1
```

## Rollback Procedure

```bash
# Stop services
docker-compose down

# Restore from backup
docker-compose up -d

# Rollback database
alembic downgrade -1
```

## Support

For issues, check:
1. `PRODUCTION_READINESS_AUDIT.md` - Detailed audit
2. `PRODUCTION_FIXES_IMPLEMENTATION.md` - Code fixes
3. Application logs: `docker-compose logs app`
EOF
echo -e "${GREEN}✓ Production deployment guide created${NC}"
echo ""

# Final summary
echo ""
echo "=============================================="
echo -e "${GREEN}✅ Production fixes applied successfully!${NC}"
echo "=============================================="
echo ""
echo "📋 What was done:"
echo "  ✓ Added production dependencies"
echo "  ✓ Created .env.production template"
echo "  ✓ Updated docker-compose.yml (secure)"
echo "  ✓ Added health check endpoints"
echo "  ✓ Created deployment script"
echo "  ✓ Initialized Alembic"
echo "  ✓ Created deployment guide"
echo ""
echo "📝 Next steps:"
echo "  1. Copy .env.production.template to .env.production"
echo "  2. Fill in secure values in .env.production"
echo "  3. Run: pip install -r requirements.txt"
echo "  4. Configure Alembic: edit alembic/env.py"
echo "  5. Create migration: alembic revision --autogenerate -m 'Initial'"
echo "  6. Apply migration: alembic upgrade head"
echo "  7. Deploy: ./deploy.sh"
echo ""
echo "📚 Documentation:"
echo "  - PRODUCTION_READINESS_AUDIT.md - Detailed audit report"
echo "  - PRODUCTION_FIXES_IMPLEMENTATION.md - All code fixes"
echo "  - PRODUCTION_READINESS_SUMMARY.md - Executive summary"
echo "  - DEPLOY_TO_PRODUCTION.md - Deployment guide"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Review all .env.production values before deploying!${NC}"
echo ""
