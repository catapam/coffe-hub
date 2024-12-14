from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, redirect
from .models import Product, ProductVariant, Category, ProductReview
from django.db.models import Min, F, Case, When, Value, IntegerField, Subquery, OuterRef, Q, Count
from django.views.generic.edit import UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import ProductEditForm, ProductVariantForm, ProductReviewForm
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib import messages
import json, os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from cloudinary.uploader import upload, destroy


class ProductListView(ListView):
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        sort_by = self.request.GET.get('sort_by')
        show_out_of_stock = self.request.GET.get('show_out_of_stock') == 'on'
        selected_categories = self.request.GET.getlist('category[]')
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')
        min_rating = self.request.GET.get('rating')
        search_query = self.request.GET.get('q')  # Capture the search query

        is_admin = self.request.user.is_authenticated and (self.request.user.is_superuser or self.request.user.is_staff)

        if sort_by in ['price_asc', 'price_desc']:
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
            # Starting from Product queryset
            available_variant = ProductVariant.objects.filter(
                product=OuterRef('pk'), stock__gt=0
            ).order_by('price')

            queryset = Product.objects.annotate(
                default_variant_price=Subquery(available_variant.values('price')[:1]),
                default_variant_stock=Subquery(available_variant.values('stock')[:1]),
                default_variant_size=Subquery(available_variant.values('size')[:1]),
                default_variant_active=Subquery(available_variant.values('active')[:1]),
                default_variant_id=Subquery(available_variant.values('id')[:1]),
            )

            # If not admin: only consider active products that have at least one active variant
            # By joining with variants__active=True, we ensure products have active variants
            if not is_admin:
                queryset = queryset.filter(active=True, variants__active=True)

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
        is_admin = self.request.user.is_authenticated and (self.request.user.is_superuser or self.request.user.is_staff)

        if self.object_list.first() and isinstance(self.object_list.first(), ProductVariant):
            # If queryset is variants
            for variant in self.object_list:
                # If not admin, only show active variants (already filtered in queryset)
                stock_by_size = {
                    v.size: {
                        "price": v.price,
                        "stock": v.stock,
                        "id": v.id,
                        "active": v.active,
                    }
                for v in (ProductVariant.objects.filter(product=variant.product, active=True) if not is_admin else ProductVariant.objects.filter(product=variant.product))                }

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
                        "id": v.id,  # Ensure variant ID is passed
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

        context.update({
            'products_with_context': products_with_context,
            'category': Category.objects.values('slug', 'name'),
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
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'

    def get(self, request, *args, **kwargs):
        product = self.get_object()

        is_admin = request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)

        # If not admin and product not active, show error and 404
        if not is_admin and not product.active:
            messages.error(request, "This product is no longer available.")
            raise Http404

        # Filter variants based on admin status
        variants_qs = product.variants.all() if is_admin else product.variants.filter(active=True)

        # If no active variants for non-admin user, 404 with message
        if not is_admin and variants_qs.count() == 0:
            messages.error(request, "This product is no longer available.")
            raise Http404

        sizes = [variant.size for variant in variants_qs]
        stock_by_size = {variant.size: variant for variant in variants_qs}

        selected_size = request.GET.get('size')

        # If a size is provided but that variant is not active (for non-admin) or doesn't exist, find a fallback
        if selected_size and selected_size not in stock_by_size:
            # Try fallback variant selection
            fallback_variant = None
            # First try one with stock > 0
            for v in variants_qs:
                if v.stock > 0:
                    fallback_variant = v
                    break
            # If no variant with stock, pick the first active variant anyway
            if not fallback_variant and variants_qs:
                fallback_variant = variants_qs.first()
            # If still no fallback_variant, product/variants no longer available
            if not fallback_variant:
                messages.error(request, "This product is no longer available.")
                raise Http404
            return redirect(f"{request.path}?size={fallback_variant.size}")

        # If no size specified, pick a default
        if 'size' not in request.GET:
            default_variant = None
            # If possible, pick one with stock
            for v in variants_qs:
                if v.stock > 0:
                    default_variant = v
                    break
            # If no stock variant found, pick the first active variant if any
            if not default_variant and variants_qs:
                default_variant = variants_qs.first()
            # If no variants at all (should be covered above), 404
            if not default_variant:
                messages.error(request, "This product is no longer available.")
                raise Http404
            return redirect(f"{request.path}?size={default_variant.size}")

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Handle new review submissions
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
            return redirect('product_detail', slug=self.object.slug)
        else:
            # If form is invalid, re-render the page with errors
            return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):    
        context = super().get_context_data(**kwargs)
        product = self.object

        is_admin = self.request.user.is_authenticated and (self.request.user.is_superuser or self.request.user.is_staff)
        
        # Filter variants based on admin status
        variants = product.variants.all().order_by('price') if is_admin else product.variants.filter(active=True).order_by('price')  # Order by price

        sizes = [variant.size for variant in variants]
        stock_by_size = {variant.size: variant for variant in variants}

        selected_size = self.request.GET.get('size')
        if selected_size and selected_size in stock_by_size:
            default_size = selected_size
        else:
            # If requested size not in active variants or no size selected
            # We already handled fallback logic in get(), so just trust here
            if sizes:
                default_size = sizes[0]
            else:
                default_size = None

        default_variant = stock_by_size.get(default_size)
        default_stock_status = "In Stock" if default_variant and default_variant.stock > 0 else "Out of Stock"
        default_price = default_variant.price if default_variant else None
        default_variant_id = default_variant.id
        size_active = default_variant.active

        product_form = ProductEditForm(instance=product) if is_admin else None
        variant_form = ProductVariantForm(instance=default_variant) if is_admin and default_variant else None

        # Get a count of all reviews grouped by rating
        rating_summary = product.reviews.values('rating').annotate(count=Count('rating')).order_by('rating')
        total_reviews = product.reviews.count()

        # Initialize a dictionary with all rating levels (0-5) set to 0
        rating_summary_dict = {i: 0 for i in range(6)}

        # Update the dictionary with actual counts from the query
        for entry in rating_summary:
            rating = entry['rating']
            count = entry['count']
            if rating in rating_summary_dict:
                rating_summary_dict[rating] = count

        # Filter reviews based on user role
        if is_admin:
            # Admin: Show all silenced comments but exclude non-commented ones
            visible_reviews = product.reviews.filter(~Q(comment="")).order_by('-created_at')
        else:
            # Non-admin: Exclude silenced and non-commented reviews
            visible_reviews = product.reviews.filter(silenced=False).exclude(comment="").order_by('-created_at')

        review_form = ProductReviewForm()
        category_items = [
            {"slug": category.slug, "name": category.name}
            for category in Category.objects.all()
        ]
        
        context.update({
            'product': product,
            'variants': variants,
            'sizes': sizes,
            'stock_by_size': stock_by_size,
            'default_size': default_size,
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
    model = Product
    fields = ['name', 'description', 'category', 'active']
    template_name = 'product/product_detail.html'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def get_success_url(self):
        return self.object.get_absolute_url()


class ProductDeactivateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def post(self, request, pk):
        if not request.user.is_superuser:
            return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)
        try:
            product = Product.objects.get(pk=pk)
            product.active = not product.active  # Toggle the active state
            product.save()
            return JsonResponse({"success": True, "active": product.active})
        except Product.DoesNotExist:
            return JsonResponse({"success": False, "error": "Product not found"}, status=404)


class VariantDeactivateView(View):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff
    
    def post(self, request, pk):
        if not request.user.is_superuser:
            return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)
        try:
            variant = ProductVariant.objects.get(pk=pk)
            variant.active = not variant.active  # Toggle the active state
            variant.save()
            return JsonResponse({"success": True, "active": variant.active})
        except ProductVariant.DoesNotExist:
            return JsonResponse({"success": False, "error": "Variant not found"}, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class SaveSelector(View):
    def post(self, request, selector_type):
        data = json.loads(request.body.decode('utf-8'))
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
            # Create a new category
            new_category = Category.objects.create(name=name)
            return JsonResponse({
                "success": True,
                "name": new_category.name,
                "slug": new_category.slug
            })

        elif action == "edit" and current_value:
            # Update existing category
            try:
                category = Category.objects.get(name=current_value)
                category.name = name
                category.save()
                return JsonResponse({
                    "success": True,
                    "name": category.name,
                    "slug": category.slug
                })
            except Category.DoesNotExist:
                return JsonResponse({"success": False, "error": "Category not found."}, status=404)

        return JsonResponse({"success": False, "error": "Invalid action or missing data."}, status=400)

    def handle_size(self, action, name, current_value, product_id):
        if not product_id:
            return JsonResponse({"success": False, "error": "Missing product_id."}, status=400)
        
        product = get_object_or_404(Product, pk=product_id)

        if action == "add":
            # Add a new variant for the product
            # Default values are just placeholders; adjust as needed.
            variant = ProductVariant.objects.create(
                product=product,
                size=name,
                price=0,
                stock=0
            )
            return JsonResponse({
                "success": True,
                "name": variant.size,
                "slug": variant.size
            })

        elif action == "edit" and current_value:
            # Update existing variant
            try:
                variant = ProductVariant.objects.get(product=product, size=current_value)
                variant.size = name
                variant.save()
                return JsonResponse({
                    "success": True,
                    "name": variant.size,
                    "slug": variant.size
                })
            except ProductVariant.DoesNotExist:
                return JsonResponse({"success": False, "error": "Variant not found."}, status=404)

        return JsonResponse({"success": False, "error": "Invalid action or missing data."}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class ReviewSilenceToggler(View):
    def post(self, request, review_id):
        if not request.user.is_superuser:
            return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)

        try:
            review = ProductReview.objects.get(id=review_id)
            review.silenced = not review.silenced
            review.save()
            return JsonResponse({"success": True, "silenced": review.silenced})
        except ProductReview.DoesNotExist:
            return JsonResponse({"success": False, "error": "Review not found"}, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class ProductSaveView(View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        variant_id = request.POST.get('variant_id')

        try:
            # Update Product
            product = Product.objects.get(id=product_id)
            product_data = json.loads(request.POST.get('product', '{}'))

            category_name = product_data.get('category')
            category = Category.objects.filter(name=category_name).first()
            if not category:
                return JsonResponse({"success": False, "error": f"Category '{category_name}' not found."}, status=400)

            product_form = ProductEditForm(
                {**product_data, "category": category.id}, instance=product
            )
            if product_form.is_valid():
                product_form.save()
            else:
                return JsonResponse({"success": False, "errors": product_form.errors}, status=400)

            # Handle Image Upload
            if 'image' in request.FILES:
                image_file = request.FILES['image']

                # Extract file extension
                file_extension = os.path.splitext(image_file.name)[1]  # E.g., ".jpg"

                # Delete the existing image from Cloudinary if it exists
                if product.image_path:
                    public_id = product.image_path.public_id
                    destroy(public_id)

                # Generate a new file name based on the product slug
                new_file_name = f"products/{product.slug}"  # Folder structure with slug as name

                # Upload the new image to Cloudinary with the correct public_id
                upload_result = upload(
                    image_file,
                    public_id=new_file_name,  # Full path: "products/ethiopian_coffee_bean"
                    overwrite=True,           # Ensures the old file is replaced
                    resource_type="image"     # Explicitly set resource type
                )

                # Save the public_id in the database
                product.image_path = upload_result['public_id']

                product.save()

            # Update Product Variant
            variant = ProductVariant.objects.get(id=variant_id)
            variant_form = ProductVariantForm(json.loads(request.POST.get('variant', '{}')), instance=variant)
            if variant_form.is_valid():
                variant_form.save()
            else:
                return JsonResponse({"success": False, "errors": variant_form.errors}, status=400)

            return JsonResponse({"success": True, "redirect_url": product.get_absolute_url()})
        except Product.DoesNotExist:
            return JsonResponse({"success": False, "error": "Product not found."}, status=404)
        except ProductVariant.DoesNotExist:
            return JsonResponse({"success": False, "error": "Variant not found."}, status=404)
