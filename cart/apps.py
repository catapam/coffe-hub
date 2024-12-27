# Django imports
from django.apps import AppConfig


class CartConfig(AppConfig):
    """
    Configuration class for the 'cart' application.

    This class is used to configure the app's settings and ensure that
    necessary signals are imported when the app is ready.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cart'

    def ready(self):
        """
        Executes initialization logic when the app is ready.

        Imports the signals module to connect signal handlers defined
        in the 'cart' application.
        """
        import cart.signals
