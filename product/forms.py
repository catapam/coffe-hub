from django import forms
from .models import Product, ProductVariant

class ProductEditForm(forms.ModelForm):
    """
    Form for editing product details. Includes fields for name, description, image, category, and rating.
    """
    class Meta:
        model = Product
        fields = ['name', 'description', 'image_path', 'rating', 'category']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter product description'
            }),
            'image_path': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 5,
                'step': 0.1
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with model values as the default.
        """
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        if instance:
            self.fields['name'].initial = instance.name
            self.fields['description'].initial = instance.description
            self.fields['image_path'].initial = instance.image_path
            self.fields['rating'].initial = instance.rating
            self.fields['category'].initial = instance.category


class ProductVariantForm(forms.ModelForm):
    """
    Form for editing product variants. Includes fields for size, price, and stock.
    """
    class Meta:
        model = ProductVariant
        fields = ['size', 'price', 'stock']
        widgets = {
            'size': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter size'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter price',
                'step': 0.01
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter stock quantity',
                'min': 0
            }),
        }

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with model values as the default.
        """
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        if instance:
            self.fields['size'].initial = instance.size
            self.fields['price'].initial = instance.price
            self.fields['stock'].initial = instance.stock