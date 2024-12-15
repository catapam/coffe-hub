from django.conf import settings
from django.db import models
from product.models import Product

class CartEntry(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart_entries",
        blank=True,
        null=True  # Allow null for anonymous carts, if needed
    )
    product = models.ForeignKey(
        Product(),  
        on_delete=models.CASCADE,
        related_name="cart_entries"
    )
    size = models.CharField(max_length=50)  # Size field to store product variant size
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product', 'size')  # Prevent duplicate entries for the same user/product/size combo

    def __str__(self):
        return ""
