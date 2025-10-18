"""Create password_reset_tokens table."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.db.session import engine
from app.db.base import Base, import_models

def create_password_reset_table():
    """Create password_reset_tokens table if it doesn't exist."""
    print("Creating password_reset_tokens table...")
    
    # Import all models
    import_models()
    
    # Create only the password_reset_tokens table
    from app.models.password_reset import PasswordResetToken
    
    # Create table
    Base.metadata.create_all(bind=engine, tables=[PasswordResetToken.__table__])
    
    print("✓ password_reset_tokens table created successfully!")

if __name__ == "__main__":
    create_password_reset_table()
