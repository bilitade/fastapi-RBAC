"""
Database initialization script.

This script initializes the database with:
- Default permissions
- Default roles (superadmin, admin, normal)
- Default users for each role
- Permission assignments to roles

Run this script after creating the database tables.

Usage:
    python -m app.scripts.init_db
"""
from typing import List
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.core.security import hash_password


# Default permissions for the system
DEFAULT_PERMISSIONS = [
    # User management
    "create_user",
    "delete_user",
    "view_user",
    "edit_user",
    
    # Role management
    "manage_roles",
    
    # Permission management
    "manage_permissions",
    
    # Example application permissions (customize as needed)
    "create_board",
    "edit_board",
    "delete_board",
    "view_board",
    "create_task",
    "edit_task",
    "delete_task",
    "view_task",
]


def create_permissions(db: Session, permissions: List[str]) -> None:
    """
    Create permissions in the database if they don't exist.
    
    Args:
        db: Database session
        permissions: List of permission names to create
    """
    created_count = 0
    for permission_name in permissions:
        existing = db.query(Permission).filter(
            Permission.name == permission_name
        ).first()
        
        if not existing:
            permission = Permission(name=permission_name)
            db.add(permission)
            created_count += 1
    
    db.commit()
    print(f"✓ Created {created_count} new permissions (total: {len(permissions)})")


def create_roles(db: Session) -> None:
    """
    Create default roles in the database.
    
    Args:
        db: Database session
    """
    role_names = ["superadmin", "admin", "normal"]
    created_count = 0
    
    for role_name in role_names:
        existing = db.query(Role).filter(Role.name == role_name).first()
        if not existing:
            role = Role(name=role_name)
            db.add(role)
            created_count += 1
    
    db.commit()
    print(f"✓ Created {created_count} new roles (total: {len(role_names)})")


def create_default_users(db: Session) -> None:
    """Create default admin users with assigned roles."""
    default_users = [
        {
            "first_name": "Super",
            "middle_name": "Admin",
            "last_name": "User",
            "role_title": "System Administrator",
            "email": "superadmin@example.com",
            "password": "SuperAdmin123!",
            "role": "superadmin",
            "is_approved": True
        },
        {
            "first_name": "Admin",
            "middle_name": "System",
            "last_name": "User",
            "role_title": "Administrator",
            "email": "admin@example.com",
            "password": "Admin123!",
            "role": "admin",
            "is_approved": True
        },
        {
            "first_name": "Normal",
            "middle_name": "Test",
            "last_name": "User",
            "role_title": "User",
            "email": "user@example.com",
            "password": "User123!",
            "role": "normal",
            "is_approved": True
        },
    ]
    
    created_count = 0
    for user_data in default_users:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        
        if not existing:
            user = User(
                first_name=user_data["first_name"],
                middle_name=user_data["middle_name"],
                last_name=user_data["last_name"],
                role_title=user_data.get("role_title"),
                email=user_data["email"],
                password=hash_password(user_data["password"]),
                is_active=True,
                is_approved=user_data.get("is_approved", False)
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            role = db.query(Role).filter(Role.name == user_data["role"]).first()
            if role:
                user.roles.append(role)
                db.commit()
            
            created_count += 1
            print(f"  - Created user: {user_data['email']} (role: {user_data['role']})")
    
    if created_count == 0:
        print("✓ All default users already exist")
    else:
        print(f"✓ Created {created_count} new users")


def assign_permissions_to_roles(db: Session) -> None:
    """
    Assign permissions to roles based on predefined mappings.
    
    Args:
        db: Database session
    """
    # Build permission lookup map
    all_permissions = db.query(Permission).all()
    permission_map = {p.name: p for p in all_permissions}
    
    # Define role-permission mappings
    role_permission_map = {
        "superadmin": DEFAULT_PERMISSIONS,  # All permissions
        "admin": [
            "create_user",
            "view_user",
            "edit_user",
            "create_board",
            "edit_board",
            "view_board",
            "create_task",
            "edit_task",
            "view_task",
        ],
        "normal": [
            "view_board",
            "view_task",
            "create_task",
        ],
    }
    
    for role_name, permission_names in role_permission_map.items():
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            print(f"⚠ Role '{role_name}' not found, skipping permission assignment")
            continue
        
        # Resolve permission objects
        permissions = [
            permission_map[name]
            for name in permission_names
            if name in permission_map
        ]
        
        # Assign permissions to role
        role.permissions = permissions
        db.commit()
        print(f"✓ Assigned {len(permissions)} permissions to role '{role_name}'")


def init_database() -> None:
    """
    Initialize the database with default data.
    """
    print("=" * 60)
    print("Initializing database...")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Create all default data
        create_permissions(db, DEFAULT_PERMISSIONS)
        create_roles(db)
        create_default_users(db)
        assign_permissions_to_roles(db)
        
        print("=" * 60)
        print("✓ Database initialization complete!")
        print("=" * 60)
        print("\nDefault users created:")
        print("  - superadmin@example.com / SuperAdmin123!")
        print("  - admin@example.com / Admin123!")
        print("  - user@example.com / User123!")
        print("\nYou can now start the application with: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()

