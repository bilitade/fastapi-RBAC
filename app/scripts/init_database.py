"""Initialize database with sample data - proper order to maintain integrity."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.db.base import Base, import_models
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.core.security import hash_password


def drop_all_tables():
    """Drop all existing tables."""
    print("🗑️  Dropping all existing tables...")
    # Use raw SQL with CASCADE to handle dependencies
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS password_reset_tokens CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS refresh_tokens CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS user_roles CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS role_permissions CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS roles CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS permissions CASCADE"))
        conn.commit()
    print("✓ All tables dropped")


def create_all_tables():
    """Create all tables."""
    print("\n📊 Creating all tables...")
    import_models()
    Base.metadata.create_all(bind=engine)
    print("✓ All tables created")


def create_permissions(db: Session):
    """Create permissions."""
    print("\n🔑 Creating permissions...")
    
    permissions_data = [
        # User permissions (match endpoints)
        "view_user",
        "create_user",
        "edit_user",
        "delete_user",
        
        # Role permissions (match endpoints)
        "manage_roles",
        
        # Permission permissions (match endpoints)
        "manage_permissions",
        
        # AI permissions
        "use_ai",
        "manage_ai",
        
        # File permissions
        "user:read",
        "user:write",
    ]
    
    permissions = []
    for perm_name in permissions_data:
        permission = Permission(name=perm_name)
        db.add(permission)
        permissions.append(permission)
    
    db.commit()
    print(f"✓ Created {len(permissions)} permissions")
    return permissions


def create_roles(db: Session, permissions: list):
    """Create roles with permissions."""
    print("\n👥 Creating roles...")
    
    # Get permissions by name for easy assignment
    perm_dict = {p.name: p for p in permissions}
    
    # Admin role - all permissions
    admin_role = Role(name="admin")
    admin_role.permissions = permissions  # All permissions
    db.add(admin_role)
    
    # Manager role - most permissions except critical ones
    manager_role = Role(name="manager")
    manager_role.permissions = [
        perm_dict["view_user"],
        perm_dict["create_user"],
        perm_dict["edit_user"],
        perm_dict["manage_roles"],
        perm_dict["use_ai"],
        perm_dict["user:read"],
        perm_dict["user:write"],
    ]
    db.add(manager_role)
    
    # User role - basic permissions
    user_role = Role(name="user")
    user_role.permissions = [
        perm_dict["view_user"],
        perm_dict["use_ai"],
        perm_dict["user:write"],
    ]
    db.add(user_role)
    
    # Guest role - minimal permissions
    guest_role = Role(name="guest")
    guest_role.permissions = [
        perm_dict["view_user"],
    ]
    db.add(guest_role)
    
    db.commit()
    print("✓ Created 4 roles (admin, manager, user, guest)")
    
    return {
        "admin": admin_role,
        "manager": manager_role,
        "user": user_role,
        "guest": guest_role
    }


def create_users(db: Session, roles: dict):
    """Create sample users."""
    print("\n👤 Creating users...")
    
    users_data = [
        {
            "email": "admin@example.com",
            "password": "Admin123!",
            "first_name": "Admin",
            "middle_name": "Super",
            "last_name": "User",
            "role_title": "System Administrator",
            "is_active": True,
            "is_approved": True,
            "roles": [roles["admin"]]
        },
        {
            "email": "manager@example.com",
            "password": "Manager123!",
            "first_name": "John",
            "middle_name": "Michael",
            "last_name": "Manager",
            "role_title": "Department Manager",
            "is_active": True,
            "is_approved": True,
            "roles": [roles["manager"]]
        },
        {
            "email": "user@example.com",
            "password": "User123!",
            "first_name": "Jane",
            "middle_name": "Marie",
            "last_name": "Doe",
            "role_title": "Team Member",
            "is_active": True,
            "is_approved": True,
            "roles": [roles["user"]]
        },
        {
            "email": "guest@example.com",
            "password": "Guest123!",
            "first_name": "Guest",
            "middle_name": "Test",
            "last_name": "Account",
            "role_title": "Guest User",
            "is_active": True,
            "is_approved": True,
            "roles": [roles["guest"]]
        },
        {
            "email": "inactive@example.com",
            "password": "Inactive123!",
            "first_name": "Inactive",
            "middle_name": "Test",
            "last_name": "User",
            "role_title": "Inactive Account",
            "is_active": False,
            "is_approved": False,
            "roles": [roles["user"]]
        }
    ]
    
    users = []
    for user_data in users_data:
        # Extract roles before creating user
        user_roles = user_data.pop("roles")
        
        # Hash password
        plain_password = user_data.pop("password")
        user_data["password"] = hash_password(plain_password)
        
        # Create user
        user = User(**user_data)
        user.roles = user_roles
        
        db.add(user)
        users.append(user)
    
    db.commit()
    print(f"✓ Created {len(users)} users")
    
    # Print credentials
    print("\n📝 User Credentials:")
    print("=" * 60)
    for user_data in users_data:
        print(f"Email: {user_data['email']}")
        print(f"Password: {user_data.get('password', 'See above')}")
        print(f"Role: {user_data['roles'][0].name if user_data.get('roles') else 'N/A'}")
        print("-" * 60)
    
    return users


def verify_data(db: Session):
    """Verify all data was created correctly."""
    print("\n✅ Verifying database...")
    
    users_count = db.query(User).count()
    roles_count = db.query(Role).count()
    permissions_count = db.query(Permission).count()
    
    print(f"Users: {users_count}")
    print(f"Roles: {roles_count}")
    print(f"Permissions: {permissions_count}")
    
    # Check relationships
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    if admin:
        print(f"\nAdmin user has {len(admin.roles)} role(s)")
        if admin.roles:
            print(f"Admin role has {len(admin.roles[0].permissions)} permission(s)")
    
    print("\n✓ Database verification complete")


def main():
    """Main initialization function."""
    print("=" * 60)
    print("🚀 Database Initialization Script")
    print("=" * 60)
    
    try:
        # Step 1: Drop existing tables
        drop_all_tables()
        
        # Step 2: Create all tables
        create_all_tables()
        
        # Step 3: Create data in correct order
        db = SessionLocal()
        
        try:
            # Order matters for foreign key integrity!
            permissions = create_permissions(db)
            roles = create_roles(db, permissions)
            users = create_users(db, roles)
            
            # Step 4: Verify
            verify_data(db)
            
            print("\n" + "=" * 60)
            print("🎉 Database initialized successfully!")
            print("=" * 60)
            print("\n💡 Quick Start:")
            print("1. Start server: uvicorn app.main:app --reload")
            print("2. Visit: http://127.0.0.1:8000/docs")
            print("3. Login with: admin@example.com / Admin123!")
            print("\n")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
