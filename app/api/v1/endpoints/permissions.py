"""Permission management endpoints."""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.permission import Permission
from app.schemas.permission import PermissionCreate, PermissionResponse
from app.middleware import require_permission

router = APIRouter()


@router.post("/", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
def create_permission(
    permission_data: PermissionCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission("manage_permissions"))
) -> Any:
    """Create new permission (requires 'manage_permissions' permission)."""
    existing_permission = db.query(Permission).filter(
        Permission.name == permission_data.name
    ).first()
    if existing_permission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission with this name already exists"
        )
    
    new_permission = Permission(name=permission_data.name)
    db.add(new_permission)
    db.commit()
    db.refresh(new_permission)
    return new_permission


@router.get("/{permission_id}", response_model=PermissionResponse)
def read_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission("manage_permissions"))
) -> Any:
    """Get permission by ID (requires 'manage_permissions' permission)."""
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    return permission


@router.get("/", response_model=List[PermissionResponse])
def list_permissions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission("manage_permissions"))
) -> Any:
    """List permissions with pagination (requires 'manage_permissions' permission)."""
    permissions = db.query(Permission).offset(skip).limit(limit).all()
    return permissions


@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission("manage_permissions"))
) -> None:
    """Delete permission (requires 'manage_permissions' permission)."""
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    db.delete(permission)
    db.commit()

