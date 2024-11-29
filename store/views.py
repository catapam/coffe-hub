from product.views import ProductListView

class Catalog(ProductListView):
    """
    Extends ProductListView to reuse its get_context_data for the catalog page.
    """
    template_name = 'store/catalog.html'

    def get_context_data(self, **kwargs):
        # Use the context from ProductListView
        context = super().get_context_data(**kwargs)

        # Add any additional context specific to the Catalog view
        context['extra_data'] = "Additional data for Catalog view"

        return context
