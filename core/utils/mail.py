from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def _subject_prefix() -> str:
    return "BookRental • "


def send_order_created(order) -> None:
    user = order.user
    ctx = {
        "order": order,
        "user": user,
        "profile_url": f"{settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else '127.0.0.1'}",
    }

    subject = f"{_subject_prefix()}Статус замовлення #{order.id}: Створено"
    text_body = render_to_string("emails/order_created.txt", ctx)
    html_body = render_to_string("emails/order_created.html", ctx)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email] if user.email else [],
    )
    if html_body:
        email.attach_alternative(html_body, "text/html")
    email.send(fail_silently=False)
