from django.utils.deprecation import MiddlewareMixin
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import requests
from .models import VisitLog
import logging

logger = logging.getLogger(__name__)


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
        if response.status_code == 200:
            data = response.json()
            return (
                data.get("country_name"),
                data.get("region"),
                data.get("city"),
                data.get("latitude"),
                data.get("longitude"),
            )
    except Exception as e:
        logger.warning(f"Geo lookup failed: {e}")
    return None, None, None, None, None


class VisitLogMiddleware(MiddlewareMixin):
    def process_request(self, request):
        path = request.path.lower()

        # Skip admin, static, media, and asset requests
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
            ip = "8.8.8.8"  # fake IP for local testing

        country, region, city, latitude, longitude = get_geo_data(ip)

        # Only log once per hour per IP
        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent_log_exists = VisitLog.objects.filter(ip=ip, timestamp__gte=one_hour_ago).exists()

        if not recent_log_exists:
            VisitLog.objects.create(
                ip=ip,
                country=country,
                city=city,
                region=region,
                latitude=latitude,
                longitude=longitude,
                path=request.path,
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )

            # ✅ Send email notification in all environments
            try:
                send_mail(
                    f"🌍 New Visitor from {country or 'Unknown'} ({ip})",
                    f"IP: {ip}\nCountry: {country}\nCity: {city}\nRegion: {region}\n"
                    f"Latitude: {latitude}\nLongitude: {longitude}\nPath: {request.path}\nTime: {timezone.now()}",
                    settings.DEFAULT_FROM_EMAIL,
                    settings.ADMIN_EMAILS,
                    fail_silently=False,
                )
                logger.info(f"Visitor email sent successfully for {ip}")
            except Exception as e:
                logger.warning(f"Email send failed: {e}")

        return None
