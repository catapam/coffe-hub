# Django imports
from django import forms
from django_countries.widgets import CountrySelectWidget
from django.utils.html import format_html

# Internal imports
from .models import Order


class CustomCountrySelectWidget(CountrySelectWidget):
    """
    Custom widget for rendering a country select field without the default
    `onchange` attribute and with enhanced accessibility.

    This widget modifies the default behavior of `CountrySelectWidget` by:
    1. Removing the `onchange` attribute to prevent automatic JavaScript-based
        actions.
    2. Adding an `aria-label` for accessibility purposes.
    3. Ensuring the flag image associated with the country has an `alt`
        attribute.
    """

    def build_attrs(self, base_attrs, extra_attrs=None):
        """
        Override the `build_attrs` method to remove the `onchange` attribute
        from the default widget's attributes.

        Args:
            base_attrs (dict): The base attributes of the widget.
            extra_attrs (dict, optional): Additional attributes for the widget.

        Returns:
            dict: The combined attributes for the widget without `onchange`.
        """
        # Combine base attributes and extra attributes
        attrs = super().build_attrs(base_attrs, extra_attrs)
        # Remove the `onchange` attribute to prevent unwanted behavior
        attrs.pop('onchange', None)
        return attrs

    def render(self, name, value, attrs=None, renderer=None):
        """
        Render the country select field with custom modifications.

        Args:
            name (str): The name of the field.
            value (str): The current value of the field.
            attrs (dict, optional): Additional attributes for the widget.
            renderer: The renderer for the widget (default is None).

        Returns:
            str: The HTML representation of the widget with custom
            modifications.
        """
        # Ensure `attrs` is initialized as a dictionary
        if attrs is None:
            attrs = {}
        # Add an accessible aria-label for the country selector
        attrs['aria-label'] = "Select your country."

        # Render the widget with the updated attributes
        html = super().render(name, value, attrs, renderer)

        # Add an `alt` attribute to the flag image for accessibility
        html = html.replace(
            'class="country-select-flag"',
            'class="country-select-flag" alt="Flag"'
        )

        # Return the final rendered HTML
        return html  # No script added


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
