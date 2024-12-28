import json
import os

# Django imports
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    View
)
from django.shortcuts import (
    get_object_or_404,
    redirect
)

from django.db.models import (
    F,
    Case,
    When,
    Value,
    IntegerField,
    Subquery,
    OuterRef,
    Q,
    Count,
    Avg,
    Exists
)
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin
)
from django.http import (
    JsonResponse,
    Http404
)
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.urls import reverse

# Third-party imports
from cloudinary.uploader import (
    upload,
    destroy
)

# Internal imports
from .forms import (
    ProductEditForm,
    ProductVariantForm,
    ProductReviewForm
)
from .models import (
    Product,
    ProductVariant,
    Category,
    ProductReview
)


class ProductListView(ListView):
    '''
    Display a list of products with filtering, sorting, and search options.

    Supports filters by category, price range, ratings, and stock status.
    Provides sorting options for price, name, and ratings.
    Admin users see inactive products and variants as well.
    '''
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        '''
        Retrieve and filter the queryset based on request parameters.

        Returns:
            QuerySet: Filtered and sorted list of products or variants.
        '''
        sort_by = self.request.GET.get('sort_by') or 'rating_desc'
        show_out_of_stock = self.request.GET.get('show_out_of_stock') == 'on'
        selected_categories = [
            c for c in self.request.GET.getlist('category[]') if c
        ]
        price_min = self.request.GET.get('price_min') or None
        price_max = self.request.GET.get('price_max') or None
        min_rating = self.request.GET.get('rating') or None
        search_query = self.request.GET.get('q') or None

        is_admin = (
            self.request.user.is_authenticated and
            (self.request.user.is_superuser or self.request.user.is_staff)
        )

        available_variant = ProductVariant.objects.filter(
            product=OuterRef('pk'), stock__gt=0
        ).order_by('price')

        queryset = Product.objects.annotate(
            default_variant_price=Subquery(
                available_variant.values('price')[:1]
            ),

            default_variant_stock=Subquery(
                available_variant.values('stock')[:1]
            ),

            default_variant_size=Subquery(
                available_variant.values('size')[:1]
            ),

            default_variant_active=Subquery(
                available_variant.values('active')[:1]
            ),

            default_variant_id=Subquery(
                available_variant.values('id')[:1]
            ),

            has_active_stock=Exists(
                ProductVariant.objects.filter(
                    product=OuterRef('pk'),
                    active=True,
                    stock__gt=0
                )
            )
        )

        if not is_admin:
            queryset = queryset.filter(
                active=True,
                variants__active=True,
                has_active_stock=True
            )
        if not show_out_of_stock:
            queryset = queryset.filter(default_variant_stock__gt=0)
        if selected_categories:
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

        if price_min or price_max or sort_by in ['price_asc', 'price_desc']:
            queryset = ProductVariant.objects.annotate(
                adjusted_price=Case(
                    When(stock__gt=0, then=F('price')),
                    default=Value(0),
                    output_field=IntegerField()
                )
            )

            if not is_admin:
                queryset = queryset.filter(
                    product__active=True, active=True
                )

            if selected_categories:
                queryset = queryset.filter(
                    product__category__slug__in=selected_categories
                )
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

            queryset = queryset.order_by(
                'adjusted_price'
                if sort_by == 'price_asc'
                else '-adjusted_price'
            )
        elif sort_by == 'rating_asc':
            queryset = queryset.order_by('rating')
        elif sort_by == 'rating_desc':
            queryset = queryset.order_by('-rating')
        elif sort_by == 'name_asc':
            queryset = queryset.order_by('name')
        elif sort_by == 'name_desc':
            queryset = queryset.order_by('-name')

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        '''
        Add additional data to the context for rendering the template.

        Returns:
            dict: Context data for the template.
        '''
        context = super().get_context_data(**kwargs)
        products_with_context = []
        is_admin = (
            self.request.user.is_authenticated and
            (self.request.user.is_superuser or self.request.user.is_staff)
        )

        if self.object_list.first() and isinstance(
            self.object_list.first(), ProductVariant
        ):
            for variant in self.object_list:
                stock_by_size = {
                    v.size: {
                        "price": v.price,
                        "stock": v.stock,
                        "id": v.id,
                        "active": v.active,
                    }
                    for v in (
                        ProductVariant.objects.filter(
                            product=variant.product, active=True
                        )
                        if not is_admin
                        else ProductVariant.objects.filter(
                            product=variant.product
                        )
                    )
                }

                products_with_context.append({
                    "product": variant.product,
                    "variant_id": variant.id,
                    "variant_size": variant.size,
                    "variant_price": variant.adjusted_price,
                    "variant_stock": variant.stock,
                    "size_active": variant.active,
                    "stock_by_size": stock_by_size,
                })
        else:
            for product in self.object_list:
                variants_qs = (
                    product.variants.all()
                    if is_admin
                    else product.variants.filter(active=True)
                )
                stock_by_size = {
                    v.size: {
                        "price": v.price,
                        "stock": v.stock,
                        "id": v.id,
                        "active": v.active,
                    }
                    for v in variants_qs
                }

                products_with_context.append({
                    "product": product,
                    "variant_id": product.default_variant_id,
                    "variant_size": product.default_variant_size,
                    "variant_price": product.default_variant_price,
                    "variant_stock": product.default_variant_stock,
                    "size_active": product.default_variant_active,
                    "stock_by_size": stock_by_size,
                    "buy_url": product.get_buy_url,
                })

        category_items = [
            {"id": category.id, "name": category.name, "slug": category.slug}
            for category in Category.objects.all().order_by('slug')
        ]

        context.update({
            'products_with_context': products_with_context,
            'category': Category.objects.values('slug', 'name'),
            'category_items': category_items,
            'selected_categories': self.request.GET.getlist('category[]'),
            'max_review': range(5),
            'sorting_options': {
                'price_asc': 'Price: Low to High',
                'price_desc': 'Price: High to Low',
                'name_asc': 'Name: A to Z',
                'name_desc': 'Name: Z to A',
                'rating_asc': 'Rating: Low to High',
                'rating_desc': 'Rating: High to Low',
            },
            'show_out_of_stock': self.request.GET.get(
                'show_out_of_stock'
            ) == 'on',
            'search_query': self.request.GET.get('q', ''),
            'view': 'list',
            'is_admin': is_admin,
        })

        return context


