from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # Home app URLs
    path('', include('store.urls')),
]
