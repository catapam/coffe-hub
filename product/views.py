from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, redirect
from .models import Product, ProductVariant, Category
from django.db.models import Min, F, Case, When, Value, IntegerField, Subquery, OuterRef, Q
from django.views.generic.edit import UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


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
        search_query = self.request.GET.get('q')  # Capture the search query

        if sort_by in ['price_asc', 'price_desc']:
            queryset = ProductVariant.objects.annotate(
                adjusted_price=Case(
                    When(stock__gt=0, then=F('price')),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            )

            # Apply filters
            if selected_categories and "" not in selected_categories:
                queryset = queryset.filter(product__category__slug__in=selected_categories)
            if price_min:
                queryset = queryset.filter(price__gte=price_min)
            if price_max:
                queryset = queryset.filter(price__lte=price_max)
            if min_rating:
                queryset = queryset.filter(product__rating__gte=min_rating)
            if search_query:
                queryset = queryset.filter(
                    Q(product__name__icontains=search_query) |
                    Q(product__description__icontains=search_query)
                )

            if not show_out_of_stock:
                queryset = queryset.filter(stock__gt=0)

            queryset = queryset.order_by('adjusted_price' if sort_by == 'price_asc' else '-adjusted_price')

        else:
            available_variant = ProductVariant.objects.filter(
                product=OuterRef('pk'), stock__gt=0
            ).order_by('price')

            queryset = Product.objects.annotate(
                default_variant_price=Subquery(available_variant.values('price')[:1]),
                default_variant_stock=Subquery(available_variant.values('stock')[:1]),
                default_variant_size=Subquery(available_variant.values('size')[:1]),
            )

            if not show_out_of_stock:
                queryset = queryset.filter(default_variant_stock__gt=0)

            if selected_categories and "" not in selected_categories:
                queryset = queryset.filter(category__slug__in=selected_categories)
            if price_min:
                queryset = queryset.filter(variants__price__gte=price_min)
            if price_max:
                queryset = queryset.filter(variants__price__lte=price_max)
            if min_rating:
                queryset = queryset.filter(rating__gte=min_rating)
            if search_query:
                queryset = queryset.filter(
                    Q(name__icontains=search_query) |
                    Q(description__icontains=search_query)
                )

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        products_with_context = []

        if isinstance(self.object_list.first(), ProductVariant):
            for variant in self.object_list:
                stock_by_size = {
                    v.size: {"price": v.price, "stock": v.stock}
                    for v in ProductVariant.objects.filter(product=variant.product)
                }

                products_with_context.append({
                    "product": variant.product,
                    "variant_size": variant.size,
                    "variant_price": variant.adjusted_price,
                    "variant_stock": variant.stock,
                    "stock_by_size": stock_by_size,
                })
        else:
            for product in self.object_list:
                stock_by_size = {
                    v.size: {"price": v.price, "stock": v.stock}
                    for v in ProductVariant.objects.filter(product=product)
                }

                products_with_context.append({
                    "product": product,
                    "variant_size": product.default_variant_size,
                    "variant_price": product.default_variant_price,
                    "variant_stock": product.default_variant_stock,
                    "stock_by_size": stock_by_size,
                    "buy_url": product.get_buy_url,
                })

        context.update({
            'products_with_context': products_with_context,
            'categories': Category.objects.values('slug', 'name'),
            'selected_categories': self.request.GET.getlist('category[]'),
            'total_review': range(5),
            'sorting_options': {
                'price_asc': 'Price: Low to High',
                'price_desc': 'Price: High to Low',
                'name_asc': 'Name: A to Z',
                'name_desc': 'Name: Z to A',
                'rating_asc': 'Rating: Low to High',
                'rating_desc': 'Rating: High to Low',
            },
            'show_out_of_stock': self.request.GET.get('show_out_of_stock') == 'on',
            'search_query': self.request.GET.get('q', ''),
            'view': 'list',
        })

        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'

    def get(self, request, *args, **kwargs):
        product = self.get_object()
        variants = product.variants.all()
        sizes = [variant.size for variant in variants]
        stock_by_size = {variant.size: variant for variant in variants}

        if 'size' not in request.GET:
            default_size = next(
                (size for size in sizes if stock_by_size[size].stock > 0),
                sizes[0] if sizes else None
            )
            if default_size:
                return redirect(f"{request.path}?size={default_size}")

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        variants = product.variants.all()
        sizes = [variant.size for variant in variants]
        stock_by_size = {variant.size: variant for variant in variants}

        selected_size = self.request.GET.get('size')

        if selected_size and selected_size in stock_by_size:
            default_size = selected_size
        else:
            default_size = next(
                (size for size in sizes if stock_by_size[size].stock > 0),
                sizes[0] if sizes else None
            )

        default_variant = stock_by_size.get(default_size)
        default_stock_status = "In Stock" if default_variant and default_variant.stock > 0 else "Out of Stock"
        default_price = default_variant.price if default_variant else None

        is_admin = self.request.user.is_authenticated and self.request.user.is_superuser

        context.update({
            'variants': variants,
            'sizes': sizes,
            'stock_by_size': stock_by_size,
            'default_size': default_size,
            'default_stock_status': default_stock_status,
            'default_price': default_price,
            'total_review': range(5),
            'view': 'detail',
            'buy_url': product.get_buy_url,
            'is_admin': is_admin,
        })
        return context

class ProductEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    fields = ['name', 'description', 'rating', 'category', 'is_active']
    template_name = 'product/admin_product_edit.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_success_url(self):
        return self.object.get_absolute_url()


class ProductDeactivateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=kwargs['pk'])
        product.is_active = False
        product.save()
        return redirect('product')
