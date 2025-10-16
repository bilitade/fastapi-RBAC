from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import Base, engine, get_db
from app.models import User, Role, Permission, RefreshToken as RefreshTokenModel
from app.schemas import UserCreate, RoleCreate, UserSchema, RoleSchema, TokenSchema, RefreshRequest
from app.auth import hash_password, verify_password, create_access_token, create_refresh_token, verify_refresh_token, hash_token
from datetime import datetime
from app.rbac import get_current_user, require_permission
from fastapi.security import OAuth2PasswordRequestForm

Base.metadata.create_all(bind=engine)
app = FastAPI()

# ----------------- AUTH -----------------
@app.post("/login", response_model=TokenSchema)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access = create_access_token({"sub": user.id})
    refresh = create_refresh_token({"sub": user.id})

    # persist refresh token hash for revocation/rotation
    rt_hash = hash_token(refresh)
    payload = verify_refresh_token(refresh)
    expires_at = None
    if payload:
        exp_val = payload.get("exp")
        if exp_val is not None:
            try:
                expires_at = datetime.utcfromtimestamp(int(exp_val))
            except Exception:
                expires_at = None

    db_rt = RefreshTokenModel(token_hash=rt_hash, user_id=user.id, revoked=False, expires_at=expires_at)
    db.add(db_rt)
    db.commit()
    db.refresh(db_rt)

    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


@app.post("/refresh", response_model=TokenSchema)
def refresh_token(req: RefreshRequest, db: Session = Depends(get_db)):
    refresh_token = req.refresh_token
    payload = verify_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")
    if user_id is not None:
        try:
            user_id = int(user_id)
        except Exception:
            pass

    # verify stored refresh token hash exists and not revoked
    rt_hash = hash_token(refresh_token)
    stored = db.query(RefreshTokenModel).filter(RefreshTokenModel.token_hash == rt_hash).first()
    if stored is None:
        raise HTTPException(status_code=401, detail="Refresh token revoked or not found")
    revoked_flag = getattr(stored, "revoked", False)
    if revoked_flag == True:
        raise HTTPException(status_code=401, detail="Refresh token revoked or not found")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # rotate: revoke current, create new refresh token and persist
    setattr(stored, "revoked", True)
    db.commit()

    new_refresh = create_refresh_token({"sub": user.id})
    new_rt_hash = hash_token(new_refresh)
    new_payload = verify_refresh_token(new_refresh)
    new_expires_at = None
    if new_payload:
        new_exp_val = new_payload.get("exp")
        if new_exp_val is not None:
            try:
                new_expires_at = datetime.utcfromtimestamp(int(new_exp_val))
            except Exception:
                new_expires_at = None

    new_db_rt = RefreshTokenModel(token_hash=new_rt_hash, user_id=user.id, revoked=False, expires_at=new_expires_at)
    db.add(new_db_rt)
    db.commit()
    db.refresh(new_db_rt)

    new_access = create_access_token({"sub": user.id})
    return {"access_token": new_access, "refresh_token": new_refresh, "token_type": "bearer"}


@app.post("/logout")
def logout(req: RefreshRequest, db: Session = Depends(get_db)):
    rt_hash = hash_token(req.refresh_token)
    stored = db.query(RefreshTokenModel).filter(RefreshTokenModel.token_hash == rt_hash).first()
    if stored:
        setattr(stored, "revoked", True)
        db.commit()
    return {"msg": "logged out"}

# ----------------- USERS -----------------
@app.post("/users/", response_model=UserSchema)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(email=user.email, password=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/me", response_model=UserSchema)
def read_me(user: User = Depends(get_current_user)):
    return user

# ----------------- ROLES -----------------
@app.post("/roles/", response_model=RoleSchema)
def create_role(role: RoleCreate, db: Session = Depends(get_db), allowed: bool = Depends(require_permission("manage_roles"))):
    new_role = Role(name=role.name)
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    # Assign permissions if provided
    if role.permissions:
        perms = db.query(Permission).filter(Permission.name.in_(role.permissions)).all()
        new_role.permissions = perms
        db.commit()
    return new_role
