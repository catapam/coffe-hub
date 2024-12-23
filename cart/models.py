from django.conf import settings
from django.db import models
from product.models import Product

class CartEntry(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart_entries",
        blank=True,
        null=True
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name="cart_entries"
    )
    size = models.CharField(max_length=10, blank=False, null=False)  # Size field to store product variant size
    quantity = models.PositiveIntegerField(default=1, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product', 'size')  # Prevent duplicate entries for the same user/product/size combo

    def __str__(self):
        return f"{self.user or 'Anonymous'}: {self.product.name} ({self.size}) x {self.quantity}"
