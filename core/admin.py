from django.contrib import admin
from .models import VisitLog

from django.contrib import admin
from .models import VisitLog
from .models import WalletSubmission

@admin.register(VisitLog)
class VisitLogAdmin(admin.ModelAdmin):
    list_display = ("ip", "country", "city", "region", "latitude", "longitude", "path", "timestamp")
    list_filter = ("country", "city", "region", "timestamp")
    search_fields = ("ip", "country", "city", "region", "path", "user_agent")
    ordering = ("-timestamp",)  # newest first

# core/admin.py

from django.contrib import admin
from .models import WalletSubmission

@admin.register(WalletSubmission)
class WalletSubmissionAdmin(admin.ModelAdmin):
    list_display = ("wallet_name", "wallet_email", "method", "created_at")
    search_fields = ("wallet_name", "wallet_email", "method")
    list_filter = ("method", "created_at")

from django.contrib import admin
from .models import QueuedEmail

@admin.register(QueuedEmail)
class QueuedEmailAdmin(admin.ModelAdmin):
    list_display = ("subject","body", "from_email", "to_emails", "created_at", "sent")
    list_filter = ("sent", "created_at")
    search_fields = ("recipient_list", "subject", "body")




