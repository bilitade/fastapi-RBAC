# Using AI Module as Boilerplate

## 🎯 Overview

The AI module is designed to be **reusable** for any future AI-powered project.

## 📦 What You Get

### Complete AI Infrastructure
- ✅ LLM factory (OpenAI, Anthropic, extensible)
- ✅ Chat service with conversation history
- ✅ Content generation service
- ✅ Document processing & RAG
- ✅ AI agent with custom tools
- ✅ Pre-built API endpoints
- ✅ Pydantic schemas
- ✅ Type-safe throughout

## 🚀 Use in New Projects

### Option 1: Copy Entire AI Module

```bash
# Copy to new project
cp -r RBAC/app/ai /your-project/app/
cp -r RBAC/app/api/v1/endpoints/ai.py /your-project/app/api/v1/endpoints/
cp -r RBAC/app/schemas/ai.py /your-project/app/schemas/
cp -r RBAC/app/scripts/index_documents.py /your-project/app/scripts/

# Add to requirements.txt
langchain>=0.1.0
langchain-openai>=0.0.5
chromadb>=0.4.22
openai>=1.12.0

# Configure .env
OPENAI_API_KEY="your-key"
AI_MODEL="gpt-3.5-turbo"
```

### Option 2: Copy Specific Services

```bash
# Just chat functionality
cp app/ai/services/llm_factory.py /your-project/
cp app/ai/services/chat_service.py /your-project/

# Just content generation
cp app/ai/services/content_service.py /your-project/

# Just document search
cp app/ai/services/document_service.py /your-project/
```

## 🎨 Customization Examples

### 1. Add Custom LLM Provider

```python
# app/ai/services/llm_factory.py

from langchain_google_genai import ChatGoogleGenerativeAI

class LLMFactory:
    @staticmethod
    def create_llm(config):
        # ... existing code ...
        
        elif config.provider == "google":
            return ChatGoogleGenerativeAI(
                model=config.model,
                temperature=config.temperature,
                api_key=config.api_key
            )
```

### 2. Add Domain-Specific Tool

```python
# app/ai/tools/custom_tools.py

def analyze_sales_data(query: str) -> str:
    """Analyze sales data from database."""
    # Your custom logic
    return result

# Add to agent tools:
Tool(
    name="analyze_sales",
    func=analyze_sales_data,
    description="Analyze sales data and provide insights"
)
```

### 3. Create Custom Chain

```python
# app/ai/chains/summary_chain.py

from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate

class SummaryChain:
    def __init__(self):
        self.llm = LLMFactory.create_llm()
        
        self.prompt = PromptTemplate.from_template(
            "Summarize the following {doc_type}:\n\n{content}\n\nSummary:"
        )
    
    async def summarize(self, content: str, doc_type: str = "document"):
        chain = self.prompt | self.llm
        result = await chain.ainvoke({
            "content": content,
            "doc_type": doc_type
        })
        return result.content
```

### 4. Add Custom Endpoint

```python
# app/api/v1/endpoints/ai.py

@router.post("/analyze-code")
async def analyze_code(
    code: str,
    current_user: User = Depends(get_current_user)
):
    """Analyze code quality and suggest improvements."""
    check_ai_configured()
    
    # Use content service or create custom chain
    content_service = ContentService()
    
    prompt = f"Analyze this code and suggest improvements:\n\n{code}"
    result = await content_service.enhance_content(
        content=code,
        enhancement_type="improve"
    )
    
    return {"analysis": result, "model": settings.AI_MODEL}
```

## 🎯 Common Patterns

### Pattern 1: Simple AI Endpoint

```python
from app.ai.services.chat_service import ChatService

@router.post("/ai-help")
async def ai_help(question: str, user: User = Depends(get_current_user)):
    chat = ChatService()
    response = await chat.chat(question)
    return {"answer": response}
```

### Pattern 2: Content Processing

```python
from app.ai.services.content_service import ContentService

@router.post("/improve-description")
async def improve_description(
    product_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    
    content_service = ContentService()
    improved = await content_service.enhance_content(
        content=product.description,
        enhancement_type="professional"
    )
    
    return {"improved": improved}
```

### Pattern 3: Document-Based Answers

```python
from app.ai.chains.qa_chain import QAChain

@router.get("/docs/ask")
async def ask_documentation(question: str):
    qa_chain = QAChain()
    result = await qa_chain.answer_question(question)
    return result
```

### Pattern 4: Smart Form Fields

```python
@router.post("/forms/smart-fill")
async def smart_fill(
    field_name: str,
    form_data: Dict[str, Any]
):
    content_service = ContentService()
    suggestion = await content_service.auto_fill_suggestion(
        field_name=field_name,
        existing_data=form_data
    )
    return {"suggestion": suggestion}
```

