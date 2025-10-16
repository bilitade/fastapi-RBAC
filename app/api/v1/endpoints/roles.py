"""Role management endpoints."""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.role import Role
from app.models.permission import Permission
from app.schemas.role import RoleCreate, RoleResponse, RoleUpdate
from app.middleware import require_permission

router = APIRouter()


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission("manage_roles"))
) -> Any:
    """Create new role (requires 'manage_roles' permission)."""
    existing_role = db.query(Role).filter(Role.name == role_data.name).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role with this name already exists"
        )
    
    new_role = Role(name=role_data.name)
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    
    if role_data.permission_names:
        permissions = db.query(Permission).filter(
            Permission.name.in_(role_data.permission_names)
        ).all()
        new_role.permissions = permissions
        db.commit()
        db.refresh(new_role)
    
    return new_role


@router.get("/{role_id}", response_model=RoleResponse)
def read_role(
    role_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission("manage_roles"))
) -> Any:
    """Get role by ID (requires 'manage_roles' permission)."""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role


@router.get("/", response_model=List[RoleResponse])
def list_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission("manage_roles"))
) -> Any:
    """List roles with pagination (requires 'manage_roles' permission)."""
    roles = db.query(Role).offset(skip).limit(limit).all()
    return roles


@router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission("manage_roles"))
) -> Any:
    """Update role details (requires 'manage_roles' permission)."""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    if role_data.name is not None:
        existing = db.query(Role).filter(
            Role.name == role_data.name,
            Role.id != role_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role name already taken"
            )
        role.name = role_data.name
    
    if role_data.permission_names is not None:
        permissions = db.query(Permission).filter(
            Permission.name.in_(role_data.permission_names)
        ).all()
        role.permissions = permissions
    
    db.commit()
    db.refresh(role)
    return role


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission("manage_roles"))
) -> None:
    """Delete role (requires 'manage_roles' permission)."""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    db.delete(role)
    db.commit()

