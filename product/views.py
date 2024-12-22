from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.shortcuts import get_object_or_404, redirect
from .models import Product, ProductVariant, Category, ProductReview
from django.db.models import F, Case, When, Value, IntegerField, Subquery, OuterRef, Q, Count, Avg
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import ProductEditForm, ProductVariantForm, ProductReviewForm
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import IntegrityError
from django.core.exceptions import ValidationError
import json, os
from cloudinary.uploader import upload, destroy
from django.urls import reverse


class ProductListView(ListView):
    """
    Displays a list of products, applying various filtering (categories, prices, ratings, stock)
    and sorting options (price ascending/descending). Supports searching by name/description.
    If user is staff/admin, shows inactive products and variants as well.
    """
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        # Retrieve query parameters, ensuring empty ones are skipped
        sort_by = self.request.GET.get('sort_by') or 'rating_desc'
        show_out_of_stock = self.request.GET.get('show_out_of_stock') == 'on'
        selected_categories = [c for c in self.request.GET.getlist('category[]') if c]
        price_min = self.request.GET.get('price_min') or None
        price_max = self.request.GET.get('price_max') or None
        min_rating = self.request.GET.get('rating') or None
        search_query = self.request.GET.get('q') or None

        is_admin = self.request.user.is_authenticated and (self.request.user.is_superuser or self.request.user.is_staff)

        # Subquery to fetch variant data
        available_variant = ProductVariant.objects.filter(
            product=OuterRef('pk'), stock__gt=0
        ).order_by('price')

        # Start with Product queryset and annotate variant info
        queryset = Product.objects.annotate(
            default_variant_price=Subquery(available_variant.values('price')[:1]),
            default_variant_stock=Subquery(available_variant.values('stock')[:1]),
            default_variant_size=Subquery(available_variant.values('size')[:1]),
            default_variant_active=Subquery(available_variant.values('active')[:1]),
            default_variant_id=Subquery(available_variant.values('id')[:1]),
        )

        # Apply filters
        if not is_admin:
            queryset = queryset.filter(active=True, variants__active=True)
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

        # Apply sorting
        if price_min or price_max or sort_by in ['price_asc', 'price_desc']:
            # Starting from ProductVariant queryset
            queryset = ProductVariant.objects.annotate(
                adjusted_price=Case(
                    When(stock__gt=0, then=F('price')),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            )

            # If not admin, only consider active products and active variants
            if not is_admin:
                queryset = queryset.filter(product__active=True, active=True)

            # Apply filters
            if selected_categories:
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
        """
        Add contextual data including variant info, categories, sorting options,
        and flags indicating admin status.
        """
        context = super().get_context_data(**kwargs)
        products_with_context = []
        is_admin = self.request.user.is_authenticated and (self.request.user.is_superuser or self.request.user.is_staff)

        if self.object_list.first() and isinstance(self.object_list.first(), ProductVariant):
            # If queryset is product variants
            for variant in self.object_list:
                stock_by_size = {
                    v.size: {
                        "price": v.price,
                        "stock": v.stock,
                        "id": v.id,
                        "active": v.active,
                    }
                    for v in (ProductVariant.objects.filter(product=variant.product, active=True) if not is_admin else ProductVariant.objects.filter(product=variant.product))
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
            # If queryset is products
            for product in self.object_list:
                variants_qs = product.variants.all() if is_admin else product.variants.filter(active=True)
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
            'show_out_of_stock': self.request.GET.get('show_out_of_stock') == 'on',
            'search_query': self.request.GET.get('q', ''),
            'view': 'list',
            'is_admin': is_admin,
        })

        return context


