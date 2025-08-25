from django.contrib import admin
from .models import Order, OrderItem, OrderEvent, CartItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderEventInline(admin.TabularInline):
    model = OrderEvent
    extra = 0
    readonly_fields = ("created_at",)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "paid", "created_at", "rental_until")
    list_filter = ("status", "paid", "created_at")
    inlines = [OrderItemInline, OrderEventInline]

admin.site.register(CartItem)
