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
