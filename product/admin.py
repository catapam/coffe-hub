from django.contrib import admin
from .models import Product, ProductVariant, Category, ProductReview
from django.utils.html import format_html


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('size', 'active', 'price', 'stock') 


class ProductReviewInline(admin.TabularInline):
    model = ProductReview
    extra = 0
    fields = ('user', 'rating', 'comment', 'silenced', 'created_at')
    readonly_fields = ('created_at',)
    show_change_link = True
    can_delete = False

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Exclude slug field from the list display
    list_display = ('name', 'category', 'active', 'rating', 'created_at', 'updated_at', 'image_preview')  # Add image preview to the list
    list_filter = ('category', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    inlines = [ProductVariantInline, ProductReviewInline]

    # Use `fields` to explicitly include the slug in the form view
    fields = ('name', 'slug', 'category', 'description', 'rating', 'image_path', 'image_preview', 'active', 'created_at', 'updated_at')
    readonly_fields = ('slug', 'created_at', 'updated_at', 'image_preview')  # Make non-editable fields read-only

    def image_preview(self, obj):
        """
        Returns an HTML img tag for the product's image.
        If no image is available, it shows a placeholder.
        """
        if obj.image_path:
            # Generate the Cloudinary image URL
            return format_html('<img src="{}" style="max-height: 150px;" />', obj.image())
        # Placeholder image
        return format_html('<img src="/static/images/product-holder.webp" style="max-height: 150px;" />')

    image_preview.short_description = "Image Preview"  # Set the column header name

    def save_model(self, request, obj, form, change):
        # Automatically set the slug using the model's save method
        obj.save()


class ProductInline(admin.TabularInline):
    model = Product
    extra = 0
    fields = ('name', 'rating', 'active', 'created_at')
    readonly_fields = ('created_at',)
    show_change_link = True
    can_delete = False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    exclude = ('slug',)  # Exclude slug field from the admin form
    list_display = ('name', 'slug', 'created_at')
    inlines = [ProductInline] 

    def save_model(self, request, obj, form, change):
        # Automatically set the slug using the model's save method
        obj.save()


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'silenced', 'comment', 'created_at')
    list_filter = ('product', 'rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')
    ordering = ('-created_at',)

    def has_change_permission(self, request, obj=None):
        """
        Allow edits only if the user is a superuser.
        """
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        """
        Allow deletes only if the user is a superuser.
        """
        return request.user.is_superuser
