"""
Production-ready RBAC API with JWT authentication and permission-based authorization.

Features:
- JWT authentication with refresh token rotation
- Fine-grained permission system
- RESTful API with versioning
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.config import settings
from app.api.v1.api import api_router
from app.db.base import Base, import_models
from app.db.session import engine
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

# Register all models with SQLAlchemy
import_models()
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## RBAC API - Authentication & Authorization System
    
    **Authentication**: JWT tokens with automatic rotation  
    **Authorization**: Role and permission-based access control  
    **Resources**: Users, Roles, Permissions
    
    ### Quick Start
    1. Login at `/api/v1/auth/login` with email/password
    2. Use returned `access_token` in Authorization header: `Bearer <token>`
    3. Refresh tokens at `/api/v1/auth/refresh` when expired
    
    ### Authorization Model
    Users → Roles → Permissions → Endpoints
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Security middleware (order matters - first added is executed last)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers to all responses
app.add_middleware(SecurityHeadersMiddleware)

# Add rate limiting to prevent brute force attacks
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=60,  # General rate limit
    requests_per_hour=1000
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", include_in_schema=False)
async def root():
    """Redirect to API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["Health"])
async def health_check():
    """Service health check."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
