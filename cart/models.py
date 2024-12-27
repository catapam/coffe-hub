# Django imports
from django.conf import settings
from django.db import models

# Internal imports
from product.models import Product


class CartEntry(models.Model):
    """
    Model representing an entry in a user's shopping cart.

    Attributes:
        user: The user to whom the cart entry belongs.
        product: The product added to the cart.
        size: The size of the product.
        quantity: The quantity of the product.
        created_at: The timestamp when the cart entry was created.
        updated_at: The timestamp when the cart entry was last updated.
    """
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
    size = models.CharField(max_length=10, blank=False, null=False)
    quantity = models.PositiveIntegerField(default=1, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta options for the CartEntry model.

        Attributes:
            unique_together: Ensures that each user-product-size combination
                             is unique in the database.
        """
        unique_together = ('user', 'product', 'size')

    def __str__(self):
        """
        String representation of the CartEntry object.

        Returns:
            str: A formatted string showing the user, product name, size,
                 and quantity of the cart entry.
        """
        return (
            f"{self.user or 'Anonymous'}: {self.product.name} ({self.size}) "
            f"x {self.quantity}"
        )
