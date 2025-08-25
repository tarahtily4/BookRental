from django.contrib import admin
from .models import Book, Category, BookStock

class BookStockInline(admin.TabularInline):
    model = BookStock
    extra = 1

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "in_stock")
    list_filter = ("category", "in_stock")
    search_fields = ("title", "author")
    inlines = [BookStockInline]
    prepopulated_fields = {"slug": ("title",)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(BookStock)
