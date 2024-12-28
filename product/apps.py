# Django imports
from django.apps import AppConfig


class ProductConfig(AppConfig):
    '''
    Configuration class for the 'product' application.

    This class is used to configure settings specific to the product app.
    '''
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'product'
