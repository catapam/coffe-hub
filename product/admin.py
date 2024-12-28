# Django imports
from django.contrib import admin
from django.utils.html import format_html

# Internal imports
from .models import (
    Product,
    ProductVariant,
    Category,
    ProductReview
)


class ProductVariantInline(admin.TabularInline):
    '''
    Inline class for managing ProductVariant entries.

    Displays variant details like size, activity status, price, and stock.
    '''
    model = ProductVariant
    extra = 1
    fields = (
        'size',
        'active',
        'price',
        'stock'
    )


class ProductReviewInline(admin.TabularInline):
    '''
    Inline class for managing ProductReview entries.

    Displays user reviews with details like rating, comments, and timestamps.
    '''
    model = ProductReview
    extra = 0
    readonly_fields = ('created_at',)
    show_change_link = True
    can_delete = False
    fields = (
        'user',
        'rating',
        'comment',
        'silenced',
        'created_at'
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    '''
    Admin class for managing Product entries.

    Includes list display, search functionality, filters, and inlines
    for managing product variants and reviews.
    '''
    list_display = (
        'name',
        'category',
        'active',
        'rating',
        'created_at',
        'updated_at',
        'image_preview'
    )

    list_filter = (
        'category',
        'rating',
        'active',
        'created_at',
        'updated_at'
    )

    search_fields = (
        'name',
        'description'
    )

    inlines = [
        ProductVariantInline,
        ProductReviewInline
    ]

    fields = (
        'name',
        'slug',
        'category',
        'description',
        'rating',
        'image_path',
        'image_preview',
        'active',
        'created_at',
        'updated_at'
    )

    readonly_fields = (
        'slug',
        'created_at',
        'updated_at',
        'image_preview',
        'rating'
    )

    def image_preview(self, obj):
        '''
        Return an HTML img tag for the product's image.

        If no image is available, a placeholder image is returned.
        '''
        if obj.image_path:
            return format_html(
                '<img src="{}" style="max-height: 150px;" />',
                obj.image()
            )
        return format_html(
            '<img src="/static/images/product-holder.webp" '
            'style="max-height: 150px;" />'
        )

    image_preview.short_description = 'Image Preview'

    def save_model(self, request, obj, form, change):
        '''
        Automatically set the slug using the model's save method.
        '''
        obj.save()


class ProductInline(admin.TabularInline):
    '''
    Inline class for managing Product entries within categories.

    Displays product details like name, rating, activity status, and
    timestamps.
    '''
    model = Product
    extra = 0
    readonly_fields = ('created_at',)
    show_change_link = True
    can_delete = False
    fields = (
        'name',
        'rating',
        'active',
        'created_at'
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    '''
    Admin class for managing Category entries.

    Provides list display, inline product management, and slug exclusion.
    '''
    exclude = ('slug',)

    list_display = (
        'name',
        'slug',
        'created_at'
    )

    inlines = [ProductInline]

    def save_model(self, request, obj, form, change):
        '''
        Automatically set the slug using the model's save method.
        '''
        obj.save()


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    '''
    Admin class for managing ProductReview entries.

    Includes list display, filters, search functionality, and
    permission restrictions for edits and deletions.
    '''
    list_display = (
        'product',
        'user',
        'rating',
        'silenced',
        'comment',
        'created_at'
    )

    list_filter = (
        'product',
        'rating',
        'created_at'
    )

    search_fields = (
        'product__name',
        'user__username',
        'comment'
    )

    ordering = ('-created_at',)

    def has_change_permission(self, request, obj=None):
        '''
        Allow edits only if the user is a superuser.
        '''
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        '''
        Allow deletes only if the user is a superuser.
        '''
        return request.user.is_superuser
