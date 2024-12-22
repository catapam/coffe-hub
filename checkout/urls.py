from django.urls import path
from .views import CheckoutView, CacheCheckoutDataView
from .webhooks import webhook

urlpatterns = [
    path('', CheckoutView.as_view(), name='checkout'),
    path('wh/', webhook, name='webhook'),
    path('cache_checkout_data/', CacheCheckoutDataView.as_view(), name='cache_checkout_data'),
]