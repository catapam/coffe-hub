import json

# Django imports
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.sessions.models import Session
from django.shortcuts import redirect
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import format_html
from django.utils.timezone import localtime
from django.contrib.admin import TabularInline, ModelAdmin

# Third-party imports
from allauth.account.models import EmailAddress

# Internal imports
from cart.admin import CartEntryInline
from checkout.admin import OrderInline, OrderAdmin
from store.models import ContactMessage
from .models import UserProfile


User = get_user_model()


class UserProfileInline(admin.StackedInline):
    '''
    Inline class to display and edit UserProfile data
    within the User admin interface.
    '''
    model = UserProfile
    can_delete = False  # Prevent deletion of profiles through the inline
    verbose_name_plural = 'User Profiles'
    fk_name = 'user'


class EmailAddressInline(TabularInline):
    '''
    Inline for showing and managing email addresses in the User admin page.
    '''
    model = EmailAddress
    extra = 0  # Number of extra blank fields to display for adding new records
    fields = ('email', 'verified', 'primary')  # Fields to display
    readonly_fields = ('forgot_password',)  # Add the custom method here

    def forgot_password(self, obj):
        if obj:
            # Generate URL for sending the forgot password email
            reset_url = reverse('account_reset_password') + \
                f'?email={obj.email}'
            return format_html(
                '<a class="button" href="{}">Send Forgot Password Email</a>',
                reset_url
            )
        return 'Save email to enable'

    forgot_password.short_description = 'Forgot Password'

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser


class CustomSessionAdmin(ModelAdmin):
    list_display = ('session_key', 'username', 'expire_date')
    readonly_fields = ('decoded_data',)
    ordering = ('-expire_date',)

    def username(self, obj):
        '''
        Extract the username from the session data if available.
        '''
        try:
            # Decode the session data
            session_data = obj.get_decoded()
            user_id = session_data.get('_auth_user_id')
            if user_id:
                user = User.objects.get(pk=user_id)
                return user.username
        except Exception as e:
            return None
    username.short_description = 'User'

    def decoded_data(self, obj):
        '''
        Display the decoded session data for debugging.
        '''
        try:
            session_data = obj.get_decoded()
            formatted_data = json.dumps(session_data, indent=4)
            return format_html('<pre>{}</pre>', formatted_data)
        except Exception:
            return 'Error decoding session data'
    decoded_data.short_description = 'Session Data'

    def has_view_permission(self, request, obj=None):
        '''
        Allow staff users to view Users while restricting access to others.
        '''
        if obj:  # Detailed view
            return request.user.is_superuser
        return True  # List view

    def has_module_permission(self, request):
        '''
        Restrict admin access for staff users to only the User model
        and ContactMessage.
        '''
        if request.user.is_superuser:
            return True
        return super().has_module_permission(request)

    def has_add_permission(self, request):
        '''
        Allow staff users to add Users while restricting access to others.
        '''
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


