from django.views.generic import TemplateView
from django.shortcuts import render

class Catalog(TemplateView):
    template_name = 'store/catalog.html'

    def get_context_data(self, **kwargs):
        # Get the default context data from the parent class
        context = super().get_context_data(**kwargs)
        # Add the range of products to the context
        context['products'] = range(9)
        context['total_review'] = range(5)
        context['review'] = 4
        return context