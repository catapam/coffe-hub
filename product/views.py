from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from .models import Product, ProductVariant, Category

class ProductListView(ListView):
    """
    Displays a list of all products with filters, sorting, and variant sizes.
    """
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        """
        Retrieves the products along with their variants.
        """
        return Product.objects.prefetch_related('variants').all()

    def get_context_data(self, **kwargs):
        """
        Adds additional filtering, sorting, and variant information to the context.
        """
        context = super().get_context_data(**kwargs)

        # Fetch the base queryset
        queryset = self.get_queryset()

        # Filters and sorting logic...

        # Prepare products with their sizes and stock
        products_with_context = []
        for product in queryset:
            variants = product.variants.all()
            stock_by_size = {
                variant.size: {"price": variant.price, "stock": variant.stock}
                for variant in variants
            }
            default_size = variants[0].size if variants else None
            default_price = stock_by_size.get(default_size, {}).get('price', 0)
            default_stock_status = (
                "In Stock" if stock_by_size.get(default_size, {}).get('stock', 0) > 0 else "Out of Stock"
            )

            products_with_context.append({
                "product": product,
                "stock_by_size": stock_by_size,
                "default_size": default_size,
                "default_price": default_price,
                "default_stock_status": default_stock_status,
            })

        # Add to context
        context['products_with_context'] = products_with_context
        context['categories'] = Category.objects.values('slug', 'name')
        context['total_review'] = range(6)  # For star ratings

        return context


class ProductDetailView(DetailView):
    """
    Displays the details of a single product, including its variants.
    Passes size and stock information dynamically from ProductVariant.
    """
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        # Fetch variants and organize sizes and stock
        variants = product.variants.all()
        sizes = [variant.size for variant in variants]
        stock_by_size = {variant.size: variant.stock for variant in variants}

        # Set default size and stock status
        default_size = sizes[0] if sizes else None
        default_stock_status = "In Stock" if stock_by_size.get(default_size, 0) > 0 else "Out of Stock"

        # Add data to the context
        context['variants'] = variants
        context['sizes'] = sizes
        context['stock_by_size'] = stock_by_size
        context['default_size'] = default_size  # First size as default
        context['default_stock_status'] = default_stock_status  # Stock status for the default size
        context['total_review'] = range(5)  # For star ratings

        return context




