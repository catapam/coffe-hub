from django.contrib import admin
from django.urls import path, include
from .views import Custom401View, Custom404View, CustomPrivacyPolicyView

urlpatterns = [
    path("admin/", admin.site.urls),

    # Home app URLs
    path('', include('store.urls')),

    # Authentication and account management URLs from 'allauth' and custom app
    path('accounts/', include('allauth.urls')),  # Third-party auth package
    
    # Custom error pages for 401 Unauthorized and 404 Not Found
    path('401/', Custom401View.as_view(), name='custom_401'),
    path('404/', Custom404View.as_view(), name='custom_404'),

    # Custom privacy policy page
    path('privacy-policy/', CustomPrivacyPolicyView.as_view(), name='privacy-policy'),
]
