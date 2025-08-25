import stripe
from datetime import date, timedelta
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception:
        return HttpResponseBadRequest("Invalid payload")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = session.get("customer_details", {}).get("email") or session.get("customer_email")
        if email:
            try:
                user = User.objects.get(email=email)
                prof = user.profile
                prof.subscription_active = True
                prof.subscription_until = date.today() + timedelta(days=30)
                prof.save()
            except User.DoesNotExist:
                pass

    return HttpResponse(status=200)
