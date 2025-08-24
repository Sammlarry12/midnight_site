from django.utils.deprecation import MiddlewareMixin
from django.contrib.gis.geoip2 import GeoIP2
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from .models import VisitLog


def get_client_ip(request):
    """Extract real client IP, even behind proxy."""
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class VisitLogMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        super().__init__(get_response)
        try:
            self.geo = GeoIP2()
        except Exception:
            self.geo = None

    def process_request(self, request):
        path = request.path.lower()

        # ❌ Skip admin, static, media, api, and assets
        if (
            path.startswith("/admin")
            or path.startswith("/static")
            or path.startswith("/media")
            or path.startswith("/api")
            or path.endswith((".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico"))
        ):
            return None

        ip = get_client_ip(request)

        # 🔹 Only override localhost IP in DEBUG mode
        if settings.DEBUG and ip in ["127.0.0.1", "::1"]:
            ip = "8.8.8.8"  # Fake IP for dev testing

        # Defaults
        country = city = region = None
        latitude = longitude = None

        try:
            if ip and self.geo:
                geo_data = self.geo.city(ip)
                country = geo_data.get("country_name")
                city = geo_data.get("city")
                region = geo_data.get("region")
                if not region and "subdivisions" in geo_data:
                    try:
                        region = geo_data["subdivisions"][0]["names"]["en"]
                    except Exception:
                        region = None
                latitude = geo_data.get("latitude")
                longitude = geo_data.get("longitude")
        except Exception:
            pass

        # Save visit log
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

        # ✅ One email per IP per hour
        visitor_key = f"visitor_email_last_sent_{ip}"
        last_sent = request.session.get(visitor_key)
        now = timezone.now()

        if not last_sent or now - timezone.datetime.fromisoformat(last_sent) > timedelta(hours=1):
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

