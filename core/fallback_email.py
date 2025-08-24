import logging
from django.core.mail.backends.smtp import EmailBackend as SMTPBackend
from django.conf import settings

logger = logging.getLogger(__name__)

class FallbackEmailBackend:
    """
    Use Mailgun SMTP as primary.
    If it fails, save email to DB for retry later.
    """

    def __init__(self, *args, **kwargs):
        # Main Mailgun backend (reads from settings.py)
        self.smtp_backend = SMTPBackend(*args, **kwargs)

    def send_messages(self, email_messages):
        try:
            return self.smtp_backend.send_messages(email_messages)
        except Exception as e:
            logger.warning(f"Mailgun failed: {e}. Saving to DB instead.")

            # Import QueuedEmail model here to avoid AppRegistryNotReady
            from .models import QueuedEmail  

            for message in email_messages:
                QueuedEmail.objects.create(
                    subject=message.subject,
                    body=message.body,
                    from_email=message.from_email,
                    to_emails=",".join(message.to),
                )
            return 0
