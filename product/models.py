from django.db import models
from django.urls import reverse
from django.templatetags.static import static
from django.conf import settings
from django.db.models import Avg
import re
from cloudinary.models import CloudinaryField
from cloudinary.api import resource
from cloudinary.exceptions import NotFound
from cloudinary.utils import cloudinary_url
from django.core.validators import MinValueValidator


class Category(models.Model):
    name = models.CharField(max_length=20, unique=True, blank=False, null=False)
    slug = models.SlugField(unique=True, blank=False, null=False, editable=False)
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
    name = models.CharField(max_length=35,unique=True, blank=False, null=False)
    slug = models.SlugField(unique=True, blank=False, null=False, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', blank=False, null=False)
    description = models.TextField(blank=True, null=True, max_length=70)
    rating = models.FloatField(default=0, help_text="Average rating (0-5).")
    image_path = CloudinaryField('image', blank=True, null=True)
    active = models.BooleanField(default=True, help_text="Set to False to deactivate the product.", blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cloudinary_version = models.CharField(max_length=20, blank=True, null=True)  # Stores the version

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Generate a slug from the name
        clean_name = re.sub(r'[^\w\s-]', '', self.name)  # Remove special characters
        clean_name = clean_name.replace('-', '_')
        clean_name = clean_name.replace(' ', '_')
        self.slug = clean_name.lower()

        # Ensure the category is not reset
        if not self.pk:
            # If the object is being created for the first time
            self.category = self.category

        # Update the rating field with the average rating
        avg_rating = self.reviews.aggregate(average=Avg('rating'))['average']
        self.rating = round(avg_rating, 1) if avg_rating is not None else 0.0
            
        super().save(*args, **kwargs)

    def image(self):
        """
        Returns the URL of the product's image.
        - If no image_path is set, returns the static placeholder.
        - Handles both CloudinaryResource objects and string public IDs.
        """
        try:
            if self.image_path:
                # Handle CloudinaryResource objects
                if hasattr(self.image_path, 'public_id'):
                    public_id = self.image_path.public_id
                else:
                    public_id = str(self.image_path)

                # Generate the Cloudinary URL
                version = self.cloudinary_version or None
                url, options = cloudinary_url(
                    public_id,
                    secure=True,
                    version=version,
                    resource_type="image",  # Ensure correct resource type
                    fetch_format="auto"    # Optional: Enable format optimization
                )
                return url
        except Exception as e:
            # return default image if there is any issues with cloudinary rendering
            return static('images/product-holder.webp')
        
        # Return the static placeholder if no image
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
        return round(avg, 1)


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', blank=False, null=False)
    size = models.CharField(max_length=10, blank=False, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0, blank=False, null=False)
    active = models.BooleanField(default=True, help_text="Set to False to deactivate the size.", blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.size}"

    class Meta:
        unique_together = ('product', 'size')


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', blank=False, null=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True
    )
    rating = models.IntegerField(help_text="Integer rating 0-5", blank=False, null=False)
    comment = models.CharField(max_length=100, blank=True, help_text="Short review (max 100 chars)")
    silenced = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review of {self.product.name} by {self.user if self.user else 'Anonymous'}: {self.rating}"
