# Django imports
from django import forms

# Internal imports
from .models import Product, ProductVariant, ProductReview


class ProductEditForm(forms.ModelForm):
    '''
    Form for editing product details.

    Includes fields for name, description, image, category, and activity
    status.
    '''
    class Meta:
        model = Product

        fields = [
            'name',
            'description',
            'image_path',
            'category',
            'active'
        ]

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
                'accept': 'image/*',
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def __init__(self, *args, **kwargs):
        '''
        Initialize the form with model values as the default.
        '''
        super().__init__(*args, **kwargs)


class ProductVariantForm(forms.ModelForm):
    '''
    Form for editing product variants.

    Includes fields for size, price, and stock.
    '''
    class Meta:
        model = ProductVariant

        fields = [
            'size',
            'price',
            'stock'
        ]

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
        '''
        Initialize the form with model values as the default.

        If an instance is provided, populate the initial values for
        size, price, and stock.
        '''
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        if instance:
            self.fields['size'].initial = instance.size
            self.fields['price'].initial = instance.price
            self.fields['stock'].initial = instance.stock


class ProductReviewForm(forms.ModelForm):
    '''
    Form for submitting product reviews.

    Includes fields for rating and a short comment.
    '''
    class Meta:
        model = ProductReview

        fields = [
            'rating',
            'comment'
        ]

        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': 0,
                'max': 5,
                'step': 1,
                'required': True,
            }),
            'comment': forms.Textarea(attrs={
                'maxlength': 100,
                'rows': 2,
                'placeholder': 'Write a short comment...'
            }),
        }

    def __init__(self, *args, **kwargs):
        '''
        Initialize the form with a default rating value of 0 if the
        form is not bound.
        '''
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.fields['rating'].initial = 0
