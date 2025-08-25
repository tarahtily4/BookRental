from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from books.models import Book, BookCondition

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    condition = models.CharField(max_length=16, choices=BookCondition.choices)
    qty = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "book", "condition")

    def __str__(self):
        return f"{self.user} — {self.book} x{self.qty} [{self.condition}]"

class OrderStatus(models.TextChoices):
    CREATED = "CREATED", "Створено"
    COLLECTED = "COLLECTED", "Зібрано"
    SHIPPED = "SHIPPED", "Відправлено"
    ARRIVED_OFFICE = "ARRIVED_OFFICE", "Прибули у відділення"
    RECEIVED_BY_USER = "RECEIVED_BY_USER", "Отримано користувачем"
    SENT_BACK = "SENT_BACK", "Відправлено назад"
    RECEIVED_BY_LIBRARY = "RECEIVED_BY_LIBRARY", "Отримано бібліотекою"
    COMPLETED = "COMPLETED", "Завершено"
    CANCELLED = "CANCELLED", "Скасовано"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=32, choices=OrderStatus.choices, default=OrderStatus.CREATED)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    rental_until = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    condition = models.CharField(max_length=16, choices=BookCondition.choices)
    qty = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.book.title} x{self.qty} [{self.condition}]"

class OrderEvent(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="events")
    status = models.CharField(max_length=32, choices=OrderStatus.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.order.id} -> {self.status} @ {self.created_at:%Y-%m-%d %H:%M}"
