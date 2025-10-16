#!/bin/bash

# RBAC System Quick Start Script
# This script helps you get started quickly

set -e

echo "=========================================="
echo "RBAC System - Quick Start"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${RED}⚠ IMPORTANT: Edit .env file with your configuration!${NC}"
    echo -e "${RED}  Especially change SECRET_KEY and DATABASE_URL${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Ask if user wants to initialize database
echo ""
read -p "Do you want to initialize the database now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Initializing database...${NC}"
    python3 -m app.scripts.init_db
    echo -e "${GREEN}✓ Database initialized${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Start the server:"
echo "   ${YELLOW}source .venv/bin/activate${NC}"
echo "   ${YELLOW}uvicorn app.main:app --reload${NC}"
echo ""
echo "3. Access the API:"
echo "   - Swagger UI: http://localhost:8000/docs"
echo "   - ReDoc: http://localhost:8000/redoc"
echo ""
echo "Default login credentials:"
echo "   - Email: admin@example.com"
echo "   - Password: Admin123!"
echo ""
echo "For more information, see README.md and USAGE_GUIDE.md"
echo "=========================================="

