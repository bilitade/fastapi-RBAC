```markdown
# AI Assistant - Complete Guide

## 🤖 Overview

Your RBAC system now includes a powerful **AI Assistant** built with LangChain that can:

✅ **Chat** - Intelligent conversations with context awareness  
✅ **Generate Ideas** - Creative brainstorming on any topic  
✅ **Enhance Content** - Improve, expand, or summarize text  
✅ **Auto-Fill** - Smart form field suggestions  
✅ **Search Documents** - Semantic search through your files  
✅ **Answer Questions** - Reference your documentation and data  

## 🎯 Key Features

### 1. **LLM-Agnostic Architecture**
- ✅ OpenAI (GPT-3.5, GPT-4)
- ✅ Anthropic (Claude)
- ✅ Easy to add more providers
- ✅ Switch providers via configuration

### 2. **LangChain Integration**
- ✅ Modular service layer
- ✅ Reusable chains
- ✅ Custom tools
- ✅ Agent executor

### 3. **Document RAG (Retrieval Augmented Generation)**
- ✅ Vector store (ChromaDB)
- ✅ Semantic search
- ✅ PDF, TXT, Markdown support
- ✅ Context-aware answers

### 4. **Production-Ready**
- ✅ Type-safe with Pydantic
- ✅ FastAPI standards
- ✅ Error handling
- ✅ Async support

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /home/bilisuma/Desktop/RBAC
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure AI Provider

Edit `.env`:
```bash
# OpenAI (recommended)
AI_PROVIDER="openai"
OPENAI_API_KEY="sk-your-api-key-here"
AI_MODEL="gpt-3.5-turbo"

# Or Anthropic
# AI_PROVIDER="anthropic"
# ANTHROPIC_API_KEY="your-anthropic-key"
# AI_MODEL="claude-3-sonnet-20240229"

# AI Settings
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=1000
```

### 3. Index Your Documents (Optional)

```bash
# Index documentation for AI search
python -m app.scripts.index_documents ./docs
```

### 4. Start Server

```bash
uvicorn app.main:app --reload
```

### 5. Access AI Endpoints

Visit: http://localhost:8000/docs#AI%20Assistant

## 📡 API Endpoints

### Chat with AI

```bash
POST /api/v1/ai/chat

{
  "message": "How can I improve my product description?",
  "context": {
    "product": "Task management app",
    "audience": "remote teams"
  }
}
```

**Response:**
```json
{
  "response": "Here are some ideas to improve your product description...",
  "model": "gpt-3.5-turbo"
}
```

### Generate Ideas

```bash
POST /api/v1/ai/generate-idea

{
  "topic": "New features for mobile app",
  "context": "E-commerce platform for small businesses",
  "style": "professional"
}
```

**Response:**
```json
{
  "result": "1. One-click checkout...\n2. Inventory management...",
  "model": "gpt-3.5-turbo"
}
```

### Enhance Content

```bash
POST /api/v1/ai/enhance-content

{
  "content": "Our app helps teams work better.",
  "enhancement_type": "expand",
  "target_length": "medium"
}
```

**Enhancement Types:**
- `improve` - Make content better
- `expand` - Add more details
- `summarize` - Make it shorter
- `professional` - Business tone
- `simplify` - Easier to understand

**Response:**
```json
{
  "result": "Our comprehensive application empowers teams...",
  "model": "gpt-3.5-turbo"
}
```

### Auto-Fill Suggestions

```bash
POST /api/v1/ai/auto-fill

{
  "field_name": "company_description",
  "existing_data": {
    "company_name": "TechStart Inc",
    "industry": "Software",
    "size": "50 employees",
    "location": "San Francisco"
  },
  "field_description": "Brief company overview"
}
```

**Response:**
```json
{
  "result": "TechStart Inc is a growing software company based in San Francisco with a team of 50 dedicated professionals.",
  "model": "gpt-3.5-turbo"
}
```

### Search Documents

```bash
POST /api/v1/ai/search-documents

{
  "query": "How to configure authentication?",
  "max_results": 5
}
```

**Response:**
```json
{
  "results": [
    {
      "content": "Authentication is configured in the .env file...",
      "source": "docs/USAGE_GUIDE.md"
    }
  ],
  "count": 1
}
```

### AI Agent (With Tools)

```bash
POST /api/v1/ai/agent

{
  "message": "How many users are in the system and what roles exist?",
  "context": {"task": "system_overview"}
}
```

**Response:**
```json
{
  "result": "The system has 5 users. Available roles are: superadmin, admin, normal.",
  "model": "gpt-3.5-turbo"
}
```

### List Available Models

```bash
GET /api/v1/ai/models
```

**Response:**
```json
{
  "provider": "openai",
  "current_model": "gpt-3.5-turbo",
  "available_models": [
    "gpt-4",
    "gpt-4-turbo-preview",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k"
  ]
}
```

## 🏗️ Architecture

```
app/ai/
├── config.py                 # LLM provider configuration
├── services/
│   ├── llm_factory.py       # Provider-agnostic LLM creation
│   ├── chat_service.py      # Chat conversations
│   ├── content_service.py   # Content generation
│   ├── document_service.py  # Document processing & RAG
│   └── agent_service.py     # AI agent with tools
├── tools/
│   └── custom_tools.py      # Custom LangChain tools
└── chains/
    └── qa_chain.py          # Question-answering chain
