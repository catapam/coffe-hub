from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Admin configuration for ContactMessage.
    """
    list_display = ('name', 'email', 'subject', 'created_at')  # Customize the list view
    search_fields = ('name', 'email', 'subject')  # Add search functionality
    readonly_fields = ('created_at',)  # Make certain fields read-only

    def has_permission(self, request):
        """
        Allow access to superusers and staff users only.
        """
        return request.user.is_superuser or request.user.is_staff

    def has_module_permission(self, request):
        """
        Restrict admin access for staff users to only the User model and ContactMessage.
        """
        if request.user.is_staff and not request.user.is_superuser:
            # Allow access to User and ContactMessage models for staff
            return self.model in [ContactMessage]
        return super().has_module_permission(request)
        
    def has_view_permission(self, request, obj=None):
        """
        Allow view permissions for staff and superusers.
        """
        return request.user.is_staff or request.user.is_superuser # Staff can view contacts too

    def has_change_permission(self, request, obj=None):
        """
        Allow change permissions for staff and superusers.
        """
        return request.user.is_superuser  # Only allow superusers to change ContactMessages

    def has_add_permission(self, request):
        """
        Allow add permissions for staff and superusers.
        """
        return request.user.is_superuser  # Only allow superusers to add ContactMessages

    def has_delete_permission(self, request, obj=None):
        """
        Allow delete permissions for staff and superusers.
        """
        return request.user.is_superuser  # Only allow superusers to delete ContactMessages
