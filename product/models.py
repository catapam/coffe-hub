from django.db import models
from django.urls import reverse
from django.templatetags.static import static


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=35)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField(blank=True, null=True,max_length=70)
    rating = models.FloatField(default=0, help_text="Average rating (0-5).")
    # image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def image(self):
        # Return the placeholder image URL
        return static('images/product-holder.webp')

    def get_buy_url(self):
        return reverse("product")  # Adjust as needed for your app's URLs

    def get_card_context(self):
        """
        Generate context for rendering this product's card.
        """
        variants = self.variants.all()
        stock_by_size = {
            variant.size: {"price": variant.price, "stock": variant.stock}
            for variant in variants
        }

        default_size = variants[0].size if variants else None
        default_price = stock_by_size[default_size]["price"] if default_size else 0
        default_stock_status = (
            "In Stock" if stock_by_size[default_size]["stock"] > 0 else "Out of Stock"
            if default_size else "Out of Stock"
        )

        return {
            "product": self,
            "stock_by_size": stock_by_size,
            "default_size": default_size,
            "default_price": default_price,
            "default_stock_status": default_stock_status,
        }



class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price specific to the size
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.size}"

    class Meta:
        unique_together = ('product', 'size')
