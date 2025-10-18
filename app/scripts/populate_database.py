"""Populate database with sample data (without dropping existing tables)."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.password_reset import PasswordResetToken
from app.models.token import RefreshToken
from app.core.security import hash_password


def clear_existing_data(db: Session):
    """Clear existing data (keeps tables)."""
    print("🧹 Clearing existing data...")
    
    # Delete in reverse order of dependencies (child tables first)
    db.query(PasswordResetToken).delete()
    db.query(RefreshToken).delete()
    # user_roles and role_permissions are junction tables, will be cleared when we delete users/roles
    db.query(User).delete()
    db.query(Role).delete()
    db.query(Permission).delete()
    
    db.commit()
    print("✓ Existing data cleared")


def populate_database():
    """Populate database with sample data."""
    print("=" * 60)
    print("📊 Populating Database")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Clear existing data
        clear_existing_data(db)
        
        # 1. Create Permissions
        print("\n🔑 Creating permissions...")
        permissions_data = [
            "view_user", "create_user", "edit_user", "delete_user",
            "manage_roles",
            "manage_permissions",
            "use_ai", "manage_ai",
            "user:read", "user:write",
        ]
        
        permissions = []
        for perm_name in permissions_data:
            permission = Permission(name=perm_name)
            db.add(permission)
            permissions.append(permission)
        
        db.commit()
        db.refresh(permissions[0])  # Refresh to get IDs
        print(f"✓ Created {len(permissions)} permissions")
        
        # Reload permissions with IDs
        permissions = db.query(Permission).all()
        perm_dict = {p.name: p for p in permissions}
        
        # 2. Create Roles
        print("\n👥 Creating roles...")
        
        # Admin role
        admin_role = Role(name="admin")
        admin_role.permissions = permissions  # All permissions
        db.add(admin_role)
        
        # Manager role
        manager_role = Role(name="manager")
        manager_role.permissions = [
            perm_dict["view_user"], perm_dict["create_user"], perm_dict["edit_user"],
            perm_dict["manage_roles"],
            perm_dict["use_ai"], perm_dict["user:read"], perm_dict["user:write"],
        ]
        db.add(manager_role)
        
        # User role
        user_role = Role(name="user")
        user_role.permissions = [
            perm_dict["view_user"], perm_dict["use_ai"],
            perm_dict["user:write"],
        ]
        db.add(user_role)
        
        # Guest role
        guest_role = Role(name="guest")
        guest_role.permissions = [perm_dict["view_user"]]
        db.add(guest_role)
        
        db.commit()
        print("✓ Created 4 roles")
        
        # Reload roles with IDs
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        manager_role = db.query(Role).filter(Role.name == "manager").first()
        user_role = db.query(Role).filter(Role.name == "user").first()
        guest_role = db.query(Role).filter(Role.name == "guest").first()
        
        # 3. Create Users
        print("\n👤 Creating users...")
        
        # Admin user
        admin = User(
            email="admin@example.com",
            password=hash_password("Admin123!"),
            first_name="Admin",
            middle_name="Super",
            last_name="User",
            role_title="System Administrator",
            is_active=True,
            is_approved=True
        )
        admin.roles = [admin_role]
        db.add(admin)
        
        # Manager user
        manager = User(
            email="manager@example.com",
            password=hash_password("Manager123!"),
            first_name="John",
            middle_name="Michael",
            last_name="Manager",
            role_title="Department Manager",
            is_active=True,
            is_approved=True
        )
        manager.roles = [manager_role]
        db.add(manager)
        
        # Regular user
        user = User(
            email="user@example.com",
            password=hash_password("User123!"),
            first_name="Jane",
            middle_name="Marie",
            last_name="Doe",
            role_title="Team Member",
            is_active=True,
            is_approved=True
        )
        user.roles = [user_role]
        db.add(user)
        
        # Guest user
        guest = User(
            email="guest@example.com",
            password=hash_password("Guest123!"),
            first_name="Guest",
            middle_name="Test",
            last_name="Account",
            role_title="Guest User",
            is_active=True,
            is_approved=True
        )
        guest.roles = [guest_role]
        db.add(guest)
        
        db.commit()
        print("✓ Created 4 users")
        
        # Verify
        print("\n✅ Verification:")
        print(f"Permissions: {db.query(Permission).count()}")
        print(f"Roles: {db.query(Role).count()}")
        print(f"Users: {db.query(User).count()}")
        
        print("\n" + "=" * 60)
        print("🎉 Database populated successfully!")
        print("=" * 60)
        
        print("\n📝 Login Credentials:")
        print("-" * 60)
        print("Admin:   admin@example.com   / Admin123!")
        print("Manager: manager@example.com / Manager123!")
        print("User:    user@example.com    / User123!")
        print("Guest:   guest@example.com   / Guest123!")
        print("-" * 60)
        
        print("\n💡 Next Steps:")
        print("1. Start server: uvicorn app.main:app --reload")
        print("2. Visit: http://127.0.0.1:8000/docs")
        print("3. Login with any credentials above")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    populate_database()
