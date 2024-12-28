# Django imports
from django.contrib import admin

# Third party imports
from allauth.account.models import EmailAddress

# Internal imports
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    '''
    Admin configuration for ContactMessage.
    '''
    list_display = (
        'status',
        'name',
        'email',
        'subject',
        'created_at'
    )

    search_fields = (
        'name',
        'email',
        'subject'
    )

    list_filter = (
        'status',
        'name',
        'email',
        'subject',
        'created_at'
    )

    def get_readonly_fields(self, request, obj=None):
        '''
        Dynamically set readonly fields based on user role.

        Args:
            request: The current HTTP request.
            obj: The object being viewed or edited (if any).

        Returns:
            tuple: A tuple of field names to be marked as readonly.
        '''
        if request.user.is_staff and not request.user.is_superuser:
            return (
                'name',
                'email',
                'subject',
                'created_at',
                'message'
            )

        elif request.user.is_superuser:
            return ('created_at',)

        return super().get_readonly_fields(request, obj)

    def has_permission(self, request):
        '''
        Allow access to superusers and staff users only.

        Args:
            request: The current HTTP request.

        Returns:
            bool: True if the user has access, otherwise False.
        '''
        return request.user.is_superuser or request.user.is_staff

    def has_module_permission(self, request):
        '''
        Restrict admin access for staff users to only the User model
        and ContactMessage.

        Args:
            request: The current HTTP request.

        Returns:
            bool: True if the user has module permission, otherwise False.
        '''
        if request.user.is_staff and not request.user.is_superuser:
            return self.model in [ContactMessage]
        return super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        '''
        Allow view permissions for staff and superusers.

        Args:
            request: The current HTTP request.
            obj: The object being viewed (if any).

        Returns:
            bool: True if the user has view permission, otherwise False.
        '''
        return request.user.is_staff or request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        '''
        Allow change permissions for staff and superusers.

        Args:
            request: The current HTTP request.
            obj: The object being changed (if any).

        Returns:
            bool: True if the user has change permission, otherwise False.
        '''
        return request.user.is_staff or request.user.is_superuser

    def has_add_permission(self, request):
        '''
        Allow add permissions for superusers only.

        Args:
            request: The current HTTP request.

        Returns:
            bool: True if the user has add permission, otherwise False.
        '''
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        '''
        Allow delete permissions for superusers only.

        Args:
            request: The current HTTP request.
            obj: The object being deleted (if any).

        Returns:
            bool: True if the user has delete permission, otherwise False.
        '''
        return request.user.is_superuser
