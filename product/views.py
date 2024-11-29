from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from .models import Product, ProductVariant, Category

class ProductListView(ListView):
    """
    Displays a list of all products with filters, sorting, and variant sizes.
    """
    model = Product
    template_name = 'product/product_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch all products and their variants
        all_products = Product.objects.prefetch_related('variants').all()

        # Filters from request
        selected_categories = self.request.GET.getlist('category[]')  # Allow multiple category selections
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')
        min_rating = self.request.GET.get('rating')

        # Apply filters
        if selected_categories:
            all_products = all_products.filter(category__slug__in=selected_categories)
        if price_min:
            all_products = all_products.filter(price__gte=price_min)
        if price_max:
            all_products = all_products.filter(price__lte=price_max)
        if min_rating:
            all_products = all_products.filter(rating__gte=min_rating)

        # Apply sorting
        sort_by = self.request.GET.get('sort_by')
        if sort_by == 'price_asc':
            all_products = all_products.order_by('price')
        elif sort_by == 'price_desc':
            all_products = all_products.order_by('-price')
        elif sort_by == 'name_asc':
            all_products = all_products.order_by('name')
        elif sort_by == 'name_desc':
            all_products = all_products.order_by('-name')
        elif sort_by == 'rating_asc':
            all_products = all_products.order_by('rating')
        elif sort_by == 'rating_desc':
            all_products = all_products.order_by('-rating')

        # Prepare product list with sizes from variants
        products_with_sizes = []
        for product in all_products:
            variants = product.variants.all()
            sizes = [variant.size for variant in variants]
            products_with_sizes.append({
                'product': product,
                'sizes': sizes if sizes else ['Unic']  # Default to "Unic" if no sizes are available
            })

        # Add context data
        context['products'] = products_with_sizes
        context['categories'] = [
            {'slug': category.slug, 'name': category.name}
            for category in Category.objects.all()
        ]
        context['selected_categories'] = selected_categories  # Pass selected categories to context
        context['total_review'] = range(0, 6)  # Star ratings 0 to 5

        return context

class ProductDetailView(DetailView):
    """
    Displays the details of a single product, including its variants.
    """
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add product variants to the context
        context['variants'] = self.object.variants.all()
        return context
