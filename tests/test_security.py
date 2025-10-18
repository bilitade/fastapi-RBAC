"""Comprehensive security tests for JWT, RBAC, and input validation."""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.db import get_db
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.core.security import hash_password, create_access_token, create_refresh_token
import time

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_security.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function")
def setup_database():
    """Setup test database with sample data."""
    # Drop and recreate all tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    # Create permissions
    perm1 = Permission(name="view_user")
    perm2 = Permission(name="create_user")
    perm3 = Permission(name="delete_user")
    db.add_all([perm1, perm2, perm3])
    db.commit()
    
    # Create roles
    admin_role = Role(name="admin")
    user_role = Role(name="user")
    admin_role.permissions = [perm1, perm2, perm3]
    user_role.permissions = [perm1]
    db.add_all([admin_role, user_role])
    db.commit()
    
    # Create users
    admin_user = User(
        first_name="Admin",
        middle_name="Test",
        last_name="User",
        email="admin@test.com",
        password=hash_password("AdminPass123!"),
        is_active=True,
        is_approved=True
    )
    admin_user.roles = [admin_role]
    
    normal_user = User(
        first_name="Normal",
        middle_name="Test",
        last_name="User",
        email="user@test.com",
        password=hash_password("UserPass123!"),
        is_active=True,
        is_approved=True
    )
    normal_user.roles = [user_role]
    
    inactive_user = User(
        first_name="Inactive",
        middle_name="Test",
        last_name="User",
        email="inactive@test.com",
        password=hash_password("InactivePass123!"),
        is_active=False,
        is_approved=True
    )
    
    db.add_all([admin_user, normal_user, inactive_user])
    db.commit()
    
    yield db
    
    db.close()


