import logging
from threading import Thread
from typing import Optional

from flask import current_app, render_template
from flask_mail import Message


class EmailService:
    def __init__(self, mail, sender: str, logger: Optional[logging.Logger] = None):
        """
        Initialize EmailService.

        Args:
            mail: Flask-Mail instance
            sender: Email address to send from
            logger: Optional logger instance (will create one if not provided)
        """
        self.mail = mail
        self.sender = sender
        self.logger = logger or logging.getLogger(__name__)

    def send_async_email(self, app, msg: Message) -> None:
        """
        Send email asynchronously.

        Args:
            app: Flask application context
            msg: Email message to send
        """
        try:
            with app.app_context():
                self.mail.send(msg)
            self.logger.info(f"Email sent successfully to {msg.recipients}")
        except Exception as e:
            self.logger.error(f"Failed to send email to {msg.recipients}: {str(e)}")
            raise

    def send_verification_email(
        self,
        verification_link: str,
        username: str,
        email: str,
        subject: Optional[str] = None,
    ) -> None:
        """
        Send email verification email.

        Args:
            verification_link: Link for email verification
            username: Recipient's username
            email: Recipient's email address
            subject: Optional custom subject
        """
        html_content = render_template(
            "emails/verify_email.html",
            username=username,
            verification_link=verification_link,
        )

        subject = subject or "Verify Your Email"
        msg = Message(
            subject=subject,
            sender=self.sender,
            recipients=[email],
        )
        msg.html = html_content

        self.logger.info(f"Sending verification email to {email}")
        Thread(
            target=self.send_async_email, args=(current_app._get_current_object(), msg)
        ).start()

    def send_password_reset_email(
        self,
        reset_link: str,
        email: str,
        username: str,
        subject: Optional[str] = None,
    ) -> None:
        """
        Send password reset email (alias for send_reset_password_email).
        """
        return self.send_reset_password_email(reset_link, email, username, subject)

    def send_reset_password_email(
        self,
        reset_link: str,
        email: str,
        username: str,
        subject: Optional[str] = None,
    ) -> None:
        """
        Send password reset email.

        Args:
            reset_link: Link for password reset
            email: Recipient's email address
            username: Recipient's username
            subject: Optional custom subject
        """
        html_content = render_template(
            "emails/reset_password.html",
            username=username,
            reset_link=reset_link,
        )

        subject = subject or "Reset Your Password"
        msg = Message(
            subject=subject,
            sender=self.sender,
            recipients=[email],
        )
        msg.html = html_content

        self.logger.info(f"Sending password reset email to {email}")
        Thread(
            target=self.send_async_email, args=(current_app._get_current_object(), msg)
        ).start()

    def send_welcome_email(
        self,
        username: str,
        email: str,
        subject: Optional[str] = None,
    ) -> None:
        """
        Send welcome email after registration.

        Args:
            username: Recipient's username
            email: Recipient's email address
            subject: Optional custom subject
        """
        html_content = render_template(
            "emails/welcome_email.html",
            username=username,
        )

        subject = subject or "Welcome to Our Platform!"
        msg = Message(
            subject=subject,
            sender=self.sender,
            recipients=[email],
        )
        msg.html = html_content

        self.logger.info(f"Sending welcome email to {email}")
        Thread(
            target=self.send_async_email, args=(current_app._get_current_object(), msg)
        ).start()
