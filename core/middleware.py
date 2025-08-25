from django.utils.deprecation import MiddlewareMixin
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import requests
from .models import VisitLog


def get_client_ip(request):
    """Extract real client IP, even behind proxy."""
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def get_geo_data(ip):
    """Fetch geo info for an IP using ipapi.co API."""
    try:
        response = requests.get(f"https://ipapi.co/{ip}/json/", timeout=3)
        data = response.json()
        return (
            data.get("country_name"),
            data.get("region"),
            data.get("city"),
            data.get("latitude"),
            data.get("longitude"),
        )
    except Exception:
        return None, None, None, None, None


class VisitLogMiddleware(MiddlewareMixin):
    def process_request(self, request):
        path = request.path.lower()

        # Skip admin, static, media, api, and assets
        if (
            path.startswith("/admin")
            or path.startswith("/static")
            or path.startswith("/media")
            or path.startswith("/api")
            or path.endswith((".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico"))
        ):
            return None

        ua = request.META.get("HTTP_USER_AGENT", "").lower()
        if any(keyword in ua for keyword in ["bot", "crawl", "spider"]):
            return None

        ip = get_client_ip(request)
        if settings.DEBUG and ip in ["127.0.0.1", "::1"]:
            ip = "8.8.8.8"  # fake IP for dev testing

        country, region, city, latitude, longitude = get_geo_data(ip)

        # Only log once per hour per IP
        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent_log_exists = VisitLog.objects.filter(ip=ip, timestamp__gte=one_hour_ago).exists()

        if not recent_log_exists:
            log = VisitLog.objects.create(
                ip=ip,
                country=country,
                city=city,
                region=region,
                latitude=latitude,
                longitude=longitude,
                path=request.path,
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
        else:
            log = None

        # Email throttling using session
        visitor_key = f"visitor_email_last_sent_{ip}"
        last_sent = request.session.get(visitor_key)
        now = timezone.now()
        last_sent_dt = last_sent and timezone.datetime.fromisoformat(last_sent)

        if log and (not last_sent_dt or now - last_sent_dt > timedelta(hours=1)):
            # Send email
            subject = f"New Visitor from {country or 'Unknown'} ({ip})"
            message = (
                f"IP: {log.ip}\n"
                f"Country: {log.country}\n"
                f"City: {log.city}\n"
                f"Region: {log.region}\n"
                f"Latitude: {log.latitude}\n"
                f"Longitude: {log.longitude}\n"
                f"Path: {log.path}\n"
                f"User Agent: {log.user_agent}\n"
                f"Timestamp: {log.timestamp}\n"
            )
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    settings.ADMIN_EMAILS,
                    fail_silently=True,
                )
                request.session[visitor_key] = now.isoformat()
            except Exception:
                pass

        return None
