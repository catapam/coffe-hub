from django.views.generic import TemplateView

# Class-based view for the Home page (Index)
class Index(TemplateView):
    # Specify the template to use for the home page
    template_name = 'store/index.html'