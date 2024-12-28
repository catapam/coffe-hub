# Django imports
from django import forms

# Third-party imports
from allauth.account.models import EmailAddress

# Internal imports
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    '''
    Form for handling contact messages.

    This form includes fields for subject, email, name, and message, with
    customizable widgets and labels.
    '''
    class Meta:
        model = ContactMessage

        fields = [
            'subject',
            'email',
            'name',
            'message'
        ]

        widgets = {
            'subject': forms.TextInput(attrs={
                'placeholder': 'Enter the subject'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter your email address'
            }),
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter your name'
            }),
            'message': forms.Textarea(attrs={
                'rows': 5, 'placeholder': 'Enter your message'
            }),
        }
        labels = {
            'subject': 'Subject',
            'email': 'Email Address',
            'name': 'Your Name',
            'message': 'Message',
        }

    def __init__(self, *args, **kwargs):
        '''
        Initialize the form and prefill the email field with the user's
        primary email if available.

        Args:
            *args: Positional arguments for the form.
            **kwargs: Keyword arguments for the form.

        Keyword Args:
            user (User): The currently logged-in user.
        '''
        user = kwargs.pop('user', None)  # Extract 'user' from kwargs
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            primary_email = (
                EmailAddress.objects.filter(user=user, primary=True).first()
            )
            if primary_email:
                self.fields['email'].initial = primary_email.email
                self.fields['email'].widget.attrs.update({
                    'value': primary_email.email
                })  # Set value for rendering
