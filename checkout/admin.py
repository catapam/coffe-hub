from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from product.models import Product
from .models import OrderLineItem, Order


class OrderLineItemAdminInline(admin.TabularInline):
    model = OrderLineItem
    extra = 0  # Number of extra blank fields for adding new entries
    fields = ('product_name', 'size', 'quantity', 'lineitem_total')
    readonly_fields = ('price', 'lineitem_total')

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class OrderInline(admin.TabularInline):
    model = Order
    extra = 0
    fields = ('order_link', 'status', 'date', 'order_total')
    readonly_fields = ('order_link', 'date', 'order_total')
    
    def order_link(self, obj):
        """
        Creates a clickable link for the order number that redirects to the order's admin detail page.
        """
        if obj.id:
            url = reverse('admin:checkout_order_change', args=[obj.id])  # Replace `checkout` with your app's name
            return format_html('<a href="{}">{}</a>', url, obj.order_number)
        return obj.order_number
    
    order_link.short_description = "Order Number"

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    model = Order
    inlines = (OrderLineItemAdminInline,)

    readonly_fields = ('order_number', 'user', 'date', 'order_total')

    fields = ('order_number', 'user', 'status', 'date', 'full_name',
              'email', 'phone_number', 'country',
              'postcode', 'town_or_city', 'street_address1',
              'street_address2', 'county',
              'order_total')

    list_display = ('order_number', 'user', 'status', 'date', 'order_total')
    list_filter = ('order_number', 'user', 'status', 'date', 'order_total')
    search_fields = ('order_number', 'user', 'date', 'order_total')  # Add search functionality

    ordering = ('-date',)

    def has_module_permission(self, request):
        return request.user.is_staff or request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