class ProductDetailView(DetailView):
    """
    Displays detailed information about a single product, including variants and reviews.
    If the product or variants are not available for non-admin users, returns 404.
    Allows creation of reviews via POST request.
    """
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'

    def get(self, request, *args, **kwargs):
        product = self.get_object()
        is_admin = request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)

        # Check product availability for non-admin users
        if not is_admin and not product.active:
            raise Http404("This product is no longer available.")

        variants_qs = product.variants.all() if is_admin else product.variants.filter(active=True)
        if not is_admin and variants_qs.count() == 0:
            raise Http404("This product is no longer available.")

        selected_size = request.GET.get('size')
        stock_by_size = {variant.size: variant for variant in variants_qs}

        # If requested size not found, redirect to a fallback if possible
        if selected_size and selected_size not in stock_by_size:
            fallback_variant = None
            for v in variants_qs:
                if v.stock > 0:
                    fallback_variant = v
                    break
            if not fallback_variant and variants_qs:
                fallback_variant = variants_qs.first()
            if not fallback_variant:
                raise Http404("This product is no longer available.")
            return self._redirect_with_size(request, fallback_variant.size)

        # If no size specified, pick a default
        if 'size' not in request.GET:
            default_variant = None
            for v in variants_qs:
                if v.stock > 0:
                    default_variant = v
                    break
            if not default_variant and variants_qs:
                default_variant = variants_qs.first()
            if not default_variant:
                raise Http404("This product is no longer available.")
            return self._redirect_with_size(request, default_variant.size)

        return super().get(request, *args, **kwargs)

    def _redirect_with_size(self, request, size):
        """
        Helper method to redirect to the same page with a given size query parameter.
        """
        url = f"{request.path}?size={size}"
        return redirect(url)

    def post(self, request, *args, **kwargs):
        """
        Handles submission of a new product review.
        Always returns JSON.
        """
        self.object = self.get_object()
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = self.object
            review.user = request.user if request.user.is_authenticated else None
            review.save()
            # Update product rating
            self.object.rating = self.object.average_rating
            self.object.save()
            return JsonResponse({"success": True, "redirect_url": self.object.get_absolute_url()})
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    def get_context_data(self, **kwargs):
        """
        Add product details, variants, category items, review summaries, and editing forms for admins.
        """
        context = super().get_context_data(**kwargs)
        product = self.object
        is_admin = self.request.user.is_authenticated and (self.request.user.is_superuser or self.request.user.is_staff)

        variants = product.variants.all().order_by('price') if is_admin else product.variants.filter(active=True).order_by('price')
        sizes = [variant.size for variant in variants]
        stock_by_size = {variant.size: variant for variant in variants}

        selected_size = self.request.GET.get('size')
        default_size = selected_size if selected_size and selected_size in stock_by_size else (sizes[0] if sizes else None)
        default_variant = stock_by_size.get(default_size)
        default_stock_status = "In Stock" if default_variant and default_variant.stock > 0 else "Out of Stock"
        default_price = default_variant.price if default_variant else None
        default_stock = default_variant.stock if default_variant else None
        default_variant_id = default_variant.id if default_variant else None
        size_active = default_variant.active if default_variant else False

        product_form = ProductEditForm(instance=product) if is_admin else None
        variant_form = ProductVariantForm(instance=default_variant) if is_admin and default_variant else None

        # Rating summary
        rating_summary = product.reviews.values('rating').annotate(count=Count('rating')).order_by('rating')
        total_reviews = product.reviews.count()
        rating_summary_dict = {i: 0 for i in range(6)}
        for entry in rating_summary:
            rating_summary_dict[entry['rating']] = entry['count']

        if is_admin:
            visible_reviews = product.reviews.filter(~Q(comment="")).order_by('-created_at')
        else:
            visible_reviews = product.reviews.filter(silenced=False).exclude(comment="").order_by('-created_at')

        review_form = ProductReviewForm()

        selected_category = product.category.id
        category_items = [
            {"id": category.id, "name": category.name}
            for category in Category.objects.all().order_by('slug')
        ]

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
        })
        return context


class ProductEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Allows staff or superusers to edit an existing product.
    POST requests return JSON responses for success or errors.
    """
    model = Product
    fields = ['name', 'description', 'category', 'active']
    template_name = 'product/product_detail.html'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_invalid(self, form):
        return JsonResponse({"success": False, "errors": form.errors}, status=400)

    def form_valid(self, form):
        product = form.save()
        return JsonResponse({"success": True, "redirect_url": product.get_absolute_url()})

    def post(self, request, *args, **kwargs):
        # Overridden to ensure JSON response on POST
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return self.object.get_absolute_url()


class ProductDeactivateView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Toggles a product's active state. Admin-only.
    Always returns JSON response.
    """
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def post(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            product.active = not product.active
            product.save()
            return JsonResponse({"success": True, "active": product.active})
        except Product.DoesNotExist:
            return JsonResponse({"success": False, "error": "Product not found"}, status=404)


class VariantDeactivateView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Toggles a variant's active state. Admin-only.
    Always returns JSON response.
    """
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def post(self, request, pk):
        try:
            variant = ProductVariant.objects.get(pk=pk)
            variant.active = not variant.active
            variant.save()
            return JsonResponse({"success": True, "active": variant.active})
        except ProductVariant.DoesNotExist:
            return JsonResponse({"success": False, "error": "Size not found"}, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class SaveSelector(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Handle dynamic addition or editing of categories and sizes (variants) via JSON POST.
    Admin-only. Always returns JSON response.
    """
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def post(self, request, selector_type):
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON payload."}, status=400)

        action = data.get('action')
        name = data.get('name')
        current_value = data.get('current_value')
        product_id = data.get('product_id', None)

        if selector_type == "category":
            return self.handle_category(action, name, current_value)
        elif selector_type == "size":
            return self.handle_size(action, name, current_value, product_id)
        else:
            return JsonResponse({"success": False, "error": "Invalid selector type."}, status=400)

    def handle_category(self, action, name, current_value):
        if action == "add":
            new_category = Category.objects.create(name=name)
            return JsonResponse({
                "success": True,
                "name": new_category.name,
                "slug": new_category.slug,
                "id": new_category.id
            })

        elif action == "edit" and current_value:
            try:
                category = Category.objects.get(id=current_value)
                category.name = name
                category.save()
                return JsonResponse({
                    "success": True,
                    "name": category.name,
                    "id": category.id
                })
            except Category.DoesNotExist:
                return JsonResponse({"success": False, "error": "Category not found."}, status=404)

        return JsonResponse({"success": False, "error": "Invalid action or missing data."}, status=400)

    def handle_size(self, action, name, current_value, product_id):
        if not product_id:
            return JsonResponse({"success": False, "error": "Missing product_id."}, status=400)

        product = get_object_or_404(Product, pk=product_id)

        if action == "add":
            variant = ProductVariant.objects.create(
                product=product,
                size=name,
                price=0,
                stock=0
            )
            return JsonResponse({
                "success": True,
                "name": variant.size,
                "slug": variant.size,
                "id": variant.id
            })

        elif action == "edit" and current_value:
            try:
                variant = ProductVariant.objects.get(product=product, size=current_value)
                variant.size = name
                variant.save()
                return JsonResponse({
                    "success": True,
                    "name": variant.size,
                    "slug": variant.size,
                    "id": variant.id
                })
            except ProductVariant.DoesNotExist:
                return JsonResponse({"success": False, "error": "Variant not found."}, status=404)

        return JsonResponse({"success": False, "error": "Invalid action or missing data."}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class ReviewSilenceToggler(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Toggle the 'silenced' state of a review. Admin-only.
    Always returns JSON response.
    """
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def post(self, request, review_id):
        try:
            review = ProductReview.objects.get(id=review_id)
            review.silenced = not review.silenced
            review.save()
            return JsonResponse({"success": True, "silenced": review.silenced})
        except ProductReview.DoesNotExist:
            return JsonResponse({"success": False, "error": "Review not found"}, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class ProductSaveView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Save changes to a product and its variant. Admin-only.
    Expects form data (including an optional image) and product/variant data as JSON strings.
    Always returns JSON response with success/error messages.
    """
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        variant_id = request.POST.get('variant_id')

        # Validate required fields
        if not product_id or not variant_id:
            return JsonResponse({"success": False, "error": "Missing product_id or variant_id."}, status=400)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({"success": False, "error": "Product not found."}, status=404)

        try:
            variant = ProductVariant.objects.get(id=variant_id)
        except ProductVariant.DoesNotExist:
            return JsonResponse({"success": False, "error": "Variant not found."}, status=404)

        # Load product and variant data
        product_data = json.loads(request.POST.get('product', '{}'))
        variant_data = json.loads(request.POST.get('variant', '{}'))

        category_id = product_data.get('category')
        if not category_id:
            return JsonResponse({"success": False, "error": "Category not specified."}, status=400)

        category = get_object_or_404(Category, id=category_id)

        product_form = ProductEditForm(product_data, instance=product)
        if not product_form.is_valid():
            return JsonResponse({"success": False, "errors": product_form.errors}, status=400)

        # Save product
        product = product_form.save(commit=False)
        product.category = category

        # Handle potential slug uniqueness issues
        try:
            product.save()
        except IntegrityError as e:
            if 'unique constraint' in str(e).lower():
                return JsonResponse({"success": False, "error": "Duplicate product name or slug detected."}, status=400)
            raise e

        # Handle image upload if provided
        if 'image' in request.FILES:
            image_file = request.FILES['image']
            if product.image_path:
                destroy(product.image_path.public_id)
            new_file_name = f"products/{product.slug}"
            upload_result = upload(
                image_file,
                public_id=new_file_name,
                overwrite=True,
                resource_type="image"
            )
            product.image_path = upload_result['public_id']
            product.cloudinary_version = upload_result.get('version')
            product.save()

        # Validate and save variant
        variant_form = ProductVariantForm(variant_data, instance=variant)
        if not variant_form.is_valid():
            return JsonResponse({"success": False, "errors": variant_form.errors}, status=400)

        try:
            variant_form.save()
        except IntegrityError as e:
            if 'unique constraint' in str(e).lower():
                return JsonResponse({"success": False, "error": "Duplicate variant size detected."}, status=400)
            raise e

        return JsonResponse({"success": True, "redirect_url": product.get_absolute_url()})


@method_decorator(csrf_exempt, name='dispatch')
class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Create a new product. Admin-only.
    For POST requests, expects JSON data in product field or standard form fields.
    Always returns JSON responses.
    """
    model = Product
    form_class = ProductEditForm
    template_name = 'product/product_detail.html'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def post(self, request, *args, **kwargs):
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                product_data = data.get('product', {})
                variant_data = data.get('variant')  # Handle optional variant data
            else:
                product_data = request.POST.dict()
                if 'product' in product_data:  # Extract JSON from 'product' key
                    product_data = json.loads(product_data['product'])
                variant_data = None

            form = self.form_class(product_data)

            if form.is_valid():
                product = form.save()
                if variant_data:  # Handle size/variant creation only if provided
                    ProductVariant.objects.create(
                        product=product,
                        size=variant_data.get('size'),
                        price=variant_data.get('price', 0),
                        stock=variant_data.get('stock', 0),
                    )
                return JsonResponse({
                    "success": True,
                    "product_id": product.id,
                    "redirect_url": reverse('product_edit', kwargs={"pk": product.id}),
                })
            else:
                print("Form Errors:", form.errors)
                return JsonResponse({
                    "success": False,
                    "type": "warning",
                    "message": json.loads(form.errors.as_json())
                }, status=200)
        except json.JSONDecodeError as e:
            return JsonResponse({"success": False, "type": "error", "message": "Invalid JSON payload."}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "type": "error", "message": str(e)}, status=500)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_form'] = self.get_form()
        category_items = [
            {"id": category.id, "name": category.name}
            for category in Category.objects.all().order_by('slug')
        ]
        context['category_items'] = category_items
        context['is_admin'] = self.request.user.is_authenticated and (self.request.user.is_superuser or self.request.user.is_staff)
        context['view'] = 'detail'
        return context
