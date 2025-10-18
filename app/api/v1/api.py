"""API v1 router aggregation."""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, roles, permissions, ai, files, password

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(password.router, prefix="/password", tags=["Password Management"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(permissions.router, prefix="/permissions", tags=["Permissions"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Assistant"])
api_router.include_router(files.router, prefix="/files", tags=["File Storage"])

