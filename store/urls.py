from django.urls import path
from .views import Catalog

# Define URL patterns for the home app
urlpatterns = [
    # The home page route, served by the Index class-based view
    path('', Catalog.as_view(), name='catalog'),
]