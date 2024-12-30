# Django imports
from django.contrib import admin
from django.urls import path, include, reverse_lazy

# Internal imports
from .views import (
    Custom404View,
    Custom401View,
    set_cookie_consent,
    reset_cookie_consent,
    render_toast_template,
    robots_txt,
    sitemap_xml
)


urlpatterns = [
    # Home app URLs
    path(
        '',
        include('store.urls')
    ),

    # Admin panel
    path(
        "admin/",
        admin.site.urls,
        name='admin'
    ),

    # Authentication and account management
    # Third-party auth package
    path(
        'accounts/',
        include('allauth.urls')
    ),

    # Apps
    # Custom account-related URLs
    path(
        'accounts/',
        include('accounts.urls')
    ),

    # Products
    path(
        'products/',
        include('product.urls')
    ),

    # Cart
    path(
        'cart/',
        include('cart.urls')
    ),

    # Checkout
    path(
        'checkout/',
        include('checkout.urls')
    ),

    # Custom error pages
    # 404 - not found
    path(
        '404/',
        Custom404View.as_view(),
        name='custom_404'
    ),

    # 401 - not permitted
    path(
        '401/',
        Custom401View.as_view(),
        name='custom_401'
    ),

    # Cookies consent
    # Set cookies
    path(
        'set-cookie-consent/',
        set_cookie_consent,
        name='set_cookie_consent'
    ),

    # Reset cookies
    path(
        'reset-cookie-consent/',
        reset_cookie_consent,
        name='reset_cookie_consent'
    ),

    # Toast messages
    path(
        'render-toast/',
        render_toast_template,
        name='render_toast'
    ),

    # Robots.txt
    path(
        'robots.txt',
        robots_txt,
        name='robots_txt'
    ),

    # Sitemap.xml
    path(
        'sitemap.xml',
        sitemap_xml,
        name='sitemap_xml'
    ),
]
