from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ✅ Fix 1: Typo in "sqlite" and proper DB URL format
# DATABASE_URL = "postgresql+psycopg2://bilisuma:12345678@localhost:5432/rbac"
# DATABASE_URL = "sqlite:///./test.db"
DATABASE_URL="postgresql+psycopg2://postgres:12345678@localhost:5432/rbac"

# ✅ Fix 2: For SQLite, connect_args must include `check_same_thread`
engine = create_engine(
    DATABASE_URL
)

# ✅ Session configuration
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

# ✅ Declarative base setup
Base = declarative_base()

# ✅ Add common schema base for Postgres, ignored by SQLite
class BaseModel(Base):
    __abstract__ = True
    __table_args__ = {"schema": "rbac"}

# ✅ Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
