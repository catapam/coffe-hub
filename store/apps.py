# Django imports
from django.apps import AppConfig


class StoreConfig(AppConfig):
    '''
    Configuration class for the 'store' application.

    This class defines the application name and the default auto field type.
    '''
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'
