from django.urls import path
from .views import ProductListView, ProductDetailView, ProductEditView, ProductDeactivateView, ReviewSilenceToggler, VariantDeactivateView

urlpatterns = [
    path('', ProductListView.as_view(), name='product'),
    path('create/', ProductListView.as_view(), name='product_create'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('<int:pk>/edit/', ProductEditView.as_view(), name='product_edit'),
    path('<int:pk>/deactivate/', ProductDeactivateView.as_view(), name='product_deactivate'),
    path('variant/<int:pk>/deactivate/', VariantDeactivateView.as_view(), name='variant_deactivate'),
    path('reviews/toggle-silence/<int:review_id>/', ReviewSilenceToggler.as_view(), name="toggle_silence"),
]
