# Django imports
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib import messages

# Internal imports
from product.views import ProductListView
from .forms import ContactForm


class HomeView(ProductListView):
    '''
    Extends ProductListView to reuse its get_context_data for the home page.
    '''
    template_name = 'store/index.html'

    def get_context_data(self, **kwargs):
        '''
        Use the context from ProductListView and add extra data for the
        home page.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            dict: Updated context with additional data for the home page.
        '''
        context = super().get_context_data(**kwargs)
        context['extra_data'] = 'Additional data for Catalog view'
        return context


class CustomPrivacyPolicyView(TemplateView):
    '''
    Render the privacy policy page.

    Uses the 'privacy-policy.html' template.
    '''
    template_name = 'store/privacy-policy.html'

    def get(self, request, *args, **kwargs):
        '''
        Handle GET requests to return the privacy policy page.

        Args:
            request: The current HTTP request.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            HttpResponse: Response object with a 200 status code.
        '''
        response = super().get(request, *args, **kwargs)
        response.status_code = 200
        return response


class AboutView(TemplateView):
    '''
    Render the about page with SEO metadata.

    Uses the 'about.html' template.
    '''
    template_name = 'store/about.html'

    def get_context_data(self, **kwargs):
        '''
        Add meta tags for SEO to the context.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            dict: Updated context with meta tags.
        '''
        context = super().get_context_data(**kwargs)
        context['meta_description'] = (
            'Learn about Coffee Hub, your trusted platform for premium '
            'coffee, brewing equipment, and accessories. Discover our '
            'mission, values, and commitment to quality.'
        )
        context['meta_keywords'] = (
            'about Coffee Hub, coffee shop, premium coffee, brewing '
            'equipment, coffee accessories'
        )
        return context

    def get(self, request, *args, **kwargs):
        '''
        Handle GET requests to return the about page.

        Args:
            request: The current HTTP request.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            HttpResponse: Response object with a 200 status code.
        '''
        response = super().get(request, *args, **kwargs)
        response.status_code = 200
        return response


class HelpView(TemplateView):
    '''
    Render the Help page with FAQ items and a contact form.

    Uses the 'help.html' template.
    '''
    template_name = 'store/help.html'

    def get_context_data(self, **kwargs):
        '''
        Add FAQ items, contact form, and SEO metadata to the context.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            dict: Updated context with FAQ items and contact form.
        '''
        context = super().get_context_data(**kwargs)
        context['base_template'] = (
            'accounts/account.html'
            if self.request.user.is_authenticated else 'base.html'
        )
        context['faq_items'] = [
            {
                'question': 'What is Coffee Hub?',
                'answer': (
                    'Coffee Hub is your one-stop platform for premium coffee, '
                    'brewing equipment, and accessories.'
                )
            },
            {
                'question': 'How do I create an account?',
                'answer': (
                    'Click on the Sign Up button at the top right of the page '
                    'and fill in your details.'
                )
            },
            {
                'question': 'How can I track my order?',
                'answer': (
                    'Log into your account and navigate to the My Orders '
                    'section for tracking details.'
                )
            },
            {
                'question': 'What payment methods do you accept?',
                'answer': (
                    'We accept Visa, MasterCard, American Express, and PayPal.'
                )
            },
            {
                'question': 'Can I return an item?',
                'answer': (
                    'Yes, you can return unused items within 30 days of '
                    'purchase. Refer to our return policy for details.'
                )
            },
        ]
        form = kwargs.get('form') or ContactForm(user=self.request.user)
        context['form'] = form
        context['meta_description'] = (
            'Find answers to common questions and contact us at Coffee Hub. '
            'Explore our FAQ section or submit your queries using our '
            'contact form.'
        )
        context['meta_keywords'] = (
            'help Coffee Hub, FAQ Coffee Hub, contact Coffee Hub, customer '
            'support, coffee shop support'
        )
        return context

    def post(self, request, *args, **kwargs):
        '''
        Handle POST requests to process the contact form.

        Args:
            request: The current HTTP request.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            HttpResponse: Redirect response to the Help page or rendered
            response with errors.
        '''
        form = ContactForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Your request has been submitted, we will reach back to you '
                'as soon as possible.'
            )
            return redirect('help')
        return self.render_to_response(self.get_context_data(form=form))
