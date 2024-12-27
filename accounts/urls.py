# Django imports
from django.urls import path

# Internal imports
from .views import (
    UpdateUsernameView,
    RedirectUserView,
    CustomLoginView,
    ProfileView
)
from checkout.views import OrderDetailView, OrderListView

# Define the URL patterns for the 'accounts' app
urlpatterns = [
    # Root URL redirects to the user update page
    path(
        '',
        RedirectUserView.as_view(),
        name='accounts'
    ),

    # URL for updating the user's username
    path(
        'user/',
        UpdateUsernameView.as_view(),
        name='account_user'
    ),

    # Custom login
    path(
        'login/',
        CustomLoginView.as_view(),
        name='account_login'
    ),

    # Account management
    path(
        'profile/',
        ProfileView.as_view(),
        name='account_profile'
    ),
    path(
        'orders/',
        OrderListView.as_view(),
        name='account_orders'
    ),
    path(
        'orders/<str:order_id>',
        OrderDetailView.as_view(),
        name='order_view'
    ),
]
