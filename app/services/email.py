"""Email service for sending emails using FastAPI-Mail."""
from typing import List, Optional
from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class EmailConfig:
    """Email configuration wrapper."""
    
    @staticmethod
    def get_config() -> ConnectionConfig:
        """Get email connection configuration."""
        return ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
            MAIL_STARTTLS=settings.MAIL_STARTTLS,
            MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
            USE_CREDENTIALS=settings.USE_CREDENTIALS,
            VALIDATE_CERTS=settings.VALIDATE_CERTS,
            TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates" / "email"
        )


class EmailService:
    """Service for sending emails."""
    
    def __init__(self):
        """Initialize email service."""
        self.config = EmailConfig.get_config()
        self.fast_mail = FastMail(self.config)
    
    async def send_email(
        self,
        subject: str,
        recipients: List[EmailStr],
        body: str,
        subtype: MessageType = MessageType.html
    ) -> bool:
        """
        Send an email.
        
        Args:
            subject: Email subject
            recipients: List of recipient email addresses
            body: Email body content
            subtype: Message type (html or plain)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                body=body,
                subtype=subtype
            )
            
            await self.fast_mail.send_message(message)
            logger.info(f"Email sent successfully to {recipients}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {recipients}: {str(e)}")
            return False
    
    async def send_password_reset_email(
        self,
        email: EmailStr,
        token: str,
        user_name: str
    ) -> bool:
        """
        Send password reset email.
        
        Args:
            email: Recipient email address
            token: Password reset token
            user_name: User's name
            
        Returns:
            bool: True if email sent successfully
        """
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        
        subject = "Password Reset Request"
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 5px 5px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background-color: #4CAF50;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 12px;
                    color: #666;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 10px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <p>Hello {user_name},</p>
                    
                    <p>We received a request to reset your password. Click the button below to create a new password:</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_link}" class="button">Reset Password</a>
                    </div>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #4CAF50;">{reset_link}</p>
                    
                    <div class="warning">
                        <strong>⚠️ Security Notice:</strong>
                        <ul>
                            <li>This link will expire in {settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes</li>
                            <li>If you didn't request this reset, please ignore this email</li>
                            <li>Never share this link with anyone</li>
                        </ul>
                    </div>
                    
                    <div class="footer">
                        <p>This is an automated message from {settings.APP_NAME}. Please do not reply to this email.</p>
                        <p>If you have any questions, please contact our support team.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            subject=subject,
            recipients=[email],
            body=body,
            subtype=MessageType.html
        )
    
    async def send_password_changed_email(
        self,
        email: EmailStr,
        user_name: str
    ) -> bool:
        """
        Send password changed confirmation email.
        
        Args:
            email: Recipient email address
            user_name: User's name
            
        Returns:
            bool: True if email sent successfully
        """
        subject = "Password Changed Successfully"
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 5px 5px;
                }}
                .success {{
                    background-color: #d4edda;
                    border-left: 4px solid #28a745;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 10px;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✓ Password Changed</h1>
                </div>
                <div class="content">
                    <p>Hello {user_name},</p>
                    
                    <div class="success">
                        <strong>✓ Success!</strong> Your password has been changed successfully.
                    </div>
                    
                    <p>Your account password was recently updated. You can now use your new password to log in.</p>
                    
                    <div class="warning">
                        <strong>⚠️ Didn't make this change?</strong>
                        <p>If you didn't change your password, please contact our support team immediately and secure your account.</p>
                    </div>
                    
                    <div class="footer">
                        <p>This is an automated message from {settings.APP_NAME}. Please do not reply to this email.</p>
                        <p>If you have any questions, please contact our support team.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            subject=subject,
            recipients=[email],
            body=body,
            subtype=MessageType.html
        )
    
    async def send_welcome_email(
        self,
        email: EmailStr,
        user_name: str
    ) -> bool:
        """
        Send welcome email to new users.
        
        Args:
            email: Recipient email address
            user_name: User's name
            
        Returns:
            bool: True if email sent successfully
        """
        subject = f"Welcome to {settings.APP_NAME}!"
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 5px 5px;
                }}
                .footer {{
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to {settings.APP_NAME}! 🎉</h1>
                </div>
                <div class="content">
                    <p>Hello {user_name},</p>
                    
                    <p>Thank you for joining {settings.APP_NAME}! We're excited to have you on board.</p>
                    
                    <p>Your account has been successfully created and you can now access all features.</p>
                    
                    <p>If you have any questions or need assistance, please don't hesitate to reach out to our support team.</p>
                    
                    <div class="footer">
                        <p>Best regards,<br>The {settings.APP_NAME} Team</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            subject=subject,
            recipients=[email],
            body=body,
            subtype=MessageType.html
        )


# Singleton instance
email_service = EmailService()
