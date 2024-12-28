# Django imports
from django.contrib.admin import TabularInline

# Internal imports
from .models import CartEntry


class CartEntryInline(TabularInline):
    '''
    Inline for displaying CartEntry objects in the User admin page.

    This class allows admin users to view, add, and delete CartEntry objects
    directly from the User admin interface.
    '''
    model = CartEntry
    extra = 0
    can_delete = True
    fields = (
        'product',
        'size',
        'quantity'
    )

    readonly_fields = (
        'product',
        'size'
    )

    def has_view_permission(self, request, obj=None):
        '''
        Determine if the user has permission to view CartEntry objects.

        Args:
            request: The current request object.
            obj: The parent object being viewed (optional).

        Returns:
            bool: True if the user is staff or superuser, otherwise False.
        '''
        return request.user.is_staff or request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        '''
        Determine if the user has permission to change CartEntry objects.

        Args:
            request: The current request object.
            obj: The parent object being viewed (optional).

        Returns:
            bool: True if the user is staff or superuser, otherwise False.
        '''
        return request.user.is_staff or request.user.is_superuser
