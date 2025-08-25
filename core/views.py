from django.views.generic import ListView
from books.models import Book, Category
from django.db.models import Q

class HomeView(ListView):
    template_name = "core/home.html"
    model = Book
    context_object_name = "books"
    paginate_by = 12

    def get_queryset(self):
        qs = Book.objects.select_related("category").all().order_by("title")
        q = self.request.GET.get("q", "").strip()
        cat = self.request.GET.get("category", "").strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(author__icontains=q))
        if cat:
            qs = qs.filter(category__slug=cat)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.all().order_by("name")
        ctx["q"] = self.request.GET.get("q", "")
        ctx["cat_active"] = self.request.GET.get("category", "")
        return ctx
