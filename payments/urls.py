from django.urls import path
from .views import subscribe, create_checkout_session, success, cancel
from .webhook import stripe_webhook

urlpatterns = [
    path("subscribe/", subscribe, name="subscribe"),
    path("create-checkout-session/", create_checkout_session, name="create_checkout_session"),
    path("success/", success, name="success"),
    path("cancel/", cancel, name="cancel"),
    path("webhook/", stripe_webhook, name="webhook"),
]
