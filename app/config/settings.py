"""Application configuration with environment variable support."""
from typing import List, Optional
import secrets
import warnings
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, model_validator


class Settings(BaseSettings):
    """Type-safe configuration loaded from environment variables or .env file."""
    
    APP_NAME: str = "RBAC API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT signing key - must be changed in production",
        min_length=32
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
    
    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        """Validate critical security settings."""
        # Check if default secret key is being used in production
        if not self.DEBUG and self.SECRET_KEY == "your-secret-key-change-in-production":
            raise ValueError(
                "CRITICAL SECURITY ERROR: Default SECRET_KEY detected in production mode. "
                "Generate a secure key using: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        
        # Ensure secret key is strong enough
        if len(self.SECRET_KEY) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters long for security. "
                "Generate a secure key using: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        
        # Validate CORS origins in production
        if not self.DEBUG:
            for origin in self.BACKEND_CORS_ORIGINS:
                if origin == "*":
                    raise ValueError(
                        "SECURITY ERROR: Wildcard CORS origin (*) not allowed in production"
                    )
                if "localhost" in origin or "127.0.0.1" in origin:
                    warnings.warn(
                        f"SECURITY WARNING: localhost origin '{origin}' detected in production mode. "
                        f"This should be replaced with your actual domain in production.",
                        UserWarning,
                        stacklevel=2
                    )
        
        return self
    
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Email Configuration
    MAIL_USERNAME: str = Field(
        default="",
        description="Email username/address for sending emails"
    )
    MAIL_PASSWORD: str = Field(
        default="",
        description="Email password or app-specific password"
    )
    MAIL_FROM: str = Field(
        default="noreply@example.com",
        description="Default sender email address"
    )
    MAIL_FROM_NAME: str = Field(
        default="RBAC API",
        description="Default sender name"
    )
    MAIL_PORT: int = Field(
        default=587,
        description="SMTP port (587 for TLS, 465 for SSL)"
    )
    MAIL_SERVER: str = Field(
        default="smtp.gmail.com",
        description="SMTP server address"
    )
    MAIL_STARTTLS: bool = Field(
        default=True,
        description="Use STARTTLS for email encryption"
    )
    MAIL_SSL_TLS: bool = Field(
        default=False,
        description="Use SSL/TLS for email encryption"
    )
    USE_CREDENTIALS: bool = Field(
        default=True,
        description="Use credentials for SMTP authentication"
    )
    VALIDATE_CERTS: bool = Field(
        default=True,
        description="Validate SSL certificates"
    )
    
    # Password Reset Configuration
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        ge=5,
        description="Password reset token expiration in minutes"
    )
    FRONTEND_URL: str = Field(
        default="http://localhost:3000",
        description="Frontend URL for password reset links"
    )
    
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