class ProductDetailView(DetailView):
    '''
    Display detailed information about a single product, including
    variants and reviews. Handle review creation via POST.

    For non-admin users, ensure the product and its variants are active.
    '''
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'

    def get(self, request, *args, **kwargs):
        '''
        Handle GET requests for product details.

        Check product and variant availability for non-admin users and
        redirect if necessary.
        '''
        product = self.get_object()
        is_admin = (
            request.user.is_authenticated and
            (request.user.is_superuser or request.user.is_staff)
        )

        if not is_admin and not product.active:
            raise Http404('This product is no longer available.')

        variants_qs = (
            product.variants.all()
            if is_admin
            else product.variants.filter(active=True)
        )

        if not is_admin and variants_qs.count() == 0:
            raise Http404('This product is no longer available.')

        selected_size = request.GET.get('size')
        stock_by_size = {variant.size: variant for variant in variants_qs}

        if selected_size and selected_size not in stock_by_size:
            fallback_variant = next(
                (v for v in variants_qs if v.stock > 0),
                variants_qs.first() if variants_qs else None
            )
            if not fallback_variant:
                if is_admin:
                    return super().get(request, *args, **kwargs)
                raise Http404('This product is no longer available.')

            return self._redirect_with_size(request, fallback_variant.size)

        return super().get(request, *args, **kwargs)

    def _redirect_with_size(self, request, size):
        '''
        Redirect to the same page with the specified size query parameter.

        Args:
            request: The current request object.
            size: The size to include in the query parameter.

        Returns:
            HttpResponseRedirect: Redirect response to the updated URL.
        '''
        url = f"{request.path}?size={size}"
        return redirect(url)

    def post(self, request, *args, **kwargs):
        '''
        Handle submission of a new product review via POST request.

        Always returns a JSON response.
        '''
        self.object = self.get_object()
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = self.object
            review.user = (
                request.user if request.user.is_authenticated else None
            )
            review.save()
            self.object.rating = self.object.average_rating
            self.object.save()
            return JsonResponse({
                'success': True,
                'redirect_url': self.object.get_absolute_url()
            })
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)

    def get_context_data(self, **kwargs):
        '''
        Add product details, variants, categories, reviews, and meta
        tags to the context.

        Returns:
            dict: Context data for the template.
        '''
        context = super().get_context_data(**kwargs)
        product = self.object
        is_admin = (
            self.request.user.is_authenticated and
            (self.request.user.is_superuser or self.request.user.is_staff)
        )

        variants = (
            product.variants.all().order_by('price')
            if is_admin
            else product.variants.filter(active=True).order_by('price')
        )
        sizes = [variant.size for variant in variants]
        stock_by_size = {variant.size: variant for variant in variants}

        selected_size = self.request.GET.get('size')
        default_size = (
            selected_size if selected_size in stock_by_size else
            (sizes[0] if sizes else None)
        )
        default_variant = stock_by_size.get(default_size)
        default_stock_status = (
            'In Stock'
            if default_variant and default_variant.stock > 0
            else 'Out of Stock'
        )
        default_price = (
            default_variant.price if default_variant else None
        )
        default_stock = (
            default_variant.stock if default_variant else None
        )
        default_variant_id = (
            default_variant.id if default_variant else None
        )
        size_active = (
            default_variant.active if default_variant else False
        )

        product_form = (
            ProductEditForm(instance=product) if is_admin else None
        )
        variant_form = (
            ProductVariantForm(instance=default_variant)
            if is_admin else None
        )

        rating_summary = (
            product.reviews.values('rating')
            .annotate(count=Count('rating'))
            .order_by('rating')
        )
        total_reviews = product.reviews.count()
        rating_summary_dict = {i: 0 for i in range(6)}
        for entry in rating_summary:
            rating_summary_dict[entry['rating']] = entry['count']

        visible_reviews = (
            product.reviews.filter(~Q(comment=''))
            if is_admin else
            product.reviews.filter(silenced=False)
            .exclude(comment='')
            .order_by('-created_at')
        )

        review_form = ProductReviewForm()

        selected_category = product.category.id
        category_items = [
            {"id": category.id, "name": category.name}
            for category in Category.objects.all().order_by('slug')
        ]

        meta_description = (
            f"Buy {product.name} in {product.category.name} category. "
            f"Enjoy premium quality with sizes like {', '.join(sizes)}. "
            "Perfect for coffee enthusiasts."
        )
        meta_keywords = (
            f"{product.name}, {product.category.name}, {' '.join(sizes)}, "
            "premium coffee, coffee accessories, buy coffee online, "
            "specialty coffee"
        )

        context.update({
            'selected_category': selected_category,
            'variants': variants,
            'sizes': sizes,
            'stock_by_size': stock_by_size,
            'default_size': default_size,
            'default_stock': default_stock,
            'default_stock_status': default_stock_status,
            'default_price': default_price,
            'default_variant_id': default_variant_id,
            'size_active': size_active,
            'max_review': range(5),
            'view': 'detail',
            'buy_url': product.get_buy_url,
            'is_admin': is_admin,
            'product_form': product_form,
            'variant_form': variant_form,
            'reviews': visible_reviews,
            'review_form': review_form,
            'rating_summary': rating_summary_dict,
            'total_reviews': total_reviews,
            'category_items': category_items,
            'meta_description': meta_description,
            'meta_keywords': meta_keywords,
        })
        return context


