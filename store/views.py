from product.views import ProductListView
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from .forms import ContactForm
from django.contrib import messages

class HomeView(ProductListView):
    """
    Extends ProductListView to reuse its get_context_data for the home page.
    """
    template_name = 'store/index.html'

    def get_context_data(self, **kwargs):
        # Use the context from ProductListView
        context = super().get_context_data(**kwargs)

        # Add any additional context specific to the Catalog view
        context['extra_data'] = "Additional data for Catalog view"

        return context

# Class-based view for handling Privacy policy page
class CustomPrivacyPolicyView(TemplateView):
    """
    This view renders provacy policy page.
    It uses the 'privacy-policy.html' template and returns an HTTP status code of 200.
    """
    template_name = 'store/privacy-policy.html'

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and returns the 200 status with the
        custom template.
        """
        response = super().get(request, *args, **kwargs)
        response.status_code = 200
        return response

# Class-based view for handling About page
class AboutView(TemplateView):
    """
    This view renders about page .
    It uses the 'about.html' template and returns an HTTP status code of 200.
    """
    template_name = 'store/about.html'

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and returns the 200 status with the
        custom template.
        """
        response = super().get(request, *args, **kwargs)
        response.status_code = 200
        return response

# Class-based view for handling About page
class HelpView(TemplateView):
    """
    This view renders the Help page with FAQ and a contact form.
    """
    template_name = 'store/help.html'

    def get_context_data(self, **kwargs):
        """
        Adds the FAQ items and contact form to the context.
        """
        context = super().get_context_data(**kwargs)

        # Dynamically set the base template
        context['base_template'] = 'accounts/account.html' if self.request.user.is_authenticated else 'base.html'

        # FAQ items
        context['faq_items'] = [
            {"question": "What is Coffee Hub?", "answer": "Coffee Hub is your one-stop platform for premium coffee, brewing equipment, and accessories."},
            {"question": "How do I create an account?", "answer": "Click on the 'Sign Up' button at the top right of the page and fill in your details."},
            {"question": "How can I track my order?", "answer": "Log into your account and navigate to the 'My Orders' section for tracking details."},
            {"question": "What payment methods do you accept?", "answer": "We accept Visa, MasterCard, American Express, and PayPal."},
            {"question": "Can I return an item?", "answer": "Yes, you can return unused items within 30 days of purchase. Refer to our return policy for details."},
        ]

        # Add the Crispy form to the context
        form = kwargs.get('form') or ContactForm(user=self.request.user)
        context['form'] = form

        return context
    
    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST, user=request.user)
        if form.is_valid():
            # Save the form data to the database
            form.save()
            messages.success(request, "Your request has been submitted, we will reach back to you as soon as possible.")
            return redirect('help')
        return self.render_to_response(self.get_context_data(form=form))
