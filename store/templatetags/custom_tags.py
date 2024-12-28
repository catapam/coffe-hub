# Django imports
from django import template

register = template.Library()


@register.simple_tag
def update_query_params(request, **kwargs):
    '''
    Update query parameters in the current request.

    Args:
        request: The current HTTP request.
        **kwargs: Key-value pairs to update the query parameters.

    Returns:
        str: A URL-encoded query string with the updated parameters.

    Usage:
        {% update_query_params request sort_by='price_desc' %}
    '''
    params = request.GET.copy()
    for key, value in kwargs.items():
        params[key] = value
    return f'?{params.urlencode()}'
