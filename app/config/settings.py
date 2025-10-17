"""Application configuration with environment variable support."""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Type-safe configuration loaded from environment variables or .env file."""
    
    APP_NAME: str = "RBAC API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT signing key - must be changed in production"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, ge=1)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, ge=1)
    MIN_PASSWORD_LENGTH: int = Field(default=8, ge=6)
    
    DATABASE_URL: str = Field(
        default="postgresql+psycopg2://postgres:12345678@localhost:5432/rbac",
        description="Database connection string"
    )
    
    BACKEND_CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="Comma-separated allowed origins"
    )
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="after")
    @classmethod
    def assemble_cors_origins(cls, v: str) -> List[str]:
        """Parse comma-separated origins into list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # AI Configuration
    AI_PROVIDER: str = Field(
        default="openai",
        description="AI provider: openai, anthropic, or custom"
    )
    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    ANTHROPIC_API_KEY: Optional[str] = Field(
        default=None,
        description="Anthropic API key"
    )
    AI_MODEL: str = Field(
        default="gpt-3.5-turbo",
        description="Default AI model to use"
    )
    AI_TEMPERATURE: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="AI temperature for responses"
    )
    AI_MAX_TOKENS: int = Field(
        default=1000,
        ge=1,
        description="Max tokens for AI responses"
    )
    
    # Storage Configuration
    UPLOAD_DIR: str = Field(
        default="./data/uploads",
        description="Directory for file uploads"
    )
    VECTOR_STORE_PATH: str = Field(
        default="./data/vectorstore",
        description="Path to vector store data"
    )
    EMBEDDING_MODEL: str = Field(
        default="text-embedding-ada-002",
        description="Embedding model for vector store"
    )
    MAX_UPLOAD_SIZE: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Maximum file upload size in bytes"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()

