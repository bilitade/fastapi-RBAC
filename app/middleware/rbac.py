"""RBAC decorators for permission and role-based endpoint protection."""
from typing import List, Set, Callable
from fastapi import Depends, HTTPException, status
from app.models.user import User
from app.core.dependencies import get_current_user


def get_user_permissions(user: User) -> Set[str]:
    """Extract all permissions from user's roles."""
    permissions: Set[str] = set()
    for role in user.roles:
        for permission in role.permissions:
            permissions.add(permission.name)
    return permissions


def get_user_roles(user: User) -> Set[str]:
    """Extract all role names from user."""
    return {role.name for role in user.roles}


def require_permission(permission_name: str) -> Callable:
    """
    Protect endpoint with permission requirement.
    
    Usage:
        @router.post("/users/")
        def create_user(_: bool = Depends(require_permission("create_user"))):
            pass
    """
    def permission_checker(current_user: User = Depends(get_current_user)) -> bool:
        user_permissions = get_user_permissions(current_user)
        if permission_name not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required: {permission_name}"
            )
        return True
    return permission_checker


def require_permissions(permission_names: List[str], require_all: bool = True) -> Callable:
    """
    Protect endpoint with multiple permission requirements.
    
    Args:
        require_all: True for AND logic, False for OR logic
    
    Usage:
        # User needs both permissions
        @router.delete("/data/")
        def delete(_: bool = Depends(require_permissions(["delete", "admin"]))):
            pass
        
        # User needs any one permission
        @router.get("/data/")
        def view(_: bool = Depends(require_permissions(["view", "admin"], require_all=False))):
            pass
    """
    def permission_checker(current_user: User = Depends(get_current_user)) -> bool:
        user_permissions = get_user_permissions(current_user)
        
        if require_all:
            missing = [p for p in permission_names if p not in user_permissions]
            if missing:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing permissions: {', '.join(missing)}"
                )
        else:
            if not any(p in user_permissions for p in permission_names):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Required one of: {', '.join(permission_names)}"
                )
        return True
    return permission_checker


def require_role(role_name: str) -> Callable:
    """
    Protect endpoint with role requirement.
    
    Usage:
        @router.get("/admin/")
        def admin_page(_: bool = Depends(require_role("admin"))):
            pass
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> bool:
        user_roles = get_user_roles(current_user)
        if role_name not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {role_name}"
            )
        return True
    return role_checker


def require_roles(role_names: List[str], require_all: bool = False) -> Callable:
    """
    Protect endpoint with multiple role requirements.
    
    Args:
        require_all: False (default) for OR logic, True for AND logic
    
    Usage:
        # User needs admin OR superadmin role
        @router.get("/restricted/")
        def restricted(_: bool = Depends(require_roles(["admin", "superadmin"]))):
            pass
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> bool:
        user_roles = get_user_roles(current_user)
        
        if require_all:
            missing = [r for r in role_names if r not in user_roles]
            if missing:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing roles: {', '.join(missing)}"
                )
        else:
            if not any(r in user_roles for r in role_names):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Required one of: {', '.join(role_names)}"
                )
        return True
    return role_checker

