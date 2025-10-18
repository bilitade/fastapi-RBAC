# Email & Password Management Guide

## 📧 Email Functionality

### Overview
The application includes a comprehensive email system using `fastapi-mail` for:
- Password reset emails
- Password change confirmations
- Welcome emails for new users
- Custom email notifications

### Features
- ✅ **HTML Email Templates** - Beautiful, responsive email designs
- ✅ **SMTP Support** - Works with Gmail, Outlook, SendGrid, etc.
- ✅ **Secure Configuration** - Credentials stored in environment variables
- ✅ **Error Handling** - Graceful failure with logging
- ✅ **Template System** - Easy to customize email templates

---

## 🔧 Email Configuration

### 1. Environment Variables

Add these to your `.env` file:

```bash
# Email Configuration
MAIL_USERNAME="your-email@gmail.com"
MAIL_PASSWORD="your-app-specific-password"
MAIL_FROM="noreply@example.com"
MAIL_FROM_NAME="RBAC API"
MAIL_PORT=587
MAIL_SERVER="smtp.gmail.com"
MAIL_STARTTLS=True
MAIL_SSL_TLS=False
USE_CREDENTIALS=True
VALIDATE_CERTS=True

# Password Reset
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES=30
FRONTEND_URL="http://localhost:3000"
```

### 2. Gmail Setup (Recommended for Development)

#### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account settings
2. Navigate to Security
3. Enable 2-Step Verification

#### Step 2: Generate App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and your device
3. Click "Generate"
4. Copy the 16-character password
5. Use this as `MAIL_PASSWORD` in your `.env` file

#### Step 3: Update Configuration
```bash
MAIL_USERNAME="your-email@gmail.com"
MAIL_PASSWORD="xxxx xxxx xxxx xxxx"  # App-specific password
MAIL_SERVER="smtp.gmail.com"
MAIL_PORT=587
MAIL_STARTTLS=True
```

### 3. Other Email Providers

#### Outlook/Office 365
```bash
MAIL_SERVER="smtp.office365.com"
MAIL_PORT=587
MAIL_STARTTLS=True
```

#### SendGrid
```bash
MAIL_SERVER="smtp.sendgrid.net"
MAIL_PORT=587
MAIL_USERNAME="apikey"
MAIL_PASSWORD="your-sendgrid-api-key"
```

#### Amazon SES
```bash
MAIL_SERVER="email-smtp.us-east-1.amazonaws.com"
MAIL_PORT=587
MAIL_USERNAME="your-smtp-username"
MAIL_PASSWORD="your-smtp-password"
```

---

## 🔐 Password Management Features

### 1. Password Reset Flow

#### Request Password Reset
```bash
POST /api/v1/password/request-reset
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "If the email exists, a password reset link has been sent",
  "email": "user@example.com"
}
```

**Security Features:**
- ✅ Returns same response whether email exists or not (prevents email enumeration)
- ✅ Invalidates previous unused tokens
- ✅ Token expires in 30 minutes (configurable)
- ✅ Token is hashed before storage (SHA256)

#### Reset Password
```bash
POST /api/v1/password/reset-password
Content-Type: application/json

{
  "token": "reset-token-from-email",
  "new_password": "NewSecurePass123!"
}
```

**Response:**
```json
{
  "message": "Password has been reset successfully. Please log in with your new password."
}
```

**Security Features:**
- ✅ Token is single-use
- ✅ Token expires after configured time
- ✅ All refresh tokens are invalidated (forces re-login)
- ✅ Confirmation email sent

### 2. Password Change (Authenticated)

```bash
POST /api/v1/password/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_password": "OldPassword123!",
  "new_password": "NewSecurePass123!"
}
```

**Response:**
```json
{
  "message": "Password has been changed successfully. Please log in again with your new password."
}
```

**Security Features:**
- ✅ Requires authentication
- ✅ Verifies current password
- ✅ Prevents reusing current password
- ✅ All refresh tokens invalidated (forces re-login)
- ✅ Confirmation email sent

### 3. Password Requirements

All passwords must meet these criteria:
- ✅ Minimum 8 characters
- ✅ At least one uppercase letter (A-Z)
- ✅ At least one lowercase letter (a-z)
- ✅ At least one digit (0-9)

**Example Valid Passwords:**
- `SecurePass123!`
- `MyP@ssw0rd`
- `Admin2024!`

**Example Invalid Passwords:**
- `password` (no uppercase, no digit)
- `PASSWORD123` (no lowercase)
- `Password` (no digit)
- `Pass1` (too short)

---

## 📨 Email Templates

### Password Reset Email

