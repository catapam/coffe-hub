from django.urls import path
from .views import UpdateUsernameView, RedirectUserView, CustomLoginView

# Define the URL patterns for the 'accounts' app
urlpatterns = [
    # Root URL redirects to the user update page
    path('', RedirectUserView.as_view(), name='accounts'),

    # URL for updating the user's username
    path('user/', UpdateUsernameView.as_view(), name='account_user'),

    # custom login
    path('login/', CustomLoginView.as_view(), name='account_login'),

    # Temporary placeholders for account management
    path('address/', RedirectUserView.as_view(), name='account_address'),
    path('orders/', RedirectUserView.as_view(), name='account_orders'),
]
