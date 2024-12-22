from django.urls import path
from .views import CartView, AddToCartView, UpdateCartView, DeleteCartView, CartChoiceView

urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('add/<item_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('update/<item_id>/', UpdateCartView.as_view(), name='update_cart'),
    path('delete/<item_id>/', DeleteCartView.as_view(), name='delete_cart'),
    path('select/', CartChoiceView.as_view(), name='cart_choice'),
]
