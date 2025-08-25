from django.views.generic import DetailView
from .models import Book

class BookDetailView(DetailView):
    model = Book
    template_name = "books/detail.html"
    context_object_name = "book"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        stocks = self.object.stocks.all()
        ctx["stock_map"] = {s.condition: s.quantity for s in stocks}
        return ctx
