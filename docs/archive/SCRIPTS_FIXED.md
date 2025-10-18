# ✅ Database Scripts - All Fixed!

## 🎉 Both Scripts Now Working

### ✅ Script 1: `init_database.py` (Full Reset)
**Status:** Working perfectly ✅

**What it does:**
- Drops all tables with CASCADE
- Creates all tables fresh
- Populates with sample data

**Usage:**
```bash
python3 app/scripts/init_database.py
# or
python3 -m app.scripts.init_database
```

**Result:**
- 20 permissions
- 4 roles
- 5 users (including 1 inactive)

---

### ✅ Script 2: `populate_database.py` (Data Refresh)
**Status:** Fixed and working ✅

**What was wrong:**
- Missing imports for `PasswordResetToken` and `RefreshToken`
- Wrong deletion order (parent tables before child tables)

**What was fixed:**
1. Added missing imports
2. Fixed deletion order (child tables first)

**Usage:**
```bash
python3 app/scripts/populate_database.py
# or
python3 -m app.scripts.populate_database
```

**Result:**
- 20 permissions
- 4 roles
- 4 users (no inactive user in this script)

---

## 📊 Comparison

| Feature | init_database.py | populate_database.py |
|---------|------------------|---------------------|
| Drops tables | ✅ Yes (CASCADE) | ❌ No |
| Creates tables | ✅ Yes | ❌ No (assumes exist) |
| Clears data | ✅ Yes | ✅ Yes |
| Populates data | ✅ Yes | ✅ Yes |
| Users created | 5 (with inactive) | 4 (all active) |
| Use case | Fresh start | Quick refresh |

---

## 🚀 Which Script to Use?

### Use `init_database.py` when:
- ✅ First time setup
- ✅ You want to completely reset everything
- ✅ Tables are corrupted or have schema issues
- ✅ You want the inactive user for testing

### Use `populate_database.py` when:
- ✅ Tables already exist
- ✅ You just want to refresh the data
- ✅ You want to keep table structure
- ✅ Faster execution (no table recreation)

---

## 📝 Login Credentials

Both scripts create these users:

| Email | Password | Role | Status |
|-------|----------|------|--------|
| admin@example.com | Admin123! | admin | Active ✅ |
| manager@example.com | Manager123! | manager | Active ✅ |
| user@example.com | User123! | user | Active ✅ |
| guest@example.com | Guest123! | guest | Active ✅ |

**Note:** `init_database.py` also creates:
- inactive@example.com / Inactive123! (Inactive ❌)

---

## ✅ Verification

After running either script:

```bash
# Start server
uvicorn app.main:app --reload

# Visit Swagger UI
http://127.0.0.1:8000/docs

# Login with
admin@example.com / Admin123!
```

---

## 🔧 Technical Details

### Fixed Issues in populate_database.py

**Before (Broken):**
```python
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
# Missing imports!

def clear_existing_data(db):
    db.query(User).delete()  # Error: PasswordResetToken not found
```

**After (Fixed):**
```python
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.password_reset import PasswordResetToken  # Added
from app.models.token import RefreshToken  # Added

def clear_existing_data(db):
    # Delete child tables first
    db.query(PasswordResetToken).delete()
    db.query(RefreshToken).delete()
    db.query(User).delete()
    db.query(Role).delete()
    db.query(Permission).delete()
```

---

## 🎯 Success!

Both scripts are now fully functional and ready to use!

**Status:** ✅ **ALL SCRIPTS WORKING**

Choose the script that fits your needs and populate your database! 🚀