## 🔌 Service Layer Usage

### Direct Service Usage (No HTTP)

```python
# In your business logic
from app.ai.services.chat_service import ChatService
from app.ai.services.content_service import ContentService

async def process_user_input(user_text: str):
    # Generate ideas
    content = ContentService()
    ideas = await content.generate_idea(user_text)
    
    # Enhance content
    enhanced = await content.enhance_content(user_text)
    
    # Chat
    chat = ChatService()
    response = await chat.chat(user_text)
    
    return {
        "ideas": ideas,
        "enhanced": enhanced,
        "chat_response": response
    }
```

## 🎓 Advanced Patterns

### 1. Custom AI Agent with Tools

```python
from langchain.agents import AgentExecutor, create_openai_functions_agent
from app.ai.services.llm_factory import LLMFactory

class MyCustomAgent:
    def __init__(self):
        self.llm = LLMFactory.create_llm()
        self.tools = self.create_custom_tools()
    
    def create_custom_tools(self):
        return [
            Tool(name="my_tool", func=my_function, description="...")
        ]
    
    async def execute(self, query: str):
        agent = create_openai_functions_agent(
            self.llm,
            self.tools,
            prompt
        )
        executor = AgentExecutor(agent=agent, tools=self.tools)
        return await executor.ainvoke({"input": query})
```

### 2. RAG with Custom Documents

```python
from app.ai.services.document_service import DocumentService

# Index your specific documents
doc_service = DocumentService()
docs = doc_service.load_documents("/your/docs")
vector_store = doc_service.create_vector_store(
    docs,
    persist_directory="./custom_vectorstore"
)

# Search later
results = await doc_service.search_documents(
    "your query",
    vector_store=vector_store
)
```

### 3. Streaming Responses

```python
from langchain_core.callbacks import AsyncCallbackHandler

class StreamingHandler(AsyncCallbackHandler):
    async def on_llm_new_token(self, token: str, **kwargs):
        # Stream token to client
        yield token

# Use with streaming endpoint
@router.post("/ai/chat-stream")
async def chat_stream(...):
    # Implement streaming response
    pass
```

## ✅ Module Features

### LLM-Agnostic
```python
# Switch provider in .env, code stays the same
AI_PROVIDER="openai"   # or "anthropic"
# No code changes needed!
```

### Type-Safe
```python
# Full type hints throughout
async def chat(message: str, context: Optional[Dict[str, Any]] = None) -> str:
    pass
```

### Async Support
```python
# All services are async
response = await chat_service.chat(message)
ideas = await content_service.generate_idea(topic)
```

### Error Handling
```python
# Graceful error handling
try:
    response = await ai_service.process(input)
except Exception as e:
    # Handle AI errors appropriately
    pass
```

## 📊 Cost Optimization

### 1. Use Appropriate Models

```python
# Fast & cheap for simple tasks
AI_MODEL="gpt-3.5-turbo"

# Best quality for complex tasks
AI_MODEL="gpt-4"
```

### 2. Limit Token Usage

```python
AI_MAX_TOKENS=500   # Shorter responses = lower cost
```

### 3. Implement Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_response(query: str):
    # Cache common queries
    pass
```

### 4. Batch Processing

```python
# Process multiple items in one call
items = ["item1", "item2", "item3"]
results = await process_batch(items)
```

## ✅ Checklist for New Projects

When using this AI module in a new project:

- [ ] Copy `app/ai/` module
- [ ] Copy AI endpoints from `api/v1/endpoints/ai.py`
- [ ] Copy AI schemas from `schemas/ai.py`
- [ ] Add AI settings to your config
- [ ] Install requirements: `pip install langchain langchain-openai openai chromadb`
- [ ] Add API key to `.env`
- [ ] Customize prompts for your domain
- [ ] Add domain-specific tools
- [ ] Index your documents
- [ ] Test endpoints
- [ ] Implement rate limiting
- [ ] Monitor usage and costs

## 🎉 Summary

The AI module provides:

✅ **Complete AI infrastructure** ready to use  
✅ **Multi-provider support** (OpenAI, Anthropic)  
✅ **LangChain best practices** implemented  
✅ **Type-safe** with Pydantic  
✅ **FastAPI standards** followed  
✅ **Extensible** architecture  
✅ **Production-ready** error handling  
✅ **Reusable** as boilerplate  

**Copy this module to any project and have AI features in minutes!** 🚀

---

**Setup Guide**: [AI_SETUP.md](AI_SETUP.md)  
**Full API Documentation**: [AI_ASSISTANT.md](AI_ASSISTANT.md)

