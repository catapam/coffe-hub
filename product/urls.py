# Django imports
from django.urls import path

# Internal imports
from .views import (
    ProductListView,
    ProductDetailView,
    ProductDeactivateView,
    ReviewSilenceToggler,
    VariantDeactivateView,
    SaveSelector,
    ProductSaveView,
    ProductCreateView
)

urlpatterns = [
    path(
        '',
        ProductListView.as_view(),
        name='product'
    ),

    path(
        'create/',
        ProductCreateView.as_view(),
        name='product_create'
    ),

    path(
        'save/',
        ProductSaveView.as_view(),
        name='product_save'
    ),

    path(
        '<int:pk>/deactivate/',
        ProductDeactivateView.as_view(),
        name='product_deactivate'
    ),

    path(
        'variant/<int:pk>/deactivate/',
        VariantDeactivateView.as_view(),
        name='variant_deactivate'
    ),

    path(
        'reviews/toggle-silence/<int:review_id>/',
        ReviewSilenceToggler.as_view(),
        name="toggle_silence"
    ),

    path(
        '<str:selector_type>/save/',
        SaveSelector.as_view(),
        name='save_selector'
    ),

    path(
        '<slug:slug>/',
        ProductDetailView.as_view(),
        name='product_detail'
    ),
]
