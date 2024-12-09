from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        from django.contrib import admin
        from allauth.account.models import EmailAddress

        # Unregister EmailAddress if already registered
        if admin.site.is_registered(EmailAddress):
            admin.site.unregister(EmailAddress)
