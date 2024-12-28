# Django imports
from django.urls import path

# Internal imports
from .views import CheckoutView, CacheCheckoutDataView
from .webhooks import webhook


urlpatterns = [
    path(
        '',
        CheckoutView.as_view(),
        name='checkout'
    ),

    # Stripe webhook callback
    path(
        'wh/',
        webhook,
        name='webhook'
    ),

    path(
        'cache_checkout_data/',
        CacheCheckoutDataView.as_view(),
        name='cache_checkout_data'
    ),
]
