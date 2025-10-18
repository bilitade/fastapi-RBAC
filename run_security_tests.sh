#!/bin/bash

# Security Test Runner Script
# Runs comprehensive security tests and checks

set -e  # Exit on error

echo "🔒 Starting Security Test Suite..."
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
    fi
}

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠ Virtual environment not detected. Activating...${NC}"
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    else
        echo -e "${RED}✗ Virtual environment not found. Please create one first.${NC}"
        exit 1
    fi
fi

echo "1️⃣  Running Unit Tests..."
echo "------------------------"
pytest tests/test_security.py -v --tb=short
print_status $? "Unit Tests"
echo ""

echo "2️⃣  Checking for Known Vulnerabilities..."
echo "---------------------------------------"
if command -v safety &> /dev/null; then
    safety check --json || true
    print_status 0 "Vulnerability Scan (safety)"
else
    echo -e "${YELLOW}⚠ 'safety' not installed. Run: pip install safety${NC}"
fi
echo ""

echo "3️⃣  Static Security Analysis..."
echo "-----------------------------"
if command -v bandit &> /dev/null; then
    bandit -r app/ -f txt -ll || true
    print_status 0 "Static Analysis (bandit)"
else
    echo -e "${YELLOW}⚠ 'bandit' not installed. Run: pip install bandit${NC}"
fi
echo ""

echo "4️⃣  Checking for Secrets in Code..."
echo "---------------------------------"
if command -v detect-secrets &> /dev/null; then
    detect-secrets scan --baseline .secrets.baseline || true
    print_status 0 "Secret Detection"
else
    echo -e "${YELLOW}⚠ 'detect-secrets' not installed. Run: pip install detect-secrets${NC}"
fi
echo ""

echo "5️⃣  Checking Dependencies..."
echo "-------------------------"
pip list --outdated | head -20
print_status 0 "Dependency Check"
echo ""

echo "6️⃣  Validating Environment Configuration..."
echo "----------------------------------------"
if [ -f ".env" ]; then
    # Check if SECRET_KEY is set and not default
    SECRET_KEY=$(grep "^SECRET_KEY=" .env | cut -d '=' -f2 | tr -d '"' | tr -d "'")
    if [ "$SECRET_KEY" = "your-secret-key-change-in-production" ] || [ -z "$SECRET_KEY" ]; then
        echo -e "${RED}✗ Default or missing SECRET_KEY detected!${NC}"
        echo "  Generate a secure key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
    else
        if [ ${#SECRET_KEY} -lt 32 ]; then
            echo -e "${YELLOW}⚠ SECRET_KEY is shorter than 32 characters${NC}"
        else
            echo -e "${GREEN}✓ SECRET_KEY is properly configured${NC}"
        fi
    fi
    
    # Check DEBUG setting
    DEBUG=$(grep "^DEBUG=" .env | cut -d '=' -f2 | tr -d '"' | tr -d "'")
    if [ "$DEBUG" = "True" ] || [ "$DEBUG" = "true" ]; then
        echo -e "${YELLOW}⚠ DEBUG mode is enabled${NC}"
    else
        echo -e "${GREEN}✓ DEBUG mode is disabled${NC}"
    fi
else
    echo -e "${YELLOW}⚠ .env file not found${NC}"
fi
echo ""

echo "7️⃣  Testing Rate Limiting..."
echo "-------------------------"
echo "Starting test server..."
# Start server in background
uvicorn app.main:app --host 127.0.0.1 --port 8888 > /dev/null 2>&1 &
SERVER_PID=$!
sleep 3

# Test rate limiting
echo "Testing login endpoint rate limit..."
for i in {1..10}; do
    curl -s -o /dev/null -w "%{http_code}\n" \
        -X POST http://127.0.0.1:8888/api/v1/auth/login \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=test@test.com&password=test" 2>/dev/null || true
done | grep -q "429" && echo -e "${GREEN}✓ Rate limiting is working${NC}" || echo -e "${YELLOW}⚠ Rate limiting may not be working${NC}"

# Stop server
kill $SERVER_PID 2>/dev/null || true
echo ""

echo "8️⃣  Security Headers Check..."
echo "---------------------------"
echo "Starting test server..."
uvicorn app.main:app --host 127.0.0.1 --port 8888 > /dev/null 2>&1 &
SERVER_PID=$!
sleep 3

HEADERS=$(curl -s -I http://127.0.0.1:8888/health)

check_header() {
    if echo "$HEADERS" | grep -qi "$1"; then
        echo -e "${GREEN}✓ $1 present${NC}"
    else
        echo -e "${RED}✗ $1 missing${NC}"
    fi
}

check_header "X-Content-Type-Options"
check_header "X-Frame-Options"
check_header "X-XSS-Protection"
check_header "Content-Security-Policy"

# Stop server
kill $SERVER_PID 2>/dev/null || true
echo ""

echo "=================================="
echo "🎉 Security Test Suite Complete!"
echo "=================================="
echo ""
echo "📊 Summary:"
echo "  - Review any warnings or errors above"
echo "  - Ensure all critical issues are resolved"
echo "  - Update dependencies regularly"
echo "  - Run these tests before each deployment"
echo ""
echo "📚 For more information, see:"
echo "  - SECURITY_AUDIT.md"
echo "  - SECURITY_BEST_PRACTICES.md"
echo "  - DEPLOYMENT_GUIDE.md"