class CustomUserAdmin(UserAdmin):
    '''
    Custom User admin to include EmailAddress and CartEntry inlines.
    '''
    readonly_fields = ('last_login', 'date_joined')
    inlines = [UserProfileInline, EmailAddressInline, CartEntryInline,
               OrderInline]

    def get_list_display(self, request):
        '''
        Dynamically determine the list_display fields based on the user's role.
        '''
        if request.user.is_superuser:
            return ('username', 'get_primary_email', 'is_staff',
                    'is_superuser', 'is_active')
        return ('username', 'get_primary_email', 'is_active')

    def get_primary_email(self, obj):
        '''
        Retrieves the primary email address for the user.
        '''
        primary_email = EmailAddress.objects.filter(user=obj, primary=True).first()
        if primary_email:
            return primary_email.email
        return 'No primary email'

    get_primary_email.short_description = 'Primary Email'

    def get_form(self, request, obj=None, **kwargs):
        '''
        Customize the form fields for staff users by hiding sensitive fields.
        '''
        return super().get_form(request, obj, **kwargs)

    def get_queryset(self, request):
        '''
        Limit the users displayed in the admin list to non-staff users for staff.
        Superusers see all users.
        '''
        qs = super().get_queryset(request)
        if request.user.is_staff and not request.user.is_superuser:
            # Restrict staff users to only see non-staff users
            return qs.filter(is_staff=False)
        return qs

    def get_fieldsets(self, request, obj=None):
        '''
        Dynamically customize fieldsets to hide the 'Permissions' section
        for non-superusers.
        '''
        # Retrieve the default fieldsets
        fieldsets = (
            (None, {'fields': ('username', 'password', 'last_login',
                               'date_joined')}),
            ('Permissions', {
                'fields': ('is_active', 'is_staff', 'is_superuser'),
            }),
        )

        # Create a new list for the modified fieldsets
        modified_fieldsets = []

        for name, options in fieldsets:
            # Exclude the 'Permissions' section dynamically for non-superusers
            if not request.user.is_superuser and name == 'Permissions':
                # Remove specific fields or the entire section for non-superusers
                fields = options.get('fields', [])
                fields = tuple(field for field in fields if field == 'is_active')
                if fields:  # Include only if there are remaining fields
                    modified_fieldsets.append((name, {'fields': fields}))
            else:
                # Add other sections unchanged
                modified_fieldsets.append((name, options))

        return modified_fieldsets

    def has_permission(self, request):
        '''
        Allow access to superusers and staff users only.
        '''
        return request.user.is_superuser or request.user.is_staff

    def has_module_permission(self, request):
        '''
        Restrict admin access for staff users to only the User model
        and ContactMessage.
        '''
        if request.user.is_staff and not request.user.is_superuser:
            return self.model in [User, OrderAdmin]
        return super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        '''
        Allow staff users to view Users while restricting access to others.
        '''
        if request.user.is_staff and not request.user.is_superuser:
            return True
        return super().has_view_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        '''
        Allow staff users to edit Users while restricting access to others.
        '''
        if request.user.is_staff and not request.user.is_superuser:
            # Prevent staff from editing other staff users or superusers
            if obj and obj.is_staff:
                return False
            return True
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request):
        '''
        Allow staff users to add Users while restricting access to others.
        '''
        if request.user.is_staff and not request.user.is_superuser:
            return False
        return super().has_add_permission(request)

    def login(self, request, extra_context=None):
        # Redirect non-superusers to the account user page
        if not request.user.is_superuser or not request.user.is_staff:
            return redirect(reverse('account_user'))
        return super().login(request, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        '''
        Add session data for the user being viewed to the admin context
        and handle session deletion. Add contact messages for the user's
        email addresses to the context.
        '''
        extra_context = extra_context or {}
        user_sessions = []
        user_contact_messages = []

        # Handle session deletions
        if request.method == 'POST':
            for key, value in request.POST.items():
                if key.startswith('sessions-') and key.endswith('-DELETE') \
                        and value == 'on':
                    session_key = request.POST.get(f'{key[:-7]}-session_key')
                    if session_key:
                        try:
                            session = Session.objects.get(session_key=session_key)
                            session.delete()
                        except Session.DoesNotExist:
                            pass

        try:
            # Get all sessions and filter by user ID
            user_id = int(object_id)
            sessions = Session.objects.all()

            for session in sessions:
                session_data = session.get_decoded()
                if str(user_id) == session_data.get('_auth_user_id'):
                    user_sessions.append({
                        'session_key': session.session_key,
                        'expire_date': session.expire_date,
                        'data': session_data,
                    })

            # Get user's associated email addresses
            user = User.objects.get(pk=user_id)
            email_addresses = EmailAddress.objects.filter(user=user)
            email_addresses = email_addresses.values_list('email', flat=True)

            user_contact_messages = ContactMessage.objects.filter(
                email__in=email_addresses)

        except User.DoesNotExist:
            pass

        # Add session and contact message data to the context
        extra_context['user_sessions'] = user_sessions
        extra_context['user_contact_messages'] = user_contact_messages
        return super().change_view(request, object_id, form_url, extra_context)


# Unregister the default User admin
admin.site.unregister(User)
admin.site.unregister(Group)

# Register the custom User admin
admin.site.register(User, CustomUserAdmin)
admin.site.register(Session, CustomSessionAdmin)
