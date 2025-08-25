from __future__ import annotations

import logging
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Order, OrderEvent
from core.utils.mail import send_order_created

log = logging.getLogger(__name__)


@receiver(pre_save, sender=Order)
def _remember_previous_status(sender, instance: Order, **kwargs) -> None:
    instance._old_status = None
    if instance.pk:
        try:
            instance._old_status = (
                Order.objects.only("status")
                .get(pk=instance.pk)
                .status
            )
        except Order.DoesNotExist:
            instance._old_status = None


@receiver(post_save, sender=Order)
def _order_post_save(sender, instance: Order, created: bool, **kwargs) -> None:
    if created:
        OrderEvent.objects.create(
            order=instance,
            status=instance.status,
            note="Order created",
        )

        try:
            if instance.user_id and getattr(instance.user, "email", None):
                send_order_created(instance)
        except Exception:
            log.exception("Failed to send 'order created' email")
        return

    prev = getattr(instance, "_old_status", None)
    if prev != instance.status:
        OrderEvent.objects.create(
            order=instance,
            status=instance.status,
            note=f"Status changed: {prev} -> {instance.status}",
        )
