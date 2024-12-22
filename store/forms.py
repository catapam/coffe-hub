from allauth.account.models import EmailAddress
from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['subject', 'email', 'name', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'Enter the subject'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email address'}),
            'name': forms.TextInput(attrs={'placeholder': 'Enter your name'}),
            'message': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Enter your message'}),
        }
        labels = {
            'subject': 'Subject',
            'email': 'Email Address',
            'name': 'Your Name',
            'message': 'Message',
        }

    def __init__(self, *args, **kwargs):
        """
        Initialize the form and prefill the email field with the user's primary email.
        """
        user = kwargs.pop('user', None)  # Extract 'user' from kwargs
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            # Fetch the primary email address using Allauth's EmailAddress model
            primary_email = EmailAddress.objects.filter(user=user, primary=True).first()
            if primary_email:
                self.fields['email'].initial = primary_email.email
                self.fields['email'].widget.attrs.update({'value': primary_email.email})  # Set value for rendering
