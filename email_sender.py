import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional

def send_email(
    sender_email: str,
    sender_password: str,
    recipient_emails: List[str],
    subject: str,
    body: str,
    smtp_server: str = "smtp.gmail.com",
    smtp_port: int = 587,
    is_html: bool = False
) -> bool:
    """
    Send an email using SMTP.
    
    Args:
        sender_email (str): Email address of the sender
        sender_password (str): Password or app-specific password for the sender's email
        recipient_emails (List[str]): List of recipient email addresses
        subject (str): Email subject
        body (str): Email body content
        smtp_server (str): SMTP server address (default: Gmail's SMTP server)
        smtp_port (int): SMTP server port (default: 587 for TLS)
        is_html (bool): Whether the body content is HTML (default: False)
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = ", ".join(recipient_emails)
        message["Subject"] = subject

        # Attach body
        content_type = "html" if is_html else "plain"
        message.attach(MIMEText(body, content_type))

        # Create SMTP session
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Enable TLS
            server.login(sender_email, sender_password)
            server.send_message(message)
        
        return True
    
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

# Example usage:
if __name__ == "__main__":
    # Example configuration
    sender = "email@gmail.com"
    password = "hi"  # For Gmail, use App Password
    recipients = ["email@gmail.com"]
    email_subject = "Test Email"
    email_body = "This is a test email sent using Python's SMTP library."
    
    # Send email
    success = send_email(
        sender_email=sender,
        sender_password=password,
        recipient_emails=recipients,
        subject=email_subject,
        body=email_body
    )
    
    if success:
        print("Email sent successfully!")
    else:
        print("Failed to send email.") 