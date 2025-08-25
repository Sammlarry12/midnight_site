from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from core.models import QueuedEmail

class Command(BaseCommand):
    help = "Retry sending all queued emails that failed earlier"

    def handle(self, *args, **kwargs):
        queued = QueuedEmail.objects.all()
        if not queued.exists():
            self.stdout.write(self.style.SUCCESS("✅ No queued emails found."))
            return

        success_count = 0
        fail_count = 0

        for email in queued:
            try:
                sent = send_mail(
                    subject=email.subject,
                    message=email.body,
                    from_email=email.from_email,
                    recipient_list=email.to_emails.split(","),
                    fail_silently=False,
                )
                if sent:
                    success_count += 1
                    email.delete()  # remove after successful send
                else:
                    fail_count += 1
            except Exception as e:
                fail_count += 1
                self.stderr.write(f"⚠️ Failed to send to {email.to_emails}: {e}")

        self.stdout.write(
            self.style.SUCCESS(f"✅ {success_count} emails sent, ❌ {fail_count} failed.")
        )
