from django.urls import path
from .views import BookDetailView

urlpatterns = [
    path("<slug:slug>/", BookDetailView.as_view(), name="detail"),
]
