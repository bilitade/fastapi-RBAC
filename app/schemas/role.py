"""
Role schemas for request/response validation.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.permission import PermissionResponse


class RoleBase(BaseModel):
    """Base role schema with common attributes."""
    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Unique role name",
        examples=["admin", "user", "manager"]
    )


class RoleCreate(RoleBase):
    """Schema for creating a new role."""
    permission_names: List[str] = Field(
        default_factory=list,
        description="List of permission names to assign to this role"
    )


class RoleUpdate(BaseModel):
    """Schema for updating a role."""
    name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        description="New role name"
    )
    permission_names: Optional[List[str]] = Field(
        None,
        description="List of permission names to assign to this role"
    )


class RoleResponse(RoleBase):
    """Schema for role responses."""
    id: int = Field(..., description="Role ID")
    permissions: List[PermissionResponse] = Field(
        default_factory=list,
        description="List of permissions granted to this role"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "admin",
                "permissions": [
                    {"id": 1, "name": "create_user"},
                    {"id": 2, "name": "delete_user"}
                ]
            }
        }
    )

