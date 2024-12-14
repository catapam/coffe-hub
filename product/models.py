from django.db import models
from django.urls import reverse
from django.templatetags.static import static
from django.conf import settings
from django.db.models import Avg
import re

class Category(models.Model):
    name = models.CharField(max_length=20, unique=True, blank=False)
    slug = models.SlugField(unique=True, blank=False, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        clean_name = re.sub(r'[^\w\s-]', '', self.name) 
        clean_name = clean_name.replace('-', '_')
        clean_name = clean_name.replace(' ', '_')
        self.slug = clean_name.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Product(models.Model):
    name = models.CharField(max_length=35,unique=True, blank=False)
    slug = models.SlugField(unique=True, blank=False, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', blank=False)
    description = models.TextField(blank=True, null=True, max_length=70)
    rating = models.FloatField(default=0, help_text="Average rating (0-5).")
    image_path = models.ImageField(upload_to='images/products/', blank=True, null=True)
    active = models.BooleanField(default=True, help_text="Set to False to deactivate the product.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Generate a slug from the name
        clean_name = re.sub(r'[^\w\s-]', '', self.name)  # Remove special characters
        clean_name = clean_name.replace('-', '_')
        clean_name = clean_name.replace(' ', '_')
        self.slug = clean_name.lower()
        super().save(*args, **kwargs)

    def image(self):
        if self.image_path:
            return self.image_path.url
        return static('images/product-holder.webp')

    def get_buy_url(self):
        return reverse("product")

    def get_card_context(self):
        variants = self.variants.all()
        stock_by_size = {
            variant.size: {"price": variant.price, "stock": variant.stock}
            for variant in variants
        }

        default_size = variants[0].size if variants else None
        default_price = stock_by_size[default_size]["price"] if default_size else 0
        default_stock_status = (
            "In Stock" if default_size and stock_by_size[default_size]["stock"] > 0 
            else "Out of Stock"
        )

        return {
            "product": self,
            "stock_by_size": stock_by_size,
            "default_size": default_size,
            "default_price": default_price,
            "default_stock_status": default_stock_status,
        }

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

    @property
    def average_rating(self):
        avg = self.reviews.aggregate(average=Avg('rating'))['average']
        if avg is None:
            return 0.0
        return round(avg, 1)  # Round to one decimal place


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', blank=False)
    size = models.CharField(max_length=10, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    stock = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True, help_text="Set to False to deactivate the size.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.size}"

    class Meta:
        unique_together = ('product', 'size')


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', blank=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True
    )
    rating = models.IntegerField(help_text="Integer rating 0-5", blank=False)
    comment = models.CharField(max_length=100, blank=True, help_text="Short review (max 100 chars)")
    silenced = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review of {self.product.name} by {self.user if self.user else 'Anonymous'}: {self.rating}"
