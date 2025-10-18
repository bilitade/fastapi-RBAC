"""SQLAlchemy declarative base for all models."""
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def import_models() -> None:
    """Register all models with SQLAlchemy for table creation."""
    from app.models.user import User  # noqa: F401
    from app.models.role import Role  # noqa: F401
    from app.models.permission import Permission  # noqa: F401
    from app.models.token import RefreshToken  # noqa: F401
    from app.models.password_reset import PasswordResetToken  # noqa: F401

