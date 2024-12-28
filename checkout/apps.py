# Django imports
from django.apps import AppConfig


class CheckoutConfig(AppConfig):
    '''
    Configuration class for the 'checkout' application.

    This class is used to configure the app's settings and ensure that
    necessary signals are imported when the app is ready.
    '''
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'checkout'

    def ready(self):
        '''
        Executes initialization logic when the app is ready.

        Imports the signals module to connect signal handlers defined
        in the 'checkout' application.
        '''
        import checkout.signals
