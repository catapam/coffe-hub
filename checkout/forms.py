# Django imports
from django import forms
from django_countries.widgets import CountrySelectWidget

# Internal imports
from .models import Order


class CustomCountrySelectWidget(CountrySelectWidget):
    def render(self, name, value, attrs=None, renderer=None):
        # Render the default widget
        html = super().render(name, value, attrs, renderer)

        # Add an `alt` attribute to the flag image
        return html.replace(
            'class="country-select-flag"',
            'class="country-select-flag" alt="Flag"'
        )


class OrderForm(forms.ModelForm):
    '''
    Form for managing user order details.

    This form handles fields like the user's name, address, and contact
    information, while adding custom styling and placeholders.
    '''
    class Meta:
        model = Order
        fields = (
            'full_name',
            'email',
            'phone_number',
            'street_address1',
            'street_address2',
            'town_or_city',
            'postcode',
            'country',
            'county',
        )

        widgets = {
            'country': CustomCountrySelectWidget(attrs={
                'class': 'form-select',
                'required': True,
            }),
        }

    def __init__(self, *args, **kwargs):
        '''
        Customize the form's appearance by adding placeholders, removing
        labels, and setting autofocus on the first field.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        '''
        super().__init__(*args, **kwargs)
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'postcode': 'Postal Code',
            'town_or_city': 'Town or City',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'county': 'County, State or Locality',
        }

        # Set autofocus for the first field
        self.fields['full_name'].widget.attrs['autofocus'] = True

        for field in self.fields:
            # Skip adding placeholder for the country field
            if field == 'country':
                continue

            # Add placeholder and remove label
            if self.fields[field].required:
                placeholder = f'{placeholders[field]} *'
            else:
                placeholder = placeholders[field]
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].label = False
