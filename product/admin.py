from django.contrib import admin
from .models import Product, ProductVariant, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'get_total_stock', 'rating', 'created_at')
    prepopulated_fields = {'slug': ('name',)}

    def get_total_stock(self, obj):
        """
        Calculate the total stock for a product by summing up the stock of its variants.
        """
        return sum(variant.stock for variant in obj.variants.all())
    get_total_stock.short_description = 'Total Stock'  # Rename column in admin panel

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'stock')