```

## 🔧 Configuration

### Switch LLM Provider

**OpenAI:**
```bash
AI_PROVIDER="openai"
OPENAI_API_KEY="sk-..."
AI_MODEL="gpt-3.5-turbo"  # or gpt-4
```

**Anthropic:**
```bash
AI_PROVIDER="anthropic"
ANTHROPIC_API_KEY="sk-ant-..."
AI_MODEL="claude-3-sonnet-20240229"
```

### Adjust AI Behavior

```bash
AI_TEMPERATURE=0.7      # 0.0 = deterministic, 2.0 = creative
AI_MAX_TOKENS=1000      # Response length limit
```

## 💡 Use Cases

### 1. Content Generation for Forms

```python
# Auto-fill company description
POST /ai/auto-fill
{
  "field_name": "bio",
  "existing_data": {
    "first_name": "John",
    "last_name": "Doe",
    "role_title": "Senior Developer"
  }
}
```

### 2. Help Users Write Better

```python
# Enhance user's draft
POST /ai/enhance-content
{
  "content": "I want to improve sales",
  "enhancement_type": "professional",
  "target_length": "medium"
}
```

### 3. Brainstorming Features

```python
# Generate feature ideas
POST /ai/generate-idea
{
  "topic": "User engagement features",
  "context": "Mobile fitness app",
  "style": "creative"
}
```

### 4. Knowledge Base Search

```python
# Search documentation
POST /ai/search-documents
{
  "query": "how to add new permissions",
  "max_results": 3
}
```

### 5. Interactive Chat

```python
# Natural conversation
POST /ai/chat
{
  "message": "What's the best way to structure my user roles?"
}
```

## 🎓 Integration Examples

### Frontend Integration

```javascript
// Chat with AI
async function chatWithAI(message) {
  const response = await fetch('/api/v1/ai/chat', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message })
  });
  
  const data = await response.json();
  return data.response;
}

// Auto-fill form field
async function getAutoFillSuggestion(fieldName, formData) {
  const response = await fetch('/api/v1/ai/auto-fill', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      field_name: fieldName,
      existing_data: formData
    })
  });
  
  const data = await response.json();
  return data.result;
}
```

### Python Integration

```python
from app.ai.services.chat_service import ChatService
from app.ai.services.content_service import ContentService

# Direct service usage
chat = ChatService()
response = await chat.chat("Hello!")

content = ContentService()
ideas = await content.generate_idea("AI features")
```

## 🔐 Security

### Authentication Required
All AI endpoints require valid JWT token:
```bash
Authorization: Bearer <access_token>
```

### Rate Limiting (Recommended)
Consider adding rate limiting to AI endpoints to control costs:

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/ai/chat")
@limiter.limit("10/minute")
async def chat(...):
    pass
```

### Cost Control
Monitor API usage and set limits:
- Max tokens per request
- User quotas
- Daily/monthly budgets

## 📊 Document Indexing

### Index Your Documentation

```bash
# Index docs folder
python -m app.scripts.index_documents ./docs

# Index custom directory
python -m app.scripts.index_documents /path/to/your/docs
```

### Supported File Types
- ✅ `.txt` - Text files
- ✅ `.md` - Markdown files
- ✅ `.pdf` - PDF documents

### Update Index
Re-run the indexing script when documents change:

```bash
# This will recreate the vector store
python -m app.scripts.index_documents ./docs
```

## 🎯 Extending the AI System

### Add Custom Tool

```python
# app/ai/tools/custom_tools.py

def my_custom_tool(input: str) -> str:
    """Your custom logic."""
    return f"Processed: {input}"

# In agent_service.py, add to tools:
Tool(
    name="my_tool",
    func=my_custom_tool,
    description="Description for AI to understand when to use this"
)
```

### Add New Chain

```python
# app/ai/chains/my_chain.py

from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate

class MyChain:
    def __init__(self):
        self.llm = LLMFactory.create_llm()
    
    async def process(self, input_data):
        prompt = PromptTemplate.from_template("Process: {input}")
        chain = prompt | self.llm
        return await chain.ainvoke({"input": input_data})
```

### Add New Endpoint

```python
# app/api/v1/endpoints/ai.py

@router.post("/my-ai-feature")
async def my_ai_feature(
    request: MyRequest,
    current_user: User = Depends(get_current_user)
):
    check_ai_configured()
    my_service = MyService()
    result = await my_service.process(request.data)
    return {"result": result}
```

## 🧪 Testing AI Features

### Using Swagger UI

1. Go to http://localhost:8000/docs
2. Authorize with your token
3. Navigate to "AI Assistant" section
4. Try different endpoints

### Using curl

```bash
# Get token first
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "username=admin@example.com&password=Admin123!" \
  | jq -r '.access_token')

# Chat with AI
curl -X POST "http://localhost:8000/api/v1/ai/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Generate ideas for improving user onboarding"
  }'
```

## 🎨 Customization

### Custom System Prompts

```json
{
  "message": "Help me write a product description",
  "system_prompt": "You are an expert marketing copywriter specializing in SaaS products. Write compelling, benefit-focused descriptions."
}
```

### Context-Aware Responses

```json
{
  "message": "What features should I add?",
  "context": {
    "product_type": "CRM",
    "target_audience": "sales teams",
    "current_users": 1000
  }
}
```

## 🔄 Provider Configuration

### OpenAI Models

```python
AI_MODEL options:
- "gpt-3.5-turbo"        # Fast, cost-effective
- "gpt-3.5-turbo-16k"    # Longer context
- "gpt-4"                # Most capable
- "gpt-4-turbo-preview"  # Latest GPT-4
```

### Anthropic Models

```python
AI_MODEL options:
- "claude-3-haiku-20240307"    # Fast, affordable
- "claude-3-sonnet-20240229"   # Balanced
- "claude-3-opus-20240229"     # Most capable
```

## 📋 Best Practices

### 1. Always Provide Context
```json
{
  "message": "Improve this",
  "context": {
    "industry": "healthcare",
    "audience": "medical professionals"
  }
}
```

### 2. Use Specific Enhancement Types
```json
{
  "content": "...",
  "enhancement_type": "professional",  // Not just "improve"
  "target_length": "short"
}
```

### 3. Index Relevant Documents
```bash
# Keep vector store updated
python -m app.scripts.index_documents ./docs
```

### 4. Monitor Costs
- Set reasonable max_tokens
- Implement rate limiting
- Track API usage

## 🚨 Error Handling

### AI Not Configured
```json
{
  "detail": "AI service not configured. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY."
}
```

**Solution:** Add API key to `.env`

### No Documents Indexed
```json
{
  "answer": "No documents indexed. Please index documents first."
}
```

**Solution:** Run `python -m app.scripts.index_documents ./docs`

### Rate Limit Exceeded
```json
{
  "detail": "Rate limit exceeded"
}
```

**Solution:** Wait or upgrade your OpenAI plan

## 🎯 Use as Boilerplate

This AI system is designed to be reusable for any project:

### 1. Copy AI Module
```bash
cp -r app/ai /your-project/app/
cp -r app/api/v1/endpoints/ai.py /your-project/app/api/v1/endpoints/
```

### 2. Update Configuration
```bash
# Add to your .env
AI_PROVIDER="openai"
OPENAI_API_KEY="your-key"
```

### 3. Customize for Your Domain
```python
# Modify prompts in content_service.py
# Add custom tools in custom_tools.py
# Create domain-specific chains
```

### 4. Index Your Documents
```bash
python -m app.scripts.index_documents /your/docs
```

## 📊 Service Layer Architecture

### LLMFactory
```python
# Provider-agnostic LLM creation
llm = LLMFactory.create_llm()
# Automatically uses configured provider
```

### ChatService
```python
# Conversational AI
chat = ChatService()
response = await chat.chat("Hello!")
```

### ContentService
```python
# Content generation & enhancement
content = ContentService()
ideas = await content.generate_idea("topic")
enhanced = await content.enhance_content("text")
suggestion = await content.auto_fill_suggestion("field", data)
```

### DocumentService
```python
# Document processing & RAG
docs = DocumentService()
documents = docs.load_documents("./docs")
vector_store = docs.create_vector_store(documents)
results = await docs.search_documents("query")
```

### AgentService
```python
# AI agent with tools
agent = AgentService()
result = await agent.execute("complex query")
```

## 🔗 Integration Patterns

### Pattern 1: Simple Chat
```python
@router.post("/help")
async def get_help(question: str, user: User = Depends(get_current_user)):
    chat = ChatService()
    return await chat.chat(question)
```

### Pattern 2: Content Enhancement
```python
@router.post("/posts/{id}/improve")
async def improve_post(id: int, user: User = Depends(get_current_user)):
    post = get_post(id)
    content = ContentService()
    improved = await content.enhance_content(post.content)
    return {"improved_content": improved}
```

### Pattern 3: Smart Forms
```python
@router.post("/forms/suggest")
async def suggest_field(field: str, data: dict):
    content = ContentService()
    suggestion = await content.auto_fill_suggestion(field, data)
    return {"suggestion": suggestion}
```

### Pattern 4: Knowledge Base
```python
@router.get("/kb/search")
async def search_kb(query: str):
    docs = DocumentService()
    results = await docs.search_documents(query)
    return {"results": results}
```

## ✅ Summary

Your RBAC system now includes:

✅ **Complete AI assistant** with LangChain  
✅ **Multi-LLM support** (OpenAI, Anthropic, extensible)  
✅ **RAG system** for document search  
✅ **Content generation** and enhancement  
✅ **Auto-fill** intelligent suggestions  
✅ **Production-ready** with proper structure  
✅ **Reusable** as boilerplate for future projects  

**Your system is now AI-powered and ready for intelligent features!** 🚀

---

**API Documentation**: http://localhost:8000/docs#AI%20Assistant
**Need help?** Check the interactive Swagger UI for examples
```