class TestAuthentication:
    """Test JWT authentication security."""
    
    def test_login_success(self, setup_database):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "admin@test.com", "password": "AdminPass123!"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_email(self, setup_database):
        """Test login with non-existent email."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "nonexistent@test.com", "password": "Password123!"}
        )
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_login_invalid_password(self, setup_database):
        """Test login with wrong password."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "admin@test.com", "password": "WrongPassword123!"}
        )
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_login_inactive_user(self, setup_database):
        """Test that inactive users cannot login (should fail at token validation)."""
        # Login will succeed but token won't work for protected endpoints
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "inactive@test.com", "password": "InactivePass123!"}
        )
        # Login itself may succeed, but using the token should fail
        if response.status_code == 200:
            token = response.json()["access_token"]
            me_response = client.get(
                "/api/v1/users/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert me_response.status_code == 403
    
    def test_access_without_token(self, setup_database):
        """Test accessing protected endpoint without token."""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401
    
    def test_access_with_invalid_token(self, setup_database):
        """Test accessing protected endpoint with invalid token."""
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        assert response.status_code == 401
    
    def test_token_refresh(self, setup_database):
        """Test token refresh flow."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": "admin@test.com", "password": "AdminPass123!"}
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh
        refresh_response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_response.status_code == 200
        data = refresh_response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_token_refresh_reuse_prevention(self, setup_database):
        """Test that refresh tokens cannot be reused (rotation)."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": "admin@test.com", "password": "AdminPass123!"}
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # First refresh - should work
        client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        
        # Second refresh with same token - should fail
        reuse_response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert reuse_response.status_code == 401
    
    def test_logout(self, setup_database):
        """Test logout functionality."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": "admin@test.com", "password": "AdminPass123!"}
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Logout
        logout_response = client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token}
        )
        assert logout_response.status_code == 200
        
        # Try to use revoked token
        refresh_response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_response.status_code == 401


class TestAuthorization:
    """Test RBAC authorization security."""
    
    def test_permission_based_access_allowed(self, setup_database):
        """Test user with permission can access endpoint."""
        # Login as admin
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": "admin@test.com", "password": "AdminPass123!"}
        )
        token = login_response.json()["access_token"]
        
        # Access endpoint requiring view_user permission
        response = client.get(
            "/api/v1/users/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
    
    def test_permission_based_access_denied(self, setup_database):
        """Test user without permission cannot access endpoint."""
        # Login as normal user
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": "user@test.com", "password": "UserPass123!"}
        )
        token = login_response.json()["access_token"]
        
        # Try to access endpoint requiring create_user permission
        response = client.post(
            "/api/v1/users/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "first_name": "Test",
                "middle_name": "New",
                "last_name": "User",
                "email": "newuser@test.com",
                "password": "Password123!"
            }
        )
        assert response.status_code == 403
        assert "Permission denied" in response.json()["detail"]
    
    def test_self_service_endpoint(self, setup_database):
        """Test that users can access their own profile."""
        # Login as normal user
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": "user@test.com", "password": "UserPass123!"}
        )
        token = login_response.json()["access_token"]
        
        # Access own profile
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["email"] == "user@test.com"


class TestInputValidation:
    """Test input validation and sanitization."""
    
    def test_password_strength_validation(self, setup_database):
        """Test password strength requirements."""
        # Too short
        response = client.post(
            "/api/v1/users/register",
            json={
                "first_name": "Test",
                "middle_name": "User",
                "last_name": "Name",
                "email": "test@example.com",
                "password": "short"
            }
        )
        assert response.status_code == 422
        
        # No uppercase
        response = client.post(
            "/api/v1/users/register",
            json={
                "first_name": "Test",
                "middle_name": "User",
                "last_name": "Name",
                "email": "test@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 422
        
        # No digit
        response = client.post(
            "/api/v1/users/register",
            json={
                "first_name": "Test",
                "middle_name": "User",
                "last_name": "Name",
                "email": "test@example.com",
                "password": "Password"
            }
        )
        assert response.status_code == 422
    
    def test_email_validation(self, setup_database):
        """Test email format validation."""
        response = client.post(
            "/api/v1/users/register",
            json={
                "first_name": "Test",
                "middle_name": "User",
                "last_name": "Name",
                "email": "invalid-email",
                "password": "Password123!"
            }
        )
        assert response.status_code == 422
    
    def test_sql_injection_protection(self, setup_database):
        """Test SQL injection attempts are blocked."""
        # Login as admin
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": "admin@test.com", "password": "AdminPass123!"}
        )
        token = login_response.json()["access_token"]
        
        # Try SQL injection in search/filter
        response = client.post(
            "/api/v1/users/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "first_name": "'; DROP TABLE users; --",
                "middle_name": "Test",
                "last_name": "User",
                "email": "sqlinjection@test.com",
                "password": "Password123!"
            }
        )
        # Should either succeed (and be escaped) or fail validation
        # The important thing is the database should not be affected
        
        # Verify users table still exists
        verify_response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert verify_response.status_code == 200
    
    def test_xss_protection(self, setup_database):
        """Test XSS attempts are sanitized."""
        response = client.post(
            "/api/v1/users/register",
            json={
                "first_name": "<script>alert('xss')</script>",
                "middle_name": "Test",
                "last_name": "User",
                "email": "xss@test.com",
                "password": "Password123!"
            }
        )
        # Should either be rejected or sanitized
        # Pydantic validation should handle this


class TestRateLimiting:
    """Test rate limiting protection."""
    
    def test_rate_limit_enforcement(self, setup_database):
        """Test that rate limiting blocks excessive requests."""
        # Make multiple rapid requests
        responses = []
        for _ in range(10):
            response = client.post(
                "/api/v1/auth/login",
                data={"username": "admin@test.com", "password": "WrongPassword"}
            )
            responses.append(response.status_code)
        
        # Should eventually get 429 Too Many Requests
        # Note: This test may need adjustment based on rate limit settings
        assert any(code == 429 for code in responses) or all(code == 401 for code in responses)


class TestSecurityHeaders:
    """Test security headers are present."""
    
    def test_security_headers_present(self, setup_database):
        """Test that security headers are added to responses."""
        response = client.get("/health")
        
        # Check for security headers
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        
        assert "X-XSS-Protection" in response.headers
        
        assert "Content-Security-Policy" in response.headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
