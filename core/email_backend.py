import logging
from django.core.mail.backends.smtp import EmailBackend

logger = logging.getLogger(__name__)

class FallbackEmailBackend(EmailBackend):
    """
    Try sending via SMTP (Gmail, Mailgun, etc.).
    If it fails, save the email into QueuedEmail for retry later.
    """

    def __init__(self, *args, **kwargs):
        # ✅ Django passes in fail_silently, host, port, etc.
        super().__init__(*args, **kwargs)

    def send_messages(self, email_messages):
        try:
            return super().send_messages(email_messages)
        except Exception as e:
            logger.warning(f"SMTP failed: {e}. Saving to DB instead.")

            # ✅ Import inside to avoid AppRegistryNotReady error
            from .models import QueuedEmail  

            for message in email_messages:
                QueuedEmail.objects.create(
                    subject=message.subject,
                    body=message.body,
                    from_email=message.from_email,
                    to_emails=",".join(message.to),
                )
            return 0
