from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from books.models import Book, BookCondition, BookStock
from .models import CartItem, Order, OrderItem, OrderStatus

from core.utils.mail import send_order_created


@login_required
def cart_view(request):
    items = CartItem.objects.filter(user=request.user).select_related("book")
    return render(request, "orders/cart.html", {"items": items})


@login_required
def add_to_cart(request, slug):
    if request.method != "POST":
        return redirect("books:detail", slug=slug)

    book = get_object_or_404(Book, slug=slug)
    cond = request.POST.get("condition", BookCondition.NEW)
    qty = int(request.POST.get("qty", 1))

    item, created = CartItem.objects.get_or_create(
        user=request.user,
        book=book,
        condition=cond,
        defaults={"qty": qty},
    )
    if not created:
        item.qty += qty
        item.save()

    messages.success(request, "Додано до кошика")
    return redirect("books:detail", slug=slug)


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    messages.info(request, "Видалено з кошика")
    return redirect("orders:cart")


@login_required
@transaction.atomic
def checkout(request):
    items = list(
        CartItem.objects.filter(user=request.user).select_related("book")
    )
    if not items:
        messages.error(request, "Кошик порожній")
        return redirect("orders:cart")

    for it in items:
        stock = BookStock.objects.filter(book=it.book, condition=it.condition).first()
        if not stock or stock.quantity < it.qty:
            messages.error(
                request,
                f"Нема достатньо на складі: {it.book.title} ({it.get_condition_display()})",
            )
            return redirect("orders:cart")

    order = Order.objects.create(user=request.user, status=OrderStatus.CREATED)

    for it in items:
        OrderItem.objects.create(
            order=order,
            book=it.book,
            condition=it.condition,
            qty=it.qty,
        )
        stock = BookStock.objects.get(book=it.book, condition=it.condition)
        stock.quantity -= it.qty
        stock.save()

    try:
        send_order_created(order)
    except Exception as e:  # не валимо чекаут, просто попереджаємо в лог/повідомленні
        messages.warning(request, "Замовлення створено, але лист не надіслано.")

    prof = request.user.profile
    if prof.subscription_active and prof.subscription_until and prof.subscription_until >= date.today():
        order.paid = True
        order.rental_until = date.today() + timedelta(days=30)
        order.save()

        CartItem.objects.filter(user=request.user).delete()

        messages.success(request, "Замовлення оформлено. Оплачено по активній підписці.")
        return redirect("orders:detail", order_id=order.id)

    messages.info(request, "Потрібна активна підписка. Оформіть її, будь ласка.")
    return redirect("payments:subscribe")


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "orders/order_detail.html", {"order": order})
