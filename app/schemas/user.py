"""User schemas for request/response validation."""
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from app.schemas.role import RoleResponse


class UserBase(BaseModel):
    """Base user schema with common attributes."""
    first_name: str = Field(..., min_length=1, max_length=100, examples=["John"])
    middle_name: str = Field(..., min_length=1, max_length=100, examples=["Michael"])
    last_name: str = Field(..., min_length=1, max_length=100, examples=["Doe"])
    role_title: Optional[str] = Field(None, max_length=100, examples=["Software Engineer"])
    email: EmailStr = Field(..., examples=["john.doe@example.com"])


class UserRegister(UserBase):
    """Public registration schema."""
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
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


class UserCreate(UserRegister):
    """Admin user creation schema (includes role assignment)."""
    role_names: Optional[List[str]] = Field(
        default=None,
        description="Role names to assign"
    )


class UserProfileUpdate(BaseModel):
    """Self-service profile update schema."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role_title: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        """Validate password strength if provided."""
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v


class UserAdminUpdate(BaseModel):
    """Admin user update schema (partial updates)."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role_title: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    role_names: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_approved: Optional[bool] = None


class UserResponse(UserBase):
    """User response schema."""
    id: int
    is_active: bool
    is_approved: bool
    roles: List[RoleResponse] = Field(default_factory=list)
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "first_name": "John",
                "middle_name": "Michael",
                "last_name": "Doe",
                "role_title": "Software Engineer",
                "email": "john.doe@example.com",
                "is_active": True,
                "is_approved": True,
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

