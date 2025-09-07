import os
import django
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'midnight_site.settings')
django.setup()

# ✅ Automatically run migrations on startup
try:
    call_command("migrate", interactive=False)
except Exception as e:
    import sys
    print(f"Migration failed: {e}", file=sys.stderr)

    # ✅ Collect static files automatically on startup
try:
    call_command("collectstatic", interactive=False, verbosity=0)
except Exception as e:
    import sys
    print(f"Collectstatic failed: {e}", file=sys.stderr)


application = get_wsgi_application()

