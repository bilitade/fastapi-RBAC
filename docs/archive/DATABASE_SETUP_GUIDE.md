# Database Setup Guide

## 🚀 Quick Start

### Option 1: Full Reset (Recommended for Fresh Start)

This will **drop all tables** and recreate everything with sample data:

```bash
python3 app/scripts/init_database.py
```

**What it does:**
1. ✅ Drops all existing tables
2. ✅ Creates all tables fresh
3. ✅ Populates with sample data
4. ✅ Maintains foreign key integrity

### Option 2: Populate Only (Keep Tables)

This will **clear data** but keep table structure:

```bash
python3 app/scripts/populate_database.py
```

**What it does:**
1. ✅ Clears existing data
2. ✅ Keeps table structure
3. ✅ Populates with sample data
4. ✅ Maintains foreign key integrity

---

## 📊 What Gets Created

### Permissions (20)
- **User Management:** view_users, create_user, update_user, delete_user, approve_user
- **Role Management:** view_roles, create_role, update_role, delete_role, assign_role
- **Permission Management:** view_permissions, create_permission, update_permission, delete_permission, assign_permission
- **AI Features:** use_ai, manage_ai
- **File Management:** upload_files, view_files, delete_files

### Roles (4)

| Role | Permissions | Description |
|------|-------------|-------------|
| **admin** | All 20 permissions | Full system access |
| **manager** | 8 permissions | Elevated access (no delete/assign) |
| **user** | 4 permissions | Basic user access |
| **guest** | 1 permission | Read-only access |

### Users (4)

| Email | Password | Role | Status |
|-------|----------|------|--------|
| admin@example.com | Admin123! | admin | Active ✅ |
| manager@example.com | Manager123! | manager | Active ✅ |
| user@example.com | User123! | user | Active ✅ |
| guest@example.com | Guest123! | guest | Active ✅ |

---

## 🔧 Troubleshooting

### Error: "Foreign key constraint fails"

**Cause:** Trying to create data in wrong order

**Solution:** Use the provided scripts which create data in correct order:
1. Permissions (no dependencies)
2. Roles (depends on Permissions)
3. Users (depends on Roles)

### Error: "Table already exists"

**Cause:** Tables already created

**Solution:** 
- Use `populate_database.py` to just add data
- Or use `init_database.py` to drop and recreate everything

### Error: "No module named 'app'"

**Cause:** Python can't find the app module

**Solution:**
```bash
# Make sure you're in the project root
cd /home/bilisuma/Desktop/RBAC

# Run the script
python3 app/scripts/init_database.py
```

### Error: "Connection refused"

**Cause:** Database server not running

**Solution:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start if needed
sudo systemctl start postgresql
```

---

## 🎯 Manual Database Setup

If you want to create tables manually:

### 1. Create Tables Only

```bash
python3 app/scripts/create_password_reset_table.py
```

Or use Python:

```python
from app.db.session import engine
from app.db.base import Base, import_models

import_models()
Base.metadata.create_all(bind=engine)
```

### 2. Add Data Manually

```python
from app.db.session import SessionLocal
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.core.security import hash_password

db = SessionLocal()

# Create permission
perm = Permission(name="view_users", description="View users")
db.add(perm)
db.commit()

# Create role with permission
role = Role(name="admin", description="Administrator")
role.permissions = [perm]
db.add(role)
db.commit()

# Create user with role
user = User(
    email="admin@example.com",
    password=hash_password("Admin123!"),
    first_name="Admin",
    middle_name="",
    last_name="User",
    is_active=True,
    is_approved=True
)
user.roles = [role]
db.add(user)
db.commit()

db.close()
```

---

## 📝 Database Schema

### Correct Order for Foreign Keys

```
1. permissions (no dependencies)
   ↓
2. roles (no dependencies)
   ↓
3. role_permissions (depends on: roles, permissions)
   ↓
4. users (no dependencies)
   ↓
5. user_roles (depends on: users, roles)
   ↓
6. refresh_tokens (depends on: users)
   ↓
7. password_reset_tokens (depends on: users)
```

### Relationships

```
User ←→ Role (many-to-many via user_roles)
Role ←→ Permission (many-to-many via role_permissions)
User → RefreshToken (one-to-many)
User → PasswordResetToken (one-to-many)
```

---

## ✅ Verification

After running the scripts, verify everything:

```bash
# Connect to database
psql -U postgres -d rbac

# Check tables
\dt

# Check data
SELECT COUNT(*) FROM permissions;
SELECT COUNT(*) FROM roles;
SELECT COUNT(*) FROM users;

# Check relationships
SELECT u.email, r.name 
FROM users u 
JOIN user_roles ur ON u.id = ur.user_id 
JOIN roles r ON ur.role_id = r.id;

# Exit
\q
```

---

## 🎨 Customization

### Add Your Own Users

Edit `app/scripts/populate_database.py`:

```python
# Add your user
my_user = User(
    email="myemail@example.com",
    password=hash_password("MyPassword123!"),
    first_name="My",
    middle_name="Custom",
    last_name="User",
    role_title="My Title",
    is_active=True,
    is_approved=True
)
my_user.roles = [user_role]  # or admin_role, manager_role, etc.
db.add(my_user)
```

### Add Custom Permissions

```python
custom_perm = Permission(
    name="custom_action",
    description="My custom permission"
)
db.add(custom_perm)
db.commit()
```

### Add Custom Roles

```python
custom_role = Role(
    name="custom_role",
    description="My custom role"
)
custom_role.permissions = [perm1, perm2, perm3]
db.add(custom_role)
db.commit()
```

---

## 🚨 Important Notes

### Foreign Key Integrity

**Always create in this order:**
1. ✅ Permissions first (no dependencies)
2. ✅ Roles second (can reference permissions)
3. ✅ Users last (can reference roles)

**Never:**
- ❌ Create users before roles
- ❌ Create roles before permissions
- ❌ Delete permissions that are assigned to roles
- ❌ Delete roles that are assigned to users

### Password Security

All passwords in the scripts are **hashed** using Argon2:
- ✅ Never stored in plain text
- ✅ Secure hashing algorithm
- ✅ Salt automatically added

### Database Backups

Before running `init_database.py` (which drops tables):

```bash
# Backup PostgreSQL database
pg_dump -U postgres rbac > backup_$(date +%Y%m%d).sql

# Restore if needed
psql -U postgres rbac < backup_20251018.sql
```

---

## 📚 Additional Scripts

### Check Database Status

```bash
python3 -c "
from app.db.session import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission

db = SessionLocal()
print(f'Users: {db.query(User).count()}')
print(f'Roles: {db.query(Role).count()}')
print(f'Permissions: {db.query(Permission).count()}')
db.close()
"
```

### List All Users

```bash
python3 -c "
from app.db.session import SessionLocal
from app.models.user import User

db = SessionLocal()
users = db.query(User).all()
for user in users:
    print(f'{user.email} - {[r.name for r in user.roles]}')
db.close()
"
```

---

## 🎉 Success!

After running the scripts, you should have:
- ✅ 20 permissions
- ✅ 4 roles with proper permission assignments
- ✅ 4 users with proper role assignments
- ✅ All foreign key relationships intact
- ✅ Ready to test the API

**Next Steps:**
1. Start server: `uvicorn app.main:app --reload`
2. Visit: http://127.0.0.1:8000/docs
3. Login with: `admin@example.com` / `Admin123!`
4. Test all endpoints!

---

**Need Help?** Check the error messages and refer to the troubleshooting section above.
