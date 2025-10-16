"""
User schemas for request/response validation.
"""
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from app.schemas.role import RoleResponse


class UserBase(BaseModel):
    """Base user schema with common attributes."""
    email: EmailStr = Field(
        ...,
        description="User email address",
        examples=["user@example.com"]
    )


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="User password (min 8 characters)",
        examples=["SecurePassword123!"]
    )
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = Field(None, description="New email address")
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=100,
        description="New password"
    )
    role_names: Optional[List[str]] = Field(
        None,
        description="List of role names to assign to this user"
    )


class UserResponse(UserBase):
    """Schema for user responses (excludes password)."""
    id: int = Field(..., description="User ID")
    roles: List[RoleResponse] = Field(
        default_factory=list,
        description="List of roles assigned to this user"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "admin@example.com",
                "roles": [
                    {
                        "id": 1,
                        "name": "admin",
                        "permissions": [
                            {"id": 1, "name": "create_user"}
                        ]
                    }
                ]
            }
        }
    )

