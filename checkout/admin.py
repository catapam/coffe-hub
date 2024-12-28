# Django imports
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.admin import TabularInline, ModelAdmin

# Internal imports
from product.models import Product
from .models import OrderLineItem, Order


class OrderLineItemAdminInline(TabularInline):
    '''
    Inline class for managing OrderLineItem entries in the admin panel.

    Allows staff or superusers to view order line items and superusers
    to edit or delete them.
    '''
    model = OrderLineItem
    extra = 0  # Number of extra blank fields for adding new entries
    fields = (
        'product_name',
        'size',
        'quantity',
        'lineitem_total'
    )

    readonly_fields = (
        'price',
        'lineitem_total'
    )

    def has_view_permission(self, request, obj=None):
        '''
        Checks if the user has permission to view the OrderLineItem.

        Args:
            request: The HTTP request object.
            obj: The current object being viewed (optional).

        Returns:
            bool: True if the user is staff or superuser, False otherwise.
        '''
        return request.user.is_staff or request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        '''
        Checks if the user has permission to change the OrderLineItem.

        Args:
            request: The HTTP request object.
            obj: The current object being viewed (optional).

        Returns:
            bool: True if the user is a superuser, False otherwise.
        '''
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        '''
        Checks if the user has permission to delete the OrderLineItem.

        Args:
            request: The HTTP request object.
            obj: The current object being viewed (optional).

        Returns:
            bool: True if the user is a superuser, False otherwise.
        '''
        return request.user.is_superuser


class OrderInline(TabularInline):
    '''
    Inline class for displaying Order objects in the admin panel.

    Provides staff and superusers with access to view and manage orders.
    '''
    model = Order
    extra = 0
    fields = (
        'order_link',
        'status',
        'date',
        'order_total'
    )

    readonly_fields = (
        'order_link',
        'date',
        'order_total'
    )

    def order_link(self, obj):
        '''
        Creates a clickable link for the order number.

        Args:
            obj: The current Order object.

        Returns:
            str: HTML link to the order's admin detail page.
        '''
        if obj.id:
            url = reverse('admin:checkout_order_change', args=[obj.id])
            return format_html('<a href="{}">{}</a>', url, obj.order_number)
        return obj.order_number

    order_link.short_description = 'Order Number'

    def has_view_permission(self, request, obj=None):
        '''
        Checks if the user has permission to view the Order.

        Args:
            request: The HTTP request object.
            obj: The current object being viewed (optional).

        Returns:
            bool: True if the user is staff or superuser, False otherwise.
        '''
        return request.user.is_staff or request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        '''
        Checks if the user has permission to change the Order.

        Args:
            request: The HTTP request object.
            obj: The current object being viewed (optional).

        Returns:
            bool: True if the user is staff or superuser, False otherwise.
        '''
        return request.user.is_staff or request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        '''
        Checks if the user has permission to delete the Order.

        Args:
            request: The HTTP request object.
            obj: The current object being viewed (optional).

        Returns:
            bool: True if the user is a superuser, False otherwise.
        '''
        return request.user.is_superuser


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    '''
    Admin class for managing Order objects in the admin panel.

    Provides detailed views, search functionality, and filters
    for Order objects.
    '''
    model = Order
    inlines = (OrderLineItemAdminInline,)

    readonly_fields = (
        'order_number',
        'user',
        'date',
        'order_total',
        'payment_intent_link'
    )

    fields = (
        'order_number',
        'payment_intent_link',
        'user',
        'status',
        'date',
        'full_name',
        'email',
        'phone_number',
        'country',
        'postcode',
        'town_or_city',
        'street_address1',
        'street_address2',
        'county',
        'order_total'
    )

    list_display = (
        'order_number',
        'user',
        'status',
        'date',
        'order_total'
    )

    list_filter = (
        'order_number',
        'user',
        'status',
        'date',
        'order_total'
    )

    search_fields = (
        'order_number',
        'user',
        'date',
        'order_total',
        'payment_intent_id'
    )

    ordering = ('-date',)

    def payment_intent_link(self, obj):
        '''
        Returns a clickable link to the Stripe dashboard.

        Args:
            obj: The current Order object.

        Returns:
            str: HTML link to the PaymentIntent in Stripe or a message.
        '''
        if obj.payment_intent_id:
            url = (
                f'https://dashboard.stripe.com/test/payments/'
                f'{obj.payment_intent_id}'
            )
            return format_html(
                '<a href="{}" target="_blank">{}</a>',
                url, obj.payment_intent_id
            )
        return 'No Payment Intent'

    payment_intent_link.short_description = 'Stripe Payment'

    def has_module_permission(self, request):
        '''
        Checks if the user has permission to view the Order module.

        Args:
            request: The HTTP request object.

        Returns:
            bool: True if the user is staff or superuser, False otherwise.
        '''
        return request.user.is_staff or request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        '''
        Checks if the user has permission to view an Order.

        Args:
            request: The HTTP request object.
            obj: The current object being viewed (optional).

        Returns:
            bool: True if the user is staff or superuser, False otherwise.
        '''
        return request.user.is_staff or request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        '''
        Checks if the user has permission to change an Order.

        Args:
            request: The HTTP request object.
            obj: The current object being viewed (optional).

        Returns:
            bool: True if the user is staff or superuser, False otherwise.
        '''
        return request.user.is_staff or request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        '''
        Checks if the user has permission to delete an Order.

        Args:
            request: The HTTP request object.
            obj: The current object being viewed (optional).

        Returns:
            bool: True if the user is a superuser, False otherwise.
        '''
        return request.user.is_superuser
