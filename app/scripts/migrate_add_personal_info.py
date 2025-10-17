"""
Migration script to add personal information fields to users table.

Run this to upgrade from previous version.
"""
from sqlalchemy import text
from app.db.session import SessionLocal, engine


def migrate():
    """Add personal information columns to users table."""
    db = SessionLocal()
    try:
        with engine.connect() as conn:
            # Add first_name column
            try:
                conn.execute(text(
                    "ALTER TABLE users ADD COLUMN first_name VARCHAR(100)"
                ))
                conn.commit()
                print("✓ Added first_name column")
            except Exception as e:
                if "already exists" not in str(e).lower() and "duplicate column" not in str(e).lower():
                    print(f"⚠ Warning: {e}")
                else:
                    print("✓ first_name column already exists")
            
            # Add middle_name column
            try:
                conn.execute(text(
                    "ALTER TABLE users ADD COLUMN middle_name VARCHAR(100)"
                ))
                conn.commit()
                print("✓ Added middle_name column")
            except Exception as e:
                if "already exists" not in str(e).lower() and "duplicate column" not in str(e).lower():
                    print(f"⚠ Warning: {e}")
                else:
                    print("✓ middle_name column already exists")
            
            # Add last_name column
            try:
                conn.execute(text(
                    "ALTER TABLE users ADD COLUMN last_name VARCHAR(100)"
                ))
                conn.commit()
                print("✓ Added last_name column")
            except Exception as e:
                if "already exists" not in str(e).lower() and "duplicate column" not in str(e).lower():
                    print(f"⚠ Warning: {e}")
                else:
                    print("✓ last_name column already exists")
            
            # Add role_title column
            try:
                conn.execute(text(
                    "ALTER TABLE users ADD COLUMN role_title VARCHAR(100)"
                ))
                conn.commit()
                print("✓ Added role_title column")
            except Exception as e:
                if "already exists" not in str(e).lower() and "duplicate column" not in str(e).lower():
                    print(f"⚠ Warning: {e}")
                else:
                    print("✓ role_title column already exists")
        
        # Update existing users with default values
        from app.models.user import User
        users = db.query(User).all()
        
        update_count = 0
        for user in users:
            needs_update = False
            
            if not hasattr(user, 'first_name') or not user.first_name:
                user.first_name = "User"
                needs_update = True
            
            if not hasattr(user, 'middle_name') or not user.middle_name:
                user.middle_name = "M"
                needs_update = True
            
            if not hasattr(user, 'last_name') or not user.last_name:
                # Extract from email or use default
                email_name = user.email.split('@')[0].replace('.', ' ').title()
                user.last_name = email_name if email_name else "User"
                needs_update = True
            
            if needs_update:
                update_count += 1
        
        if update_count > 0:
            db.commit()
            print(f"✓ Updated {update_count} existing users with default names")
        else:
            print("✓ All users already have personal information")
        
        # Now make columns NOT NULL
        try:
            with engine.connect() as conn:
                conn.execute(text(
                    "ALTER TABLE users ALTER COLUMN first_name SET NOT NULL"
                ))
                conn.execute(text(
                    "ALTER TABLE users ALTER COLUMN middle_name SET NOT NULL"
                ))
                conn.execute(text(
                    "ALTER TABLE users ALTER COLUMN last_name SET NOT NULL"
                ))
                conn.commit()
                print("✓ Set name columns as NOT NULL")
        except Exception as e:
            print(f"⚠ Note: Could not set NOT NULL constraint: {e}")
        
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()

