from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from allauth.account.models import EmailAddress


class EmailAddressInline(admin.TabularInline):
    """
    Inline for showing email addresses in the User admin page.
    """
    model = EmailAddress
    extra = 1  # Number of extra blank fields to display for adding new records
    fields = ('email', 'verified', 'primary')  # Fields to display
    readonly_fields = ('verified', 'primary')  # Make fields read-only if necessary


class CustomUserAdmin(UserAdmin):
    """
    Custom User admin to include EmailAddress inline.
    """
    inlines = [EmailAddressInline]
    

# Unregister the default User admin
admin.site.unregister(User)

# Register the custom User admin
admin.site.register(User, CustomUserAdmin)

