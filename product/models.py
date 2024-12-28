import re

# Django imports
from django.db import models
from django.urls import reverse
from django.templatetags.static import static
from django.conf import settings
from django.db.models import Avg

# Third-party imports
from cloudinary.models import CloudinaryField
from cloudinary.api import resource
from cloudinary.exceptions import NotFound
from cloudinary.utils import cloudinary_url

# Internal imports
from django.core.validators import MinValueValidator


class Category(models.Model):
    '''
    Model representing a product category.

    Attributes:
        name (str): The name of the category.
        slug (str): The unique slug identifier for the category.
        created_at (datetime): Timestamp for when the category was created.
    '''
    name = models.CharField(
        max_length=20,
        unique=True,
        blank=False,
        null=False
    )

    slug = models.SlugField(
        unique=True,
        blank=False,
        null=False,
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        '''
        Override the save method to generate a clean slug from the name.
        '''
        clean_name = re.sub(r'[^\w\s-]', '', self.name)
        clean_name = clean_name.replace('-', '_').replace(' ', '_')
        self.slug = clean_name.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Product(models.Model):
    '''
    Model representing a product.

    Attributes:
        name (str): The name of the product.
        slug (str): The unique slug identifier for the product.
        category (Category): The associated category for the product.
        description (str): A short description of the product.
        rating (float): The average rating of the product.
        image_path (CloudinaryField): The image of the product.
        active (bool): Whether the product is active.
        created_at (datetime): Timestamp for when the product was created.
        updated_at (datetime): Timestamp for when the product was last updated.
    '''
    name = models.CharField(
        max_length=35,
        unique=True,
        blank=False,
        null=False
    )

    slug = models.SlugField(
        unique=True,
        blank=False,
        null=False,
        editable=False
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        blank=False, null=False
    )

    description = models.TextField(
        blank=True,
        null=True,
        max_length=70
    )

    rating = models.FloatField(
        default=0,
        help_text='Average rating (0-5).'
    )

    image_path = CloudinaryField(
        'image',
        blank=True,
        null=True
    )

    active = models.BooleanField(
        default=True,
        help_text='Set to False to deactivate the product.',
        blank=False,
        null=False
    )

    cloudinary_version = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        '''
        Override the save method to generate a slug and update ratings.

        Preserves existing 'active' status and ensures category consistency.
        '''
        if self.pk:
            original = Product.objects.get(pk=self.pk)
            if not hasattr(self, 'active'):
                self.active = original.active

        if self.name:
            clean_name = re.sub(r'[^\w\s-]', '', self.name)
            clean_name = clean_name.replace('-', '_').replace(' ', '_')
            self.slug = clean_name.lower()

        super().save(*args, **kwargs)

        if self.pk:
            self.rating = self.average_rating
            super().save(update_fields=['rating'])

    def image(self):
        '''
        Retrieve the product image URL or return a placeholder if unavailable.

        Returns:
            str: The URL of the product image or a static placeholder.
        '''
        try:
            if self.image_path:
                public_id = (
                    self.image_path.public_id
                    if hasattr(self.image_path, 'public_id')
                    else str(self.image_path)
                )

                version = self.cloudinary_version or None
                url, _ = cloudinary_url(
                    public_id, secure=True, version=version,
                    resource_type='image', fetch_format='auto'
                )
                return url
        except Exception:
            return static('images/product-holder.webp')

        return static('images/product-holder.webp')

    def get_buy_url(self):
        '''
        Return the URL for purchasing the product.
        '''
        return reverse('product')

    def get_card_context(self):
        '''
        Generate context for rendering the product card.

        Returns:
            dict: Context with stock, size, price, and status details.
        '''
        variants = self.variants.all()
        stock_by_size = {
            variant.size: {'price': variant.price, 'stock': variant.stock}
            for variant in variants
        }

        default_size = variants[0].size if variants else None
        default_price = (
            stock_by_size[default_size]['price'] if default_size else 0
        )
        default_stock_status = (
            'In Stock'
            if default_size and stock_by_size[default_size]['stock'] > 0
            else 'Out of Stock'
        )

        return {
            'product': self,
            'stock_by_size': stock_by_size,
            'default_size': default_size,
            'default_price': default_price,
            'default_stock_status': default_stock_status,
        }

    def get_absolute_url(self):
        '''
        Return the absolute URL for the product detail view.
        '''
        return reverse('product_detail', kwargs={'slug': self.slug})

    @property
    def average_rating(self):
        '''
        Calculate and return the average product rating.

        Returns:
            float: Rounded average rating or 0.0 if no ratings exist.
        '''
        avg = self.reviews.aggregate(average=Avg('rating'))['average']
        return round(avg, 1) if avg else 0.0


class ProductVariant(models.Model):
    '''
    Model representing a product variant.

    Attributes:
        product (Product): The associated product.
        size (str): The size of the product variant.
        price (Decimal): The price of the variant.
        stock (int): The stock quantity of the variant.
        active (bool): Whether the variant is active.
    '''
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
        blank=False,
        null=False
    )

    size = models.CharField(
        max_length=10,
        blank=False,
        null=False
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=False,
        null=False,
        validators=[MinValueValidator(0)]
    )

    stock = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False
    )

    active = models.BooleanField(
        default=True,
        help_text='Set to False to deactivate the size.',
        blank=False,
        null=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.size}"

    class Meta:
        unique_together = ('product', 'size')


class ProductReview(models.Model):
    '''
    Model representing a product review.

    Attributes:
        product (Product): The reviewed product.
        user (User): The user who submitted the review.
        rating (int): The review rating (0-5).
        comment (str): A short review comment.
        silenced (bool): Whether the review is silenced.
        created_at (datetime): Timestamp for when the review was created.
    '''
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reviews',
        blank=False, null=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        blank=True, null=True
    )

    rating = models.IntegerField(
        help_text='Integer rating 0-5', blank=False, null=False
    )

    comment = models.CharField(
        max_length=100, blank=True,
        help_text='Short review (max 100 chars)'
    )

    silenced = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"Review of {self.product.name} by "
            f"{self.user if self.user else 'Anonymous'}: {self.rating}"
        )
