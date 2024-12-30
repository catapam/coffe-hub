import uuid

# Django imports
from django.db import models
from django.db.models import Sum
from django.conf import settings
from django.core.validators import MinValueValidator
from django_countries.fields import CountryField

# Internal imports
from product.models import Product


class Order(models.Model):
    '''
    Model representing a customer order.

    Attributes:
        user (ForeignKey): The user placing the order.
        order_number (CharField): Unique order identifier.
        status (CharField): Current status of the order.
        full_name (CharField): Customer's full name.
        email (EmailField): Customer's email address.
        phone_number (CharField): Customer's phone number.
        country (CountryField): Country of delivery.
        postcode (CharField): Postal code for delivery.
        town_or_city (CharField): Town or city of delivery.
        street_address1 (CharField): Primary street address.
        street_address2 (CharField): Secondary street address.
        county (CharField): County, state, or locality.
        date (DateTimeField): Timestamp of the order creation.
        order_total (DecimalField): Total cost of the order.
        stripe_pid (CharField): Stripe Payment Intent ID.
    '''
    STATUS_CHOICES = [
        ('cancelled', 'Cancelled'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        related_name='orders', blank=True, null=True
    )

    order_number = models.CharField(
        max_length=32, null=False, editable=False
    )

    status = models.CharField(
        max_length=12, choices=STATUS_CHOICES, default='processing',
        blank=False, null=False
    )

    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    country = CountryField(blank_label='Country *', null=False, blank=False)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    order_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0
    )
    stripe_pid = models.CharField(max_length=255, null=True, blank=True)

    def _generate_order_number(self):
        '''
        Generate a random, unique order number using UUID.

        Returns:
            str: A unique order number.
        '''
        return uuid.uuid4().hex.upper()

    def update_total(self):
        '''
        Update the order's total by aggregating line item totals.

        If no line items remain, sets the order total to 0.
        '''
        total = self.lineitems.aggregate(Sum('lineitem_total'))[
            'lineitem_total__sum'
        ]
        self.order_total = total if total is not None else 0
        self.save()

    def save(self, *args, **kwargs):
        '''
        Override the save method to generate an order number
        if not already set.
        '''
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderLineItem(models.Model):
    '''
    Model representing an individual line item in an order.

    Attributes:
        order (ForeignKey): The associated order.
        product (ForeignKey): The product in the line item.
        product_name (CharField): Name of the product.
        price (DecimalField): Price per unit of the product.
        size (CharField): Size of the product variant.
        quantity (IntegerField): Quantity of the product.
        lineitem_total (DecimalField): Total cost for this line item.
    '''
    order = models.ForeignKey(
        Order, null=False, blank=False, on_delete=models.CASCADE,
        related_name='lineitems'
    )
    product = models.ForeignKey(
        Product, null=False, blank=False, on_delete=models.CASCADE
    )
    product_name = models.CharField(max_length=35, blank=False, null=False)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=False, null=False,
        validators=[MinValueValidator(0)]
    )
    size = models.CharField(max_length=10, blank=False, null=False)
    quantity = models.IntegerField(null=False, blank=False, default=0)
    lineitem_total = models.DecimalField(
        max_digits=6, decimal_places=2, null=False, blank=False
    )

    def save(self, *args, **kwargs):
        '''
        Override the save method to calculate the line item total and
        update the product name and price if not already set.
        '''
        if not self.pk:
            self.product_name = self.product.name
            variant = self.product.variants.get(size=self.size)
            self.price = variant.price

        self.lineitem_total = self.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f'Product ID {self.product.id} on order '
            f'{self.order.order_number}'
        )
