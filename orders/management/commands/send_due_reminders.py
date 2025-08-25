from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from orders.models import Order

class Command(BaseCommand):
    help = "Надіслати нагадування про завершення оренди за 3 дні"

    def handle(self, *args, **options):
        target_day = date.today() + timedelta(days=3)
        qs = Order.objects.filter(paid=True, rental_until=target_day)
        for o in qs.select_related("user"):
            subject = f"Нагадування: замовлення #{o.id} завершується {o.rental_until}"
            body = f"Ваша оренда по замовленню #{o.id} завершується {o.rental_until}. Будь ласка, підготуйте повернення."
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [o.user.email], fail_silently=True)
        self.stdout.write(self.style.SUCCESS(f"Відправлено: {qs.count()}"))