class ProductDeactivateView(LoginRequiredMixin, UserPassesTestMixin, View):
    '''
    Toggle a product's active state. Admin-only.

    Always returns a JSON response.
    '''
    def test_func(self):
        '''
        Check if the user has the necessary permissions.

        Returns:
            bool: True if the user is superuser or staff.
        '''
        return self.request.user.is_superuser or self.request.user.is_staff

    def post(self, request, pk):
        '''
        Handle POST request to toggle product active state.

        Args:
            request: The incoming HTTP request.
            pk (int): The primary key of the product to toggle.

        Returns:
            JsonResponse: Response indicating success or failure.
        '''
        try:
            product = Product.objects.get(pk=pk)
            product.active = not product.active
            product.save()
            return JsonResponse({
                'success': True, 'active': product.active
            })
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False, 'error': 'Product not found'
            }, status=404)


class VariantDeactivateView(LoginRequiredMixin, UserPassesTestMixin, View):
    '''
    Toggle a variant's active state. Admin-only.

    Always returns a JSON response.
    '''
    def test_func(self):
        '''
        Check if the user has the necessary permissions.

        Returns:
            bool: True if the user is superuser or staff.
        '''
        return self.request.user.is_superuser or self.request.user.is_staff

    def post(self, request, pk):
        '''
        Handle POST request to toggle variant active state.

        Args:
            request: The incoming HTTP request.
            pk (int): The primary key of the variant to toggle.

        Returns:
            JsonResponse: Response indicating success or failure.
        '''
        try:
            variant = ProductVariant.objects.get(pk=pk)
            variant.active = not variant.active
            variant.save()
            return JsonResponse({
                'success': True, 'active': variant.active
            })
        except ProductVariant.DoesNotExist:
            return JsonResponse({
                'success': False, 'error': 'Size not found'
            }, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class SaveSelector(LoginRequiredMixin, UserPassesTestMixin, View):
    '''
    Handle dynamic addition or editing of categories and sizes (variants)
    via JSON POST. Admin-only.

    Always returns a JSON response.
    '''
    def test_func(self):
        '''
        Check if the user has the necessary permissions.

        Returns:
            bool: True if the user is superuser or staff.
        '''
        return self.request.user.is_superuser or self.request.user.is_staff

    def post(self, request, selector_type):
        '''
        Handle POST request to add or edit categories and sizes.

        Args:
            request: The incoming HTTP request.
            selector_type (str): The type of selector ('category' or 'size').

        Returns:
            JsonResponse: Response indicating success or failure.
        '''
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False, 'error': 'Invalid JSON payload.'
            }, status=400)

        action = data.get('action')
        name = data.get('name')
        current_value = data.get('current_value')
        product_id = data.get('product_id', None)

        if selector_type == 'category':
            return self.handle_category(action, name, current_value)
        elif selector_type == 'size':
            return self.handle_size(action, name, current_value, product_id)
        return JsonResponse({
            'success': False, 'error': 'Invalid selector type.'
        }, status=400)

    def handle_category(self, action, name, current_value):
        '''
        Handle category addition or editing.

        Args:
            action (str): The action to perform ('add' or 'edit').
            name (str): The name of the category.
            current_value (str): The ID of the category to edit.

        Returns:
            JsonResponse: Response indicating success or failure.
        '''
        if action == 'add':
            try:
                new_category = Category.objects.create(name=name)
                return JsonResponse({
                    'success': True,
                    'name': new_category.name,
                    'slug': new_category.slug,
                    'id': new_category.id
                })
            except IntegrityError:
                return JsonResponse({
                    'success': False,
                    'error': (
                        f"A category with the name '{name}' already exists."
                    )
                }, status=400)

        elif action == 'edit' and current_value:
            try:
                category = Category.objects.get(id=current_value)
                category.name = name
                category.save()
                return JsonResponse({
                    'success': True,
                    'name': category.name,
                    'id': category.id
                })
            except IntegrityError:
                return JsonResponse({
                    'success': False,
                    'error': (
                        f"A category with the name '{name}' already exists."
                    )
                }, status=400)
            except Category.DoesNotExist:
                return JsonResponse({
                    'success': False, 'error': 'Category not found.'
                }, status=404)

        return JsonResponse({
            'success': False, 'error': 'Invalid action or missing data.'
        }, status=400)

    def handle_size(self, action, name, current_value, product_id):
        '''
        Handle size addition or editing.

        Args:
            action (str): The action to perform ('add' or 'edit').
            name (str): The name of the size.
            current_value (str): The size to edit.
            product_id (int): The ID of the product associated with the size.

        Returns:
            JsonResponse: Response indicating success or failure.
        '''
        if not product_id:
            return JsonResponse({
                'success': False, 'error': 'Missing product.'
            }, status=404)

        product = get_object_or_404(Product, pk=product_id)

        if action == 'add':
            try:
                variant = ProductVariant.objects.create(
                    product=product,
                    size=name,
                    price=0,
                    stock=0
                )
                return JsonResponse({
                    'success': True,
                    'name': variant.size,
                    'slug': variant.size,
                    'id': variant.id
                })
            except IntegrityError:
                return JsonResponse({
                    'success': False,
                    'error': f"A size with the name '{name}' already exists."
                }, status=200)

        elif action == 'edit' and current_value:
            try:
                variant = ProductVariant.objects.get(
                    product=product, size=current_value
                )
                variant.size = name
                variant.save()
                return JsonResponse({
                    'success': True,
                    'name': variant.size,
                    'slug': variant.size,
                    'id': variant.id
                })
            except IntegrityError:
                return JsonResponse({
                    'success': False,
                    'error': f"A size with the name '{name}' already exists."
                }, status=400)
            except ProductVariant.DoesNotExist:
                return JsonResponse({
                    'success': False, 'error': 'Variant not found.'
                }, status=404)

        return JsonResponse({
            'success': False, 'error': 'Invalid action or missing data.'
        }, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class ReviewSilenceToggler(LoginRequiredMixin, UserPassesTestMixin, View):
    '''
    Toggle the 'silenced' state of a review. Admin-only.

    Always returns a JSON response.
    '''
    def test_func(self):
        '''
        Check if the user has the necessary permissions.

        Returns:
            bool: True if the user is superuser or staff.
        '''
        return self.request.user.is_superuser or self.request.user.is_staff

    def post(self, request, review_id):
        '''
        Handle POST request to toggle the silenced state of a review.

        Args:
            request: The incoming HTTP request.
            review_id (int): The ID of the review to toggle.

        Returns:
            JsonResponse: Response indicating success or failure.
        '''
        try:
            review = ProductReview.objects.get(id=review_id)
            review.silenced = not review.silenced
            review.save()
            return JsonResponse({
                'success': True, 'silenced': review.silenced
            })
        except ProductReview.DoesNotExist:
            return JsonResponse({
                'success': False, 'error': 'Review not found'
            }, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class ProductSaveView(LoginRequiredMixin, UserPassesTestMixin, View):
    '''
    Save changes to a product and its variant. Admin-only.

    Expects form data (including an optional image) and product/variant
    data as JSON strings. Always returns JSON response with
    success/error messages.
    '''
    def test_func(self):
        '''
        Check if the user has the necessary permissions.

        Returns:
            bool: True if the user is superuser or staff.
        '''
        return self.request.user.is_superuser or self.request.user.is_staff

    def post(self, request, *args, **kwargs):
        '''
        Handle POST request to save product and variant changes.

        Args:
            request: The incoming HTTP request.

        Returns:
            JsonResponse: Response indicating success or failure.
        '''
        product_id = request.POST.get('product_id')
        variant_id = request.POST.get('variant_id')

        if not product_id:
            return JsonResponse({
                'success': False, 'error': 'Product is required.'
            }, status=400)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False, 'error': 'Product not found.'
            }, status=404)

        previous_values = {
            'active': product.active,
        }

        product_data = json.loads(request.POST.get('product', '{}'))

        for field, value in previous_values.items():
            if field not in product_data:
                product_data[field] = value

        product_form = ProductEditForm(product_data, instance=product)

        if not product_form.is_valid():
            return JsonResponse({
                'success': False,
                'errors': product_form.errors.get_json_data()
            }, status=400)

        try:
            product_form.save()
        except IntegrityError as e:
            if 'unique constraint' in str(e).lower():
                return JsonResponse({
                    'success': False,
                    'error': 'Duplicate product name or slug detected.'
                }, status=400)

        if 'image' in request.FILES:
            image_file = request.FILES['image']
            if product.image_path:
                destroy(product.image_path.public_id)
            new_file_name = f'products/{product.slug}'
            upload_result = upload(
                image_file,
                public_id=new_file_name,
                overwrite=True,
                resource_type='image'
            )
            product.image_path = upload_result['public_id']
            product.cloudinary_version = upload_result.get('version')
            product.save()

        if variant_id:
            try:
                variant = ProductVariant.objects.get(id=variant_id)
            except ProductVariant.DoesNotExist:
                return JsonResponse({
                    'success': False, 'error': 'Size not found.'
                }, status=404)

            variant_data = json.loads(request.POST.get('variant', '{}'))
            variant_form = ProductVariantForm(variant_data, instance=variant)

            if not variant_form.is_valid():
                return JsonResponse({
                    'success': False,
                    'errors': variant_form.errors.get_json_data()
                }, status=400)

            try:
                variant_form.save()
            except IntegrityError as e:
                if 'unique constraint' in str(e).lower():
                    return JsonResponse({
                        'success': False,
                        'error': 'Duplicate size name detected.'
                    }, status=400)

        return JsonResponse({
            'success': True,
            'redirect_url': product.get_absolute_url()
        })


@method_decorator(csrf_exempt, name='dispatch')
class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    '''
    Create a new product. Admin-only.

    For POST requests, expects JSON data in product field or standard
    form fields. Always returns JSON responses.
    '''
    model = Product
    form_class = ProductEditForm
    template_name = 'product/product_detail.html'

    def test_func(self):
        '''
        Check if the user has the necessary permissions.

        Returns:
            bool: True if the user is superuser or staff.
        '''
        return self.request.user.is_superuser or self.request.user.is_staff

    def post(self, request, *args, **kwargs):
        '''
        Handle POST request to create a new product.

        Args:
            request: The incoming HTTP request.

        Returns:
            JsonResponse: Response indicating success or failure.
        '''
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                product_data = data.get('product', {})
            else:
                product_data = request.POST.dict()
                if 'product' in product_data:
                    product_data = json.loads(product_data['product'])

            form = self.form_class(product_data)

            if form.is_valid():
                try:
                    product = form.save()
                except IntegrityError as e:
                    if 'unique constraint' in str(e).lower():
                        return JsonResponse({
                            'success': False,
                            'error': 'Duplicate product name or slug detected.'
                        }, status=400)
                    raise e

                return JsonResponse({
                    'success': True,
                    'product_id': product.id,
                    'redirect_url': reverse('product_detail', kwargs={
                        'slug': product.slug
                    }),
                })

            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data()
            }, status=400)

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False, 'error': 'Invalid JSON payload.'
            }, status=400)
        except IntegrityError as e:
            if 'unique constraint' in str(e).lower():
                return JsonResponse({
                    'success': False,
                    'error': 'Duplicate product name detected.'
                }, status=400)
            return JsonResponse({
                'success': False, 'error': str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False, 'error': str(e)
            }, status=500)

    def get_context_data(self, **kwargs):
        '''
        Add contextual data for the template.

        Returns:
            dict: Context data for the template.
        '''
        context = super().get_context_data(**kwargs)
        context['product_form'] = self.get_form()
        context['category_items'] = [
            {"id": category.id, "name": category.name}
            for category in Category.objects.all().order_by('slug')
        ]
        context['is_admin'] = (
            self.request.user.is_authenticated and
            (self.request.user.is_superuser or self.request.user.is_staff)
        )
        context['view'] = 'detail'
        return context
