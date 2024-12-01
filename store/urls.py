from django.urls import path
from .views import HomeView, CustomPrivacyPolicyView, AboutView, HelpView, ContactFormView

# Define URL patterns for the home app
urlpatterns = [
    # The home page route, served by the Index class-based view
    path('', HomeView.as_view(), name='home'),

    # About page
    path('about/', AboutView.as_view(), name='about'),

    # Help page
    path('help/', HelpView.as_view(), name='help'),
    path('contact_form/', ContactFormView.as_view(), name='contact_form'),

    # Custom privacy policy page
    path('privacy_policy/', CustomPrivacyPolicyView.as_view(), name='privacy_policy'),
]