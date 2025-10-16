from pydantic import BaseModel, Field
from typing import List, Optional


class PermissionSchema(BaseModel):
    id: Optional[int] = None
    name: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {"id": 1, "name": "create_user"}
        }


class RoleSchema(BaseModel):
    id: Optional[int] = None
    name: str
    permissions: List[PermissionSchema] = Field(default_factory=list)

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {"id": 1, "name": "admin", "permissions": [{"id": 1, "name": "create_user"}]}
        }


class UserSchema(BaseModel):
    id: Optional[int] = None
    email: str
    roles: List[RoleSchema] = Field(default_factory=list)

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {"id": 1, "email": "admin@example.com", "roles": [{"id": 1, "name": "admin"}]}
        }


class UserCreate(BaseModel):
    email: str
    password: str

    class Config:
        schema_extra = {
            "example": {"email": "user@example.com", "password": "strongpassword"}
        }


class RoleCreate(BaseModel):
    name: str
    permissions: Optional[List[str]] = Field(default_factory=list)

    class Config:
        schema_extra = {"example": {"name": "admin", "permissions": ["create_user", "edit_user"]}}


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"

    class Config:
        schema_extra = {
            "example": {"access_token": "<access token>", "refresh_token": "<refresh token>", "token_type": "bearer"}
        }


class RefreshRequest(BaseModel):
    refresh_token: str

    class Config:
        schema_extra = {"example": {"refresh_token": "<refresh token>"}}
