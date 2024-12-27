# Django imports
from django.urls import path

# Internal imports
from .views import (
    CartView,
    AddToCartView,
    UpdateCartView,
    DeleteCartView,
    CartChoiceView
)

urlpatterns = [
    path(
        '',
        CartView.as_view(),
        name='cart'
    ),

    path(
        'add/<item_id>/',
        AddToCartView.as_view(),
        name='add_to_cart'
    ),

    path(
        'update/<item_id>/',
        UpdateCartView.as_view(),
        name='update_cart'
    ),

    path(
        'delete/<item_id>/',
        DeleteCartView.as_view(),
        name='delete_cart'
    ),

    # User chooses if they want to keep database or session cart, or merge both
    path(
        'select/',
        CartChoiceView.as_view(),
        name='cart_choice'
    ),
]
