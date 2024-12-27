# Django imports
from django import forms
from django.contrib.auth.models import User

# Internal imports
from .models import UserProfile


class UpdateUsernameForm(forms.ModelForm):
    """
    Form for updating the username of the currently logged-in user.
    This form is tied to the built-in User model.
    """
    class Meta:
        model = User
        fields = ['username']

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with custom attributes for the username field.
        """
        super(UpdateUsernameForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})

    def clean_username(self):
        """
        Validate that the new username is not already taken by another user.

        Returns:
            str: The cleaned username if it is valid.

        Raises:
            forms.ValidationError: If the username is already in use by
                                   another user.
        """
        username = self.cleaned_data.get('username')

        # Check if the new username is already taken by another user
        if User.objects.filter(
            username=username
        ).exclude(
            pk=self.instance.pk
        ).exists():
            raise forms.ValidationError(
                "This username is already taken. Please choose another one."
            )

        return username


class UserProfileForm(forms.ModelForm):
    """
    Form for managing the UserProfile model, excluding the associated user.
    """
    class Meta:
        model = UserProfile
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated labels,
        and set autofocus on the first field.
        """
        super().__init__(*args, **kwargs)
        placeholders = {
            'default_full_name': 'Full Name',
            'default_phone_number': 'Phone Number',
            'default_postcode': 'Postal Code',
            'default_town_or_city': 'Town or City',
            'default_street_address1': 'Street Address 1',
            'default_street_address2': 'Street Address 2',
            'default_county': 'County, State or Locality',
        }

        self.fields['default_full_name'].widget.attrs['autofocus'] = True
        for field in self.fields:
            if field != 'default_country':
                if self.fields[field].required:
                    placeholder = f'{placeholders[field]} *'
                else:
                    placeholder = placeholders[field]
                self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].label = False
