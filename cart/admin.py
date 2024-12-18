from django.contrib import admin
from .models import CartEntry

class CartEntryInline(admin.TabularInline):
    """
    Inline for displaying CartEntry objects in the User admin page.
    """
    model = CartEntry
    extra = 0  # Number of extra blank fields for adding new entries
    fields = ('product', 'size', 'quantity')  # Fields to display in the inline
    readonly_fields = ('product', 'size',)
    can_delete = True  # Allow deletion of entries

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser
