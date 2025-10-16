"""Authentication endpoints for login, logout, and token refresh."""
from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.models.token import RefreshToken
from app.schemas.token import Token, RefreshRequest
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    hash_token,
)

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """Authenticate user and issue JWT tokens."""
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})
    
    token_hash = hash_token(refresh_token)
    payload = verify_refresh_token(refresh_token)
    
    expires_at = None
    if payload:
        exp_val = payload.get("exp")
        if exp_val is not None:
            try:
                expires_at = datetime.utcfromtimestamp(int(exp_val))
            except (ValueError, TypeError):
                expires_at = None
    
    db_refresh_token = RefreshToken(
        token_hash=token_hash,
        user_id=user.id,
        revoked=False,
        expires_at=expires_at
    )
    db.add(db_refresh_token)
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
def refresh(
    request: RefreshRequest,
    db: Session = Depends(get_db)
) -> Any:
    """Exchange refresh token for new tokens (implements rotation)."""
    payload = verify_refresh_token(request.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is not None:
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
    
    token_hash = hash_token(request.refresh_token)
    stored_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash
    ).first()
    
    if not stored_token or stored_token.revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token revoked or not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    stored_token.revoked = True
    db.commit()
    
    new_access_token = create_access_token({"sub": user.id})
    new_refresh_token = create_refresh_token({"sub": user.id})
    new_token_hash = hash_token(new_refresh_token)
    new_payload = verify_refresh_token(new_refresh_token)
    
    new_expires_at = None
    if new_payload:
        new_exp_val = new_payload.get("exp")
        if new_exp_val is not None:
            try:
                new_expires_at = datetime.utcfromtimestamp(int(new_exp_val))
            except (ValueError, TypeError):
                new_expires_at = None
    
    new_db_token = RefreshToken(
        token_hash=new_token_hash,
        user_id=user.id,
        revoked=False,
        expires_at=new_expires_at
    )
    db.add(new_db_token)
    db.commit()
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout")
def logout(
    request: RefreshRequest,
    db: Session = Depends(get_db)
) -> Any:
    """Revoke refresh token (access token remains valid until expiry)."""
    token_hash = hash_token(request.refresh_token)
    stored_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash
    ).first()
    
    if stored_token:
        stored_token.revoked = True
        db.commit()
    
    return {"message": "Successfully logged out"}

