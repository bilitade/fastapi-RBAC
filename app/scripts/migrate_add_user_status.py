"""
Migration script to add is_active and is_approved fields to existing users.

Run this once if you're upgrading from the old version.
"""
from sqlalchemy import text
from app.db.session import SessionLocal, engine


def migrate():
    """Add new columns to users table for existing databases."""
    db = SessionLocal()
    try:
        # Check if columns already exist
        with engine.connect() as conn:
            # Try adding is_active column
            try:
                conn.execute(text(
                    "ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE NOT NULL"
                ))
                conn.commit()
                print("✓ Added is_active column")
            except Exception as e:
                if "already exists" not in str(e).lower() and "duplicate column" not in str(e).lower():
                    print(f"⚠ Warning: {e}")
                else:
                    print("✓ is_active column already exists")
            
            # Try adding is_approved column
            try:
                conn.execute(text(
                    "ALTER TABLE users ADD COLUMN is_approved BOOLEAN DEFAULT FALSE NOT NULL"
                ))
                conn.commit()
                print("✓ Added is_approved column")
            except Exception as e:
                if "already exists" not in str(e).lower() and "duplicate column" not in str(e).lower():
                    print(f"⚠ Warning: {e}")
                else:
                    print("✓ is_approved column already exists")
        
        # Set existing users to approved
        from app.models.user import User
        users = db.query(User).all()
        for user in users:
            user.is_active = True
            user.is_approved = True
        db.commit()
        print(f"✓ Updated {len(users)} existing users to active and approved")
        
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()

