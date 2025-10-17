"""AI agent schemas for request/response validation."""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class MessageRole(str, Enum):
    """Chat message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Chat message schema."""
    role: MessageRole
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    """Chat request schema."""
    message: str = Field(..., min_length=1, max_length=5000, description="User message")
    system_prompt: Optional[str] = Field(None, max_length=2000, description="Custom system prompt")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "How can I improve user engagement?",
                "context": {"product": "SaaS platform", "industry": "education"}
            }
        }
    )


class ChatResponse(BaseModel):
    """Chat response schema."""
    response: str = Field(..., description="AI response")
    model: str = Field(..., description="Model used")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "response": "Here are some ideas to improve user engagement...",
                "model": "gpt-3.5-turbo"
            }
        }
    )


class IdeaGenerationRequest(BaseModel):
    """Idea generation request schema."""
    topic: str = Field(..., min_length=1, max_length=500)
    context: Optional[str] = Field(None, max_length=2000)
    style: str = Field(default="professional", description="Writing style")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "topic": "Mobile app features",
                "context": "E-commerce platform for small businesses",
                "style": "professional"
            }
        }
    )


class ContentEnhanceRequest(BaseModel):
    """Content enhancement request schema."""
    content: str = Field(..., min_length=1, max_length=10000)
    enhancement_type: str = Field(
        default="improve",
        description="Type: improve, expand, summarize, professional, simplify"
    )
    target_length: Optional[str] = Field(
        None,
        description="Target length: short, medium, long"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content": "This product helps businesses grow.",
                "enhancement_type": "expand",
                "target_length": "medium"
            }
        }
    )


class AutoFillRequest(BaseModel):
    """Auto-fill suggestion request schema."""
    field_name: str = Field(..., min_length=1, max_length=100)
    existing_data: Dict[str, Any] = Field(..., description="Already filled fields")
    field_description: Optional[str] = Field(None, max_length=500)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "field_name": "company_description",
                "existing_data": {
                    "company_name": "TechStartup Inc",
                    "industry": "Software",
                    "size": "50 employees"
                },
                "field_description": "Brief company description"
            }
        }
    )


class DocumentSearchRequest(BaseModel):
    """Document search request schema."""
    query: str = Field(..., min_length=1, max_length=500)
    max_results: int = Field(default=5, ge=1, le=20)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "How to configure authentication?",
                "max_results": 5
            }
        }
    )


class DocumentSearchResponse(BaseModel):
    """Document search response schema."""
    results: List[Dict[str, str]] = Field(..., description="Search results")
    count: int = Field(..., description="Number of results")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "results": [
                    {
                        "content": "Authentication is configured in...",
                        "source": "docs/auth.md"
                    }
                ],
                "count": 1
            }
        }
    )


class AIResponse(BaseModel):
    """Generic AI response schema."""
    result: str = Field(..., description="AI generated result")
    model: str = Field(..., description="Model used")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "result": "Generated content here...",
                "model": "gpt-3.5-turbo"
            }
        }
    )

