from django.db import models
from django.core.validators import MinValueValidator
from .utils import make_slug

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = make_slug(self.name)  # ← тут
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    author = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="books")
    pages = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    in_stock = models.BooleanField(default=True)
    cover = models.ImageField(upload_to="covers/", blank=True, null=True)
    cover_url = models.URLField(blank=True)

    class Meta:
        ordering = ["title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = make_slug(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} — {self.author}"


class BookCondition(models.TextChoices):
    NEW = "NEW", "Нова"
    USED = "USED", "Використовувалась"
    FRAGILE = "FRAGILE", "Хрупка"


class BookStock(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="stocks")
    condition = models.CharField(max_length=16, choices=BookCondition.choices, default=BookCondition.NEW)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("book", "condition")

    def __str__(self):
        return f"{self.book.title} [{self.get_condition_display()}] — {self.quantity}"