The password reset email includes:
- User's name
- Reset link button
- Plain text link (for email clients that don't support HTML)
- Expiration time warning
- Security notice
- Professional styling

### Password Changed Email

The confirmation email includes:
- Success message
- Security warning (if user didn't make the change)
- Contact information
- Professional styling

### Welcome Email

Sent to new users with:
- Welcome message
- Getting started information
- Support contact details

---

## 🔒 Security Best Practices

### 1. Token Security
- **Tokens are hashed** before storage (SHA256)
- **Single-use tokens** - marked as used after reset
- **Time-limited** - expire after 30 minutes (configurable)
- **Automatic cleanup** - old tokens invalidated

### 2. Email Enumeration Prevention
- Same response for existing and non-existing emails
- No indication whether email is registered
- Prevents attackers from discovering valid emails

### 3. Session Management
- All refresh tokens invalidated after password change
- Forces re-authentication with new password
- Prevents unauthorized access with old sessions

### 4. Password Validation
- Strong password requirements enforced
- Cannot reuse current password
- Current password verification required for changes

---

## 🧪 Testing Email Functionality

### 1. Development Testing

For development, use a test email service like:

#### Mailtrap (Recommended)
```bash
MAIL_SERVER="smtp.mailtrap.io"
MAIL_PORT=2525
MAIL_USERNAME="your-mailtrap-username"
MAIL_PASSWORD="your-mailtrap-password"
```

#### MailHog (Local)
```bash
MAIL_SERVER="localhost"
MAIL_PORT=1025
USE_CREDENTIALS=False
```

### 2. Test Password Reset Flow

```bash
# 1. Request password reset
curl -X POST http://localhost:8000/api/v1/password/request-reset \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# 2. Check email for reset link

# 3. Reset password
curl -X POST http://localhost:8000/api/v1/password/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "token": "token-from-email",
    "new_password": "NewPassword123!"
  }'
```

### 3. Test Password Change

```bash
# 1. Login to get access token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=CurrentPass123!" \
  | jq -r '.access_token')

# 2. Change password
curl -X POST http://localhost:8000/api/v1/password/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "CurrentPass123!",
    "new_password": "NewPassword123!"
  }'
```

---

## 📊 Database Schema

### PasswordResetToken Table

```sql
CREATE TABLE password_reset_tokens (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    token_hash VARCHAR(64) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_token_hash ON password_reset_tokens(token_hash);
```

---

## 🎨 Customizing Email Templates

### Modify Email Content

Edit `/app/services/email.py`:

```python
async def send_password_reset_email(
    self,
    email: EmailStr,
    token: str,
    user_name: str
) -> bool:
    # Customize the HTML body here
    body = f"""
    <!DOCTYPE html>
    <html>
    <!-- Your custom HTML template -->
    </html>
    """
    
    return await self.send_email(...)
```

### Add New Email Types

```python
async def send_custom_email(
    self,
    email: EmailStr,
    custom_data: dict
) -> bool:
    """Send a custom email."""
    subject = "Custom Subject"
    body = f"""
    <!-- Your custom template -->
    """
    
    return await self.send_email(
        subject=subject,
        recipients=[email],
        body=body,
        subtype=MessageType.html
    )
```

---

## 🚀 Production Deployment

### 1. Use Production Email Service

Recommended services:
- **SendGrid** - 100 emails/day free
- **Amazon SES** - Very low cost
- **Mailgun** - 5,000 emails/month free
- **Postmark** - Reliable transactional emails

### 2. Environment Configuration

```bash
# Production .env
MAIL_SERVER="smtp.sendgrid.net"
MAIL_PORT=587
MAIL_USERNAME="apikey"
MAIL_PASSWORD="your-production-api-key"
MAIL_FROM="noreply@yourdomain.com"
MAIL_FROM_NAME="Your App Name"
FRONTEND_URL="https://yourdomain.com"
```

### 3. Security Checklist

- [ ] Use environment variables for credentials
- [ ] Enable SSL/TLS for SMTP
- [ ] Use app-specific passwords (not account password)
- [ ] Set appropriate token expiration times
- [ ] Monitor email sending failures
- [ ] Set up email rate limiting
- [ ] Configure SPF, DKIM, and DMARC records

---

## 📚 API Documentation

All password endpoints are documented in the interactive API docs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Navigate to the "Password Management" section to see:
- Request/response schemas
- Example payloads
- Try out the endpoints

---

## 🐛 Troubleshooting

### Email Not Sending

**Check logs:**
```bash
# Look for email service errors
tail -f logs/app.log | grep email
```

**Common issues:**
1. **Invalid credentials** - Check MAIL_USERNAME and MAIL_PASSWORD
2. **Firewall blocking** - Ensure port 587 is open
3. **2FA not enabled** - Required for Gmail app passwords
4. **Wrong SMTP server** - Verify MAIL_SERVER setting

### Password Reset Token Invalid

**Possible causes:**
1. Token expired (30 minutes default)
2. Token already used
3. Token not found in database
4. User account inactive

**Solution:**
Request a new password reset token

### Password Validation Errors

**Common errors:**
- "Password must be at least 8 characters long"
- "Password must contain at least one uppercase letter"
- "Password must contain at least one lowercase letter"
- "Password must contain at least one digit"

**Solution:**
Ensure password meets all requirements

---

## 📖 Code Examples

### Send Custom Email

```python
from app.services.email import email_service

# Send custom email
await email_service.send_email(
    subject="Custom Subject",
    recipients=["user@example.com"],
    body="<h1>Hello!</h1><p>Custom message</p>",
    subtype=MessageType.html
)
```

### Check Email Configuration

```python
from app.config import settings

print(f"Email Server: {settings.MAIL_SERVER}")
print(f"Email Port: {settings.MAIL_PORT}")
print(f"From: {settings.MAIL_FROM}")
```

---

## ✅ Summary

Your application now includes:

### Email Features
- ✅ Professional HTML email templates
- ✅ Password reset emails
- ✅ Password change confirmations
- ✅ Welcome emails
- ✅ Configurable SMTP settings
- ✅ Error handling and logging

### Password Features
- ✅ Password reset flow (unauthenticated)
- ✅ Password change (authenticated)
- ✅ Strong password validation
- ✅ Secure token management
- ✅ Session invalidation on password change
- ✅ Email confirmations

### Security
- ✅ Email enumeration prevention
- ✅ Token hashing (SHA256)
- ✅ Single-use tokens
- ✅ Time-limited tokens
- ✅ Session management
- ✅ Audit logging

**Your email and password management system is production-ready!** 🎉
