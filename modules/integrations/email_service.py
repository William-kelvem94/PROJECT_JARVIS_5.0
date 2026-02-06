"""
Email Service Integration
Provides email sending capabilities
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List


class EmailService:
    """
    Email service for sending emails.
    
    Features:
    - Send plain text emails
    - Send HTML emails
    - Multiple recipients
    - Attachments support
    """
    
    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        email_address: Optional[str] = None,
        email_password: Optional[str] = None
    ):
        """
        Initialize email service.
        
        Args:
            smtp_server: SMTP server address (or use EMAIL_SMTP_SERVER env var)
            smtp_port: SMTP server port (or use EMAIL_SMTP_PORT env var)
            email_address: Sender email address (or use EMAIL_ADDRESS env var)
            email_password: Email password/app password (or use EMAIL_PASSWORD env var)
        """
        self.smtp_server = smtp_server or os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('EMAIL_SMTP_PORT', '587'))
        self.email_address = email_address or os.getenv('EMAIL_ADDRESS', '')
        self.email_password = email_password or os.getenv('EMAIL_PASSWORD', '')
        
        self.is_available = bool(self.email_address and self.email_password)
        
        if not self.is_available:
            print("[Email] ⚠ Email credentials not configured")
            print("[Email] Set EMAIL_ADDRESS and EMAIL_PASSWORD environment variables")
            print("[Email] For Gmail, use App Password: https://support.google.com/accounts/answer/185833")
        else:
            print(f"[Email] ✓ Email service initialized ({self.email_address})")
    
    def send_email(
        self,
        to_address: str,
        subject: str,
        body: str,
        html: bool = False
    ) -> bool:
        """
        Send an email.
        
        Args:
            to_address: Recipient email address
            subject: Email subject
            body: Email body content
            html: If True, send as HTML email
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available:
            print("[Email] Service not available - credentials not configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to_address
            msg['Subject'] = subject
            
            # Attach body
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Secure connection
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            print(f"[Email] ✓ Email sent to {to_address}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("[Email] ✗ Authentication failed - check credentials")
            return False
        except smtplib.SMTPException as e:
            print(f"[Email] ✗ SMTP error: {e}")
            return False
        except Exception as e:
            print(f"[Email] ✗ Error sending email: {e}")
            return False
    
    def send_email_multiple(
        self,
        to_addresses: List[str],
        subject: str,
        body: str,
        html: bool = False
    ) -> Dict[str, bool]:
        """
        Send email to multiple recipients.
        
        Args:
            to_addresses: List of recipient email addresses
            subject: Email subject
            body: Email body content
            html: If True, send as HTML email
            
        Returns:
            Dictionary mapping email addresses to success status
        """
        results = {}
        for to_address in to_addresses:
            results[to_address] = self.send_email(to_address, subject, body, html)
        return results
    
    def send_quick_email(self, to_address: str, message: str) -> bool:
        """
        Send a quick email with minimal parameters.
        
        Args:
            to_address: Recipient email address
            message: Message to send (becomes both subject and body)
            
        Returns:
            True if successful, False otherwise
        """
        subject = f"Message from JARVIS"
        return self.send_email(to_address, subject, message)
    
    def test_connection(self) -> bool:
        """
        Test SMTP connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        if not self.is_available:
            return False
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
            print("[Email] ✓ Connection test successful")
            return True
        except Exception as e:
            print(f"[Email] ✗ Connection test failed: {e}")
            return False


# Configuration examples for common providers
EMAIL_CONFIGS = {
    'gmail': {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'notes': 'Use App Password, not regular password. Enable 2FA first.'
    },
    'outlook': {
        'smtp_server': 'smtp-mail.outlook.com',
        'smtp_port': 587,
        'notes': 'Use your regular Outlook password.'
    },
    'yahoo': {
        'smtp_server': 'smtp.mail.yahoo.com',
        'smtp_port': 587,
        'notes': 'Use App Password. Generate at account.yahoo.com/account/security'
    },
    'office365': {
        'smtp_server': 'smtp.office365.com',
        'smtp_port': 587,
        'notes': 'Use your Office 365 credentials.'
    }
}


# Example usage
if __name__ == "__main__":
    # Initialize
    email_service = EmailService()
    
    if email_service.is_available:
        # Test connection
        print("\n=== Testing Connection ===")
        if email_service.test_connection():
            print("✓ Email service ready to send emails")
            
            # Example: Send test email (uncomment to actually send)
            # print("\n=== Sending Test Email ===")
            # success = email_service.send_email(
            #     to_address="recipient@example.com",
            #     subject="Test from JARVIS",
            #     body="This is a test email sent by JARVIS assistant!"
            # )
            # if success:
            #     print("✓ Test email sent successfully")
        else:
            print("✗ Connection failed - check credentials")
    else:
        print("\nEmail service not configured.")
        print("\nConfiguration guide:")
        print("1. Set EMAIL_ADDRESS environment variable")
        print("2. Set EMAIL_PASSWORD environment variable")
        print("\nFor Gmail:")
        print("  - Enable 2-Factor Authentication")
        print("  - Generate App Password at: https://myaccount.google.com/apppasswords")
        print("  - Use App Password (not regular password)")
        print("\nSupported providers:")
        for provider, config in EMAIL_CONFIGS.items():
            print(f"\n{provider.upper()}:")
            print(f"  Server: {config['smtp_server']}")
            print(f"  Port: {config['smtp_port']}")
            print(f"  Notes: {config['notes']}")
