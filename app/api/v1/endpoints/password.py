"""Password management endpoints (reset and change)."""
from typing import Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.schemas.password import (
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChange,
    PasswordResetResponse,
    PasswordChangeResponse
)
from app.core.security import hash_password, verify_password, hash_token
from app.core.dependencies import get_current_user
from app.services.email import email_service
from app.config import settings
import secrets
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def generate_reset_token() -> str:
    """Generate a secure random token for password reset."""
    return secrets.token_urlsafe(32)


@router.post("/request-reset", response_model=PasswordResetResponse, status_code=status.HTTP_200_OK)
async def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Request a password reset email.
    
    - **email**: User's email address
    
    Returns a success message regardless of whether the email exists (security best practice).
    """
    # Always return success to prevent email enumeration
    response_message = "If the email exists, a password reset link has been sent"
    
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        logger.warning(f"Password reset requested for non-existent email: {request.email}")
        return PasswordResetResponse(message=response_message, email=request.email)
    
    if not user.is_active:
        logger.warning(f"Password reset requested for inactive user: {request.email}")
        return PasswordResetResponse(message=response_message, email=request.email)
    
    # Generate reset token
    reset_token = generate_reset_token()
    token_hash = hash_token(reset_token)
    
    # Calculate expiration
    expires_at = datetime.utcnow() + timedelta(
        minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
    )
    
    # Invalidate any existing unused tokens for this user
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used == False
    ).update({"used": True})
    
    # Create new reset token
    reset_token_record = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at
    )
    db.add(reset_token_record)
    db.commit()
    
    # Send reset email
    user_name = f"{user.first_name} {user.last_name}"
    email_sent = await email_service.send_password_reset_email(
        email=user.email,
        token=reset_token,
        user_name=user_name
    )
    
    if not email_sent:
        logger.error(f"Failed to send password reset email to {user.email}")
        # Don't reveal this to the user for security
    else:
        logger.info(f"Password reset email sent to {user.email}")
    
    return PasswordResetResponse(message=response_message, email=request.email)


@router.post("/reset-password", response_model=PasswordChangeResponse, status_code=status.HTTP_200_OK)
async def reset_password(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db)
) -> Any:
    """
    Reset password using a valid reset token.
    
    - **token**: Password reset token from email
    - **new_password**: New password (min 8 chars, must include uppercase, lowercase, and digit)
    """
    # Hash the provided token
    token_hash = hash_token(request.token)
    
    # Find the reset token
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash,
        PasswordResetToken.used == False
    ).first()
    
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Check if token has expired
    if datetime.utcnow() > reset_token.expires_at:
        reset_token.used = True
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired. Please request a new one."
        )
    
    # Get the user
    user = db.query(User).filter(User.id == reset_token.user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive"
        )
    
    # Update password
    user.password = hash_password(request.new_password)
    
    # Mark token as used
    reset_token.used = True
    
    # Invalidate all refresh tokens for security
    from app.models.token import RefreshToken
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id
    ).update({"revoked": True})
    
    db.commit()
    
    # Send confirmation email
    user_name = f"{user.first_name} {user.last_name}"
    await email_service.send_password_changed_email(
        email=user.email,
        user_name=user_name
    )
    
    logger.info(f"Password reset successful for user: {user.email}")
    
    return PasswordChangeResponse(
        message="Password has been reset successfully. Please log in with your new password."
    )


@router.post("/change-password", response_model=PasswordChangeResponse, status_code=status.HTTP_200_OK)
async def change_password(
    request: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Change password (requires authentication and current password).
    
    - **current_password**: Current password for verification
    - **new_password**: New password (min 8 chars, must include uppercase, lowercase, and digit)
    
    Requires authentication.
    """
    # Verify current password
    if not verify_password(request.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Check if new password is same as current
    if verify_password(request.new_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Update password
    current_user.password = hash_password(request.new_password)
    
    # Invalidate all refresh tokens for security (force re-login)
    from app.models.token import RefreshToken
    db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id
    ).update({"revoked": True})
    
    db.commit()
    
    # Send confirmation email
    user_name = f"{current_user.first_name} {current_user.last_name}"
    await email_service.send_password_changed_email(
        email=current_user.email,
        user_name=user_name
    )
    
    logger.info(f"Password changed successfully for user: {current_user.email}")
    
    return PasswordChangeResponse(
        message="Password has been changed successfully. Please log in again with your new password."
    )
