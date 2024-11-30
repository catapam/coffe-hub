from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from .models import Product, ProductVariant, Category
from django.db.models import Min, F, Case, When, Value, IntegerField, Subquery, OuterRef

class ProductListView(ListView):
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        # Check for sorting and filtering parameters
        sort_by = self.request.GET.get('sort_by')
        show_out_of_stock = self.request.GET.get('show_out_of_stock') == 'on'
        selected_categories = self.request.GET.getlist('category[]')
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')
        min_rating = self.request.GET.get('rating')

        if sort_by in ['price_asc', 'price_desc']:
            # Flatten all variants into a single list and order by price
            queryset = ProductVariant.objects.annotate(
                adjusted_price=Case(
                    When(stock__gt=0, then=F('price')),
                    default=Value(0),  # Out-of-stock products are treated as price 0
                    output_field=IntegerField(),
                )
            )

            # Apply filters for category, price, and rating
            if selected_categories and "" not in selected_categories:
                queryset = queryset.filter(product__category__slug__in=selected_categories)
            if price_min:
                queryset = queryset.filter(price__gte=price_min)
            if price_max:
                queryset = queryset.filter(price__lte=price_max)
            if min_rating:
                queryset = queryset.filter(product__rating__gte=min_rating)

            # Exclude out-of-stock variants if "show_out_of_stock" is not active
            if not show_out_of_stock:
                queryset = queryset.filter(stock__gt=0)

            # Order by price
            queryset = queryset.order_by('adjusted_price' if sort_by == 'price_asc' else '-adjusted_price')

        else:
            # Default behavior: Show one card per product with its default variant
            available_variant = ProductVariant.objects.filter(
                product=OuterRef('pk'), stock__gt=0
            ).order_by('price')

            queryset = Product.objects.annotate(
                default_variant_price=Subquery(available_variant.values('price')[:1]),
                default_variant_stock=Subquery(available_variant.values('stock')[:1]),
                default_variant_size=Subquery(available_variant.values('size')[:1]),
            )

            # Exclude products with no stock if "show_out_of_stock" is not active
            if not show_out_of_stock:
                queryset = queryset.filter(default_variant_stock__gt=0)

            # Apply filters
            if selected_categories and "" not in selected_categories:
                queryset = queryset.filter(category__slug__in=selected_categories)
            if price_min:
                queryset = queryset.filter(variants__price__gte=price_min)
            if price_max:
                queryset = queryset.filter(variants__price__lte=price_max)
            if min_rating:
                queryset = queryset.filter(rating__gte=min_rating)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        products_with_context = []

        if isinstance(self.object_list.first(), ProductVariant):
            # Handle flattened variants for price sorting
            for variant in self.object_list:
                # Fetch all stock and prices for this product
                stock_by_size = {
                    v.size: {"price": v.price, "stock": v.stock}
                    for v in ProductVariant.objects.filter(product=variant.product)
                }

                products_with_context.append({
                    "product": variant.product,
                    "variant_size": variant.size,  # Set the current variant as default size
                    "variant_price": variant.adjusted_price,
                    "variant_stock": variant.stock,
                    "stock_by_size": stock_by_size,  # Include all sizes
                })
        else:
            # Handle default single-card rendering per product
            for product in self.object_list:
                # Fetch all stock and prices for this product
                stock_by_size = {
                    v.size: {"price": v.price, "stock": v.stock}
                    for v in ProductVariant.objects.filter(product=product)
                }

                # Use the default variant for size, price, and stock
                products_with_context.append({
                    "product": product,
                    "variant_size": product.default_variant_size,  # Default size
                    "variant_price": product.default_variant_price,
                    "variant_stock": product.default_variant_stock,
                    "stock_by_size": stock_by_size,  # Include all sizes
                })

        context.update({
            'products_with_context': products_with_context,
            'categories': Category.objects.values('slug', 'name'),
            'selected_categories': self.request.GET.getlist('category[]'),
            'total_review': range(6),  # For star ratings
            'sorting_options': {
                'price_asc': 'Price: Low to High',
                'price_desc': 'Price: High to Low',
                'name_asc': 'Name: A to Z',
                'name_desc': 'Name: Z to A',
                'rating_asc': 'Rating: Low to High',
                'rating_desc': 'Rating: High to Low',
            },
            'show_out_of_stock': self.request.GET.get('show_out_of_stock') == 'on',
        })

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




