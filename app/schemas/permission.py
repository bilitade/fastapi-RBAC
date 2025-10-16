"""
Permission schemas for request/response validation.
"""
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class PermissionBase(BaseModel):
    """Base permission schema with common attributes."""
    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Unique permission name",
        examples=["create_user", "edit_post", "delete_comment"]
    )


class PermissionCreate(PermissionBase):
    """Schema for creating a new permission."""
    pass


class PermissionResponse(PermissionBase):
    """Schema for permission responses."""
    id: int = Field(..., description="Permission ID")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "create_user"
            }
        }
    )

