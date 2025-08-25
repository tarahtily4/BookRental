from django.urls import path
from .views import cart_view, add_to_cart, remove_from_cart, checkout, order_detail

urlpatterns = [
    path("cart/", cart_view, name="cart"),
    path("add/<slug:slug>/", add_to_cart, name="add_to_cart"),
    path("remove/<int:item_id>/", remove_from_cart, name="remove_from_cart"),
    path("checkout/", checkout, name="checkout"),
    path("order/<int:order_id>/", order_detail, name="detail"),
]
