# Django imports
from django.urls import path

# Internal imports
from .views import (
    HomeView,
    CustomPrivacyPolicyView,
    AboutView,
    HelpView
)


# Define URL patterns for the home app
urlpatterns = [
    # The home page route, served by the Index class-based view
    path(
        '',
        HomeView.as_view(),
        name='home'
    ),

    # About page
    path(
        'about/',
        AboutView.as_view(),
        name='about'
    ),

    # Help page
    path(
        'help/',
        HelpView.as_view(),
        name='help'
    ),

    # Custom privacy policy page
    path(
        'privacy_policy/',
        CustomPrivacyPolicyView.as_view(),
        name='privacy_policy'
    ),
]
