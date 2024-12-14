from django.contrib import admin
from django.urls import path, include
from .views import Custom404View, Custom401View, set_cookie_consent, reset_cookie_consent

urlpatterns = [
    path("admin/", admin.site.urls, name='admin'),

    # Home app URLs
    path('', include('store.urls')),

    # Authentication and account management URLs from 'allauth' and custom app
    path('accounts/', include('allauth.urls')),  # Third-party auth package
    path('accounts/', include('accounts.urls')),  # Custom account-related URLs

    # Products
    path('products/', include('product.urls')),

    # Cart
    path('cart/', include('cart.urls')),

    # Custom error pages for 404 Not Found
    path('404/', Custom404View.as_view(), name='custom_404'),
    path('401/', Custom401View.as_view(), name='custom_401'),

    # cookies consent
    path('set-cookie-consent/', set_cookie_consent, name='set_cookie_consent'),
    path('reset-cookie-consent/', reset_cookie_consent, name='reset_cookie_consent'),
]
