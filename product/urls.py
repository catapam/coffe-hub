from django.urls import path
from .views import ProductListView, ProductDetailView, ProductEditView, ProductDeactivateView

urlpatterns = [
    path('', ProductListView.as_view(), name='product'),
    path('create/', ProductListView.as_view(), name='product_create'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('<int:pk>/edit/', ProductEditView.as_view(), name='product_edit'),
    path('<int:pk>/deactivate/', ProductDeactivateView.as_view(), name='product_deactivate'),
]
