# Quick Start: Email & Password Features

## 🚀 5-Minute Setup

### Step 1: Install Dependencies

```bash
pip install fastapi-mail
```

Or update all dependencies:

```bash
pip install -r requirements.txt
```

### Step 2: Configure Email (Gmail Example)

1. **Enable 2-Factor Authentication** on your Gmail account

2. **Generate App Password:**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Click "Generate"
   - Copy the 16-character password

3. **Update `.env` file:**

```bash
# Email Configuration
MAIL_USERNAME="your-email@gmail.com"
MAIL_PASSWORD="xxxx xxxx xxxx xxxx"  # Your app password
MAIL_FROM="noreply@example.com"
MAIL_FROM_NAME="RBAC API"
MAIL_SERVER="smtp.gmail.com"
MAIL_PORT=587
MAIL_STARTTLS=True

# Password Reset
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES=30
FRONTEND_URL="http://localhost:3000"
```

### Step 3: Create Database Table

```bash
python3 app/scripts/create_password_reset_table.py
```

### Step 4: Start the Server

```bash
uvicorn app.main:app --reload
```

### Step 5: Test the Features

#### Test Password Reset

```bash
# 1. Request password reset
curl -X POST http://localhost:8000/api/v1/password/request-reset \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# 2. Check your email for the reset link

# 3. Reset password (use token from email)
curl -X POST http://localhost:8000/api/v1/password/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "token": "your-token-from-email",
    "new_password": "NewPassword123!"
  }'
```

#### Test Password Change (Authenticated)

```bash
# 1. Login first
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=CurrentPass123!"

# 2. Change password (use access_token from login)
curl -X POST http://localhost:8000/api/v1/password/change-password \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "CurrentPass123!",
    "new_password": "NewPassword123!"
  }'
```

---

## 📚 API Endpoints

### Password Reset (Unauthenticated)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/password/request-reset` | POST | Request password reset email |
| `/api/v1/password/reset-password` | POST | Reset password with token |

### Password Change (Authenticated)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/password/change-password` | POST | Change password (requires auth) |

---

## 🎨 Interactive API Docs

Visit http://localhost:8000/docs to:
- View all endpoints
- See request/response schemas
- Test endpoints directly in browser
- View password requirements

---

## 🔒 Security Features

### Password Requirements
- ✅ Minimum 8 characters
- ✅ At least one uppercase letter
- ✅ At least one lowercase letter
- ✅ At least one digit

### Token Security
- ✅ Tokens hashed with SHA256
- ✅ Single-use tokens
- ✅ 30-minute expiration (configurable)
- ✅ Automatic cleanup of old tokens

### Email Security
- ✅ No email enumeration (same response for all emails)
- ✅ Secure token generation (32 bytes)
- ✅ Session invalidation on password change

---

## 📧 Email Templates

The system includes beautiful HTML email templates for:

1. **Password Reset Email**
   - Professional design
   - Clear call-to-action button
   - Security warnings
   - Expiration notice

2. **Password Changed Confirmation**
   - Success notification
   - Security alert if unauthorized
   - Support contact info

3. **Welcome Email**
   - Friendly greeting
   - Getting started info
   - Support details

---

## 🧪 Development Testing

### Use Mailtrap for Testing

Instead of real email, use Mailtrap for development:

```bash
# Sign up at https://mailtrap.io (free)
# Get your credentials and update .env:

MAIL_SERVER="smtp.mailtrap.io"
MAIL_PORT=2525
MAIL_USERNAME="your-mailtrap-username"
MAIL_PASSWORD="your-mailtrap-password"
```

All emails will be captured in Mailtrap's inbox without being sent to real users.

---

## 🐛 Troubleshooting

### Email Not Sending?

**Check:**
1. MAIL_USERNAME and MAIL_PASSWORD are correct
2. 2FA is enabled on Gmail
3. Using app-specific password (not account password)
4. Port 587 is not blocked by firewall
5. Check application logs for errors

**View logs:**
```bash
# Check for email errors
tail -f logs/app.log | grep -i email
```

### Password Reset Token Invalid?

**Possible causes:**
1. Token expired (30 minutes)
2. Token already used
3. Wrong token copied from email

**Solution:**
Request a new password reset

---

## 📖 Full Documentation

For complete documentation, see:
- **[EMAIL_PASSWORD_GUIDE.md](EMAIL_PASSWORD_GUIDE.md)** - Complete guide
- **[SECURITY_BEST_PRACTICES.md](SECURITY_BEST_PRACTICES.md)** - Security guidelines
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Production deployment

---

## ✅ Checklist

- [ ] Install `fastapi-mail` package
- [ ] Configure email settings in `.env`
- [ ] Set up Gmail app password (or other SMTP)
- [ ] Create password_reset_tokens table
- [ ] Test password reset flow
- [ ] Test password change flow
- [ ] Review email templates
- [ ] Configure frontend URL
- [ ] Test in development (Mailtrap)
- [ ] Configure production email service

---

**You're all set! 🎉**

Your application now has professional email and password management features!
