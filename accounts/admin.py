from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from allauth.account.models import EmailAddress
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.auth import get_user_model
from django.templatetags.static import static
from cart.admin import CartEntryInline
from checkout.admin import OrderInline, OrderAdmin


User = get_user_model()


class EmailAddressInline(admin.TabularInline):
    """
    Inline for showing and managing email addresses in the User admin page.
    """
    model = EmailAddress
    extra = 0  # Number of extra blank fields to display for adding new records
    fields = ('email', 'verified', 'primary')  # Fields to display
    readonly_fields = ('forgot_password',)  # Add the custom method here

    def forgot_password(self, obj):
        if obj:
            # Generate URL for sending the forgot password email
            reset_url = reverse('account_reset_password') + f'?email={obj.email}'
            return format_html(
                '<a class="button" href="{}">Send Forgot Password Email</a>',
                reset_url
            )
        return "Save email to enable"
    
    forgot_password.short_description = "Forgot Password"

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser


class CustomUserAdmin(UserAdmin):
    """
    Custom User admin to include EmailAddress and CartEntry inlines.
    """
    readonly_fields = ('last_login', 'date_joined')
    inlines = [EmailAddressInline, CartEntryInline, OrderInline]
    
    def get_list_display(self, request):
        """
        Dynamically determine the list_display fields based on the user's role.
        """
        if request.user.is_superuser:
            return ('username', 'email', 'is_staff', 'is_superuser', 'is_active')  # Superuser view
        return ('username', 'email', 'is_active')  # Non-superuser view

    def get_form(self, request, obj=None, **kwargs):
        """
        Customize the form fields for staff users by hiding sensitive fields.
        """
        return super().get_form(request, obj, **kwargs)

    def get_queryset(self, request):
        """
        Limit the users displayed in the admin list to non-staff users for staff.
        Superusers see all users.
        """
        qs = super().get_queryset(request)
        if request.user.is_staff and not request.user.is_superuser:
            # Restrict staff users to only see non-staff users
            return qs.filter(is_staff=False)
        return qs

    def get_fieldsets(self, request, obj=None):
        """
        Dynamically customize fieldsets to hide the "Permissions" section for non-superusers.
        """
        # Retrieve the default fieldsets
        fieldsets = (
            (None, {'fields': ('username', 'password', 'last_login', 'date_joined')}),
            ('Permissions', {
                'fields': ('is_active', 'is_staff', 'is_superuser'),
            }),
        )

        # Create a new list for the modified fieldsets
        modified_fieldsets = []
        
        for name, options in fieldsets:
            # Exclude the "Permissions" section dynamically for non-superusers
            if not request.user.is_superuser and name == 'Permissions':
                # Remove specific fields or the entire section for non-superusers
                fields = options.get('fields', [])
                fields = tuple(field for field in fields if field == 'is_active')  # Keep only 'is_active'
                if fields:  # Include only if there are remaining fields
                    modified_fieldsets.append((name, {'fields': fields}))
            else:
                # Add other sections unchanged
                modified_fieldsets.append((name, options))

        return modified_fieldsets

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
            return self.model in [User, OrderAdmin]
        return super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        """
        Allow staff users to view Users while restricting access to others.
        """
        if request.user.is_staff and not request.user.is_superuser:
            return True
        return super().has_view_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        """
        Allow staff users to edit Users while restricting access to others.
        """
        if request.user.is_staff and not request.user.is_superuser:
            # Prevent staff from editing other staff users or superusers
            if obj and obj.is_staff:
                return False
            return True
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request):
        """
        Allow staff users to add Users while restricting access to others.
        """
        if request.user.is_staff and not request.user.is_superuser:
            return False
        return super().has_add_permission(request)

    def get_inlines(self, request, obj=None):
        """
        Dynamically include inlines based on user permissions.
        """
        if not request.user.is_superuser:
            # Allow staff users to see both inlines
            return [EmailAddressInline, CartEntryInline, OrderInline]
        return super().get_inlines(request, obj)
    
    def login(self, request, extra_context=None):
        # Redirect non-superusers to the account user page
        if not request.user.is_superuser or not request.user.is_staff:
            return redirect(reverse('account_user')) 
        return super().login(request, extra_context)

# Unregister the default User admin
admin.site.unregister(User)
admin.site.unregister(Group)

# Register the custom User admin
admin.site.register(User, CustomUserAdmin)
