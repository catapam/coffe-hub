# Django imports
from django.urls import reverse
from django import template

# Create a template library instance
register = template.Library()

@register.filter
def get_url_path(url_name):
    """
    Custom template filter to get the URL path for a given URL name.

    Args:
        url_name (str): The name of the URL pattern to resolve.

    Returns:
        str: The resolved URL path if the URL name exists, otherwise an
             empty string.
    """
    try:
        # Attempt to resolve the URL name to its corresponding path
        return reverse(url_name)
    except Exception:
        # Return an empty string if the URL cannot be resolved
        return ""