from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.db import get_db
from app.models import User
from app.auth import verify_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    # "sub" might be encoded as str or int; normalize to int when possible
    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Try to coerce to int when possible (tokens sometimes encode IDs as strings)
    try:
        user_id = int(sub) if not isinstance(sub, int) else sub
    except (TypeError, ValueError):
        user_id = sub

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_permission(permission_name: str):
    def permission_checker(user: User = Depends(get_current_user)):
        user_permissions = {perm.name for role in user.roles for perm in role.permissions}
        if permission_name not in user_permissions:
            raise HTTPException(status_code=403, detail="Permission denied")
        return True
    return permission_checker
