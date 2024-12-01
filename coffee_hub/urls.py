from django.contrib import admin
from django.urls import path, include
from .views import Custom404View, Custom401View

urlpatterns = [
    path("admin/", admin.site.urls),

    # Home app URLs
    path('', include('store.urls')),

    # Authentication and account management URLs from 'allauth' and custom app
    path('accounts/', include('allauth.urls')),  # Third-party auth package
    path('accounts/', include('accounts.urls')),  # Custom account-related URLs

    # Products
    path('products/', include('product.urls')),

    # Custom error pages for 404 Not Found
    path('404/', Custom404View.as_view(), name='custom_404'),
    path('401/', Custom401View.as_view(), name='custom_401'),
]
