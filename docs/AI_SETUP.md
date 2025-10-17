# AI Assistant Setup Guide

## 🚀 Quick Setup (5 Minutes)

### Step 1: Install Dependencies

```bash
cd /home/bilisuma/Desktop/RBAC
source .venv/bin/activate
pip install -r requirements.txt
```

This installs:
- LangChain and LangChain integrations
- OpenAI and Anthropic clients
- ChromaDB for vector storage
- Document processing libraries

### Step 2: Configure API Key

Add to your `.env` file:

```bash
# For OpenAI (Recommended)
AI_PROVIDER="openai"
OPENAI_API_KEY="sk-your-openai-api-key-here"
AI_MODEL="gpt-3.5-turbo"

# Or for Anthropic
# AI_PROVIDER="anthropic"
# ANTHROPIC_API_KEY="sk-ant-your-key-here"
# AI_MODEL="claude-3-sonnet-20240229"

# AI Settings
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=1000

# Vector Store
VECTOR_STORE_PATH="./data/vectorstore"
EMBEDDING_MODEL="text-embedding-ada-002"
```

### Step 3: Index Documents (Optional)

```bash
# Index your documentation for AI search
python -m app.scripts.index_documents ./docs
```

### Step 4: Start Server

```bash
uvicorn app.main:app --reload
```

### Step 5: Test AI Features

Visit: http://localhost:8000/docs

Navigate to **AI Assistant** section and try:
- `/api/v1/ai/chat` - Chat with AI
- `/api/v1/ai/generate-idea` - Generate ideas
- `/api/v1/ai/enhance-content` - Improve content

## 🔑 Get API Keys

### OpenAI
1. Go to https://platform.openai.com/
2. Sign up / Login
3. Navigate to API Keys
4. Create new secret key
5. Copy and add to `.env`

### Anthropic
1. Go to https://console.anthropic.com/
2. Sign up / Login
3. Get API key
4. Copy and add to `.env`

## 📊 Test Commands

### 1. Test Chat
```bash
curl -X POST "http://localhost:8000/api/v1/ai/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! Can you help me?"
  }'
```

### 2. Generate Ideas
```bash
curl -X POST "http://localhost:8000/api/v1/ai/generate-idea" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Mobile app features",
    "style": "professional"
  }'
```

### 3. Enhance Content
```bash
curl -X POST "http://localhost:8000/api/v1/ai/enhance-content" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Our product is good.",
    "enhancement_type": "expand"
  }'
```

### 4. Auto-Fill Suggestion
```bash
curl -X POST "http://localhost:8000/api/v1/ai/auto-fill" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "field_name": "bio",
    "existing_data": {
      "first_name": "John",
      "last_name": "Doe",
      "role_title": "Developer"
    }
  }'
```

## 🔧 Configuration Options

### Model Selection

**GPT-3.5 Turbo** (Recommended for most use cases)
- Fast responses
- Cost-effective
- Good quality

```bash
AI_MODEL="gpt-3.5-turbo"
```

**GPT-4** (Best quality)
- Highest quality responses
- More expensive
- Slower

```bash
AI_MODEL="gpt-4"
```

**Claude 3** (Alternative)
- Great for longer context
- Different AI personality
- Competitive pricing

```bash
AI_PROVIDER="anthropic"
AI_MODEL="claude-3-sonnet-20240229"
```

### Temperature Control

```bash
AI_TEMPERATURE=0.0   # Deterministic, factual
AI_TEMPERATURE=0.7   # Balanced (recommended)
AI_TEMPERATURE=1.5   # Creative, varied
```

### Token Limits

```bash
AI_MAX_TOKENS=500    # Short responses
AI_MAX_TOKENS=1000   # Medium (recommended)
AI_MAX_TOKENS=2000   # Long, detailed
```

## 📁 Project Structure

```
app/ai/
├── config.py                  # LLM configuration
├── services/
│   ├── llm_factory.py        # Provider-agnostic LLM factory
│   ├── chat_service.py       # Chat functionality
│   ├── content_service.py    # Content generation
│   ├── document_service.py   # Document RAG
│   └── agent_service.py      # AI agent with tools
├── tools/
│   └── custom_tools.py       # Custom LangChain tools
└── chains/
    └── qa_chain.py           # Question-answering chain

app/api/v1/endpoints/
└── ai.py                     # AI API endpoints

app/schemas/
└── ai.py                     # AI request/response schemas

app/scripts/
└── index_documents.py        # Document indexing script
```

## 🎓 Best Practices

### 1. Secure Your API Keys
```bash
# Never commit .env to git
# Use environment variables in production
# Rotate keys regularly
```

### 2. Implement Rate Limiting
```python
# Prevent abuse and control costs
from slowapi import Limiter

@limiter.limit("10/minute")
@router.post("/ai/chat")
async def chat(...):
    pass
```

### 3. Monitor Usage
```python
# Track API calls
# Set usage budgets
# Alert on high usage
```

### 4. Cache Responses
```python
# Cache common queries
# Reduce API costs
# Faster responses
```

## 🚨 Troubleshooting

### Module Not Found: langchain
```bash
pip install -r requirements.txt
```

### AI Service Not Configured
Add API key to `.env`:
```bash
OPENAI_API_KEY="sk-..."
```

### Slow Responses
- Reduce `AI_MAX_TOKENS`
- Use faster model (gpt-3.5-turbo)
- Implement caching

### High Costs
- Set lower `AI_MAX_TOKENS`
- Implement rate limiting
- Use cheaper model
- Cache common requests

## ✅ Verification

Test if AI is working:

```bash
# 1. Check configuration loads
python -c "from app.config import settings; print(f'AI Provider: {settings.AI_PROVIDER}')"

# 2. Test imports
python -c "from app.ai.services.chat_service import ChatService; print('✓ AI services ready')"

# 3. Start server and check /docs
uvicorn app.main:app --reload
```

## 🎯 Next Steps

1. ✅ Get API key from OpenAI
2. ✅ Add to `.env` file
3. ✅ Install dependencies
4. ✅ Index your documents
5. ✅ Test endpoints via Swagger UI
6. ✅ Integrate into your application

---

**Ready to build AI-powered features!** 🤖

For detailed API usage, see: [AI_ASSISTANT.md](AI_ASSISTANT.md)

