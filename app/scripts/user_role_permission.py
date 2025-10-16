from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import Permission, Role, User
from app.auth import hash_password

default_permissions = [
    "create_user",
    "delete_user",
    "view_user",
    "edit_user",
    "manage_roles",
    "manage_permissions",
    "create_board",
    "edit_board",
    "delete_board",
    "view_board",
    "create_task",
    "edit_task",
    "delete_task",
    "view_task",
]


def create_permissions(db: Session):
    for perm_name in default_permissions:
        perm = db.query(Permission).filter(Permission.name == perm_name).first()
        if not perm:
            perm = Permission(name=perm_name)
            db.add(perm)
    db.commit()
    print("Permissions populated!")


def create_roles(db: Session):
    role_names = ["superadmin", "admin", "normal"]
    created = []
    for name in role_names:
        role = db.query(Role).filter(Role.name == name).first()
        if not role:
            role = Role(name=name)
            db.add(role)
            created.append(name)
    db.commit()
    if created:
        print("Roles created:", created)
    else:
        print("Roles already exist")


def create_users(db: Session):
    # Define three users and which role they should have
    users = [
        {"email": "superadmin@example.com", "password": "supersecret", "role": "superadmin"},
        {"email": "admin@example.com", "password": "adminsecret", "role": "admin"},
        {"email": "user@example.com", "password": "usersecret", "role": "normal"},
    ]

    for u in users:
        user = db.query(User).filter(User.email == u["email"]).first()
        if not user:
            user = User(email=u["email"], password=hash_password(u["password"]))
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created user {u['email']}")
        else:
            print(f"User {u['email']} already exists")

        # Ensure role assignment
        role = db.query(Role).filter(Role.name == u["role"]).first()
        if role and role not in user.roles:
            user.roles.append(role)
            db.commit()
            print(f"Assigned role '{role.name}' to {user.email}")


def assign_permissions_to_roles(db: Session):
    """Map permissions to roles.

    - superadmin: all permissions
    - admin: common management permissions
    - normal: read/create limited permissions
    """
    # Build a name -> Permission map (force keys to str to satisfy type checkers)
    perms = db.query(Permission).all()
    perm_map = {str(p.name): p for p in perms}

    role_permission_map = {
        "superadmin": default_permissions,  # all
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

    for role_name, perm_names in role_permission_map.items():
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            print(f"Role '{role_name}' not found, skipping permission assignment")
            continue

        # Resolve Permission objects, skip missing names
        resolved = [perm_map[name] for name in perm_names if name in perm_map]

        # Replace role.permissions with resolved list (idempotent)
        role.permissions = resolved
        db.commit()
        print(f"Assigned {len(resolved)} permissions to role '{role_name}'")


def run():
    db = SessionLocal()
    try:
        create_permissions(db)
        create_roles(db)
        create_users(db)
        assign_permissions_to_roles(db)
        print("Startup data population complete.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
