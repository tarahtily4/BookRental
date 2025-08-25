import stripe
from datetime import date, timedelta
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def subscribe(request):
    return render(request, "payments/subscribe.html", {
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY
    })

@login_required
def create_checkout_session(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    price_id = settings.STRIPE_PRICE_ID
    session = stripe.checkout.Session.create(
        mode="subscription",
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=request.build_absolute_uri("/payments/success/"),
        cancel_url=request.build_absolute_uri("/payments/cancel/"),
        customer_email=request.user.email or None,
    )
    return JsonResponse({"id": session.id})

@login_required
def success(request):
    prof = request.user.profile
    prof.subscription_active = True
    prof.subscription_until = date.today() + timedelta(days=30)
    prof.save()
    return render(request, "payments/success.html")

def cancel(request):
    return render(request, "payments/cancel.html")

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

@login_required
def dev_activate(request):
    if not settings.DEBUG:
        return HttpResponseForbidden("Only in DEBUG")
    from datetime import date, timedelta
    prof = request.user.profile
    prof.subscription_active = True
    prof.subscription_until = date.today() + timedelta(days=30)
    prof.save()
    return redirect("accounts:profile")