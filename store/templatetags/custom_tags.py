from django import template

register = template.Library()

@register.simple_tag
def update_query_params(request, **kwargs):
    """
    Updates query parameters in the current request.
    Usage: {% update_query_params request sort_by='price_desc' %}
    """
    params = request.GET.copy()
    for key, value in kwargs.items():
        params[key] = value
    return f"?{params.urlencode()}"
