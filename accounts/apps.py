# Django imports
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    '''
    Configuration class for the 'accounts' application.

    This class sets the default auto field and application name. It also
    ensures that the EmailAddress model from allauth is unregistered from
    the Django admin site during the app's ready state.
    '''
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        '''
        Executes custom initialization logic when the app is ready.

        Unregisters the EmailAddress model from the Django admin site if it
        is already registered.
        '''
        from django.contrib import admin
        from allauth.account.models import EmailAddress

        # Unregister EmailAddress if already registered
        if admin.site.is_registered(EmailAddress):
            admin.site.unregister(EmailAddress)
