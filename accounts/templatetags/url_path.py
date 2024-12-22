from django.urls import reverse
from django import template

register = template.Library()

@register.filter
def get_url_path(url_name):
    try:
        return reverse(url_name)
    except:
        return ""
