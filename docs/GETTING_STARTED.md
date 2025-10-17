# 🚀 Getting Started - AI-Powered RBAC System

## Quick Start (5 Minutes)

### Step 1: Install Dependencies
```bash
cd /home/bilisuma/Desktop/RBAC
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
cp .env.example .env
nano .env  # Add your OPENAI_API_KEY
```

### Step 3: Initialize Database
```bash
python -m app.scripts.init_db
```

### Step 4: Index Documents (Optional - for AI search)
```bash
python -m app.scripts.index_documents ./docs
```

### Step 5: Start Server
```bash
uvicorn app.main:app --reload
```

### Step 6: Explore!
- **Swagger UI**: http://localhost:8000/docs
- **AI Assistant**: http://localhost:8000/docs#AI%20Assistant

## 🎯 Test the System

### 1. Register a User
```bash
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "middle_name": "M",
    "last_name": "Doe",
    "role_title": "Developer",
    "email": "john@test.com",
    "password": "Test123!"
  }'
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "username=john@test.com&password=Test123!"
```

### 3. Chat with AI (if API key configured)
```bash
curl -X POST "http://localhost:8000/api/v1/ai/chat" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Generate ideas for a task management app"}'
```

## 📚 Documentation

- **[Main README](README.md)** - Full overview
- **[docs/README.md](docs/README.md)** - Documentation index
- **[docs/AI_SETUP.md](docs/AI_SETUP.md)** - AI setup guide
- **[docs/API_EXAMPLES.md](docs/API_EXAMPLES.md)** - API examples

## ✅ You're Ready!

Your AI-powered RBAC system is running! 🎉

---

**Need help?** Check the [documentation](docs/README.md)
