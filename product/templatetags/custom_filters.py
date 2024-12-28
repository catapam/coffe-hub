# Django imports
from django import template

# Register a custom template library
register = template.Library()


@register.filter
def add(value, arg):
    '''
    Add two values together.

    Args:
        value (int or str): The first value.
        arg (int or str): The value to add to the first value.

    Returns:
        int: The sum of the two values if both can be converted to integers.
        Original value: If conversion fails, return the original value.
    '''
    try:
        return int(value) + int(arg)
    except (ValueError, TypeError):
        return value


@register.filter
def multiply(value, arg):
    '''
    Multiply two values together.

    Args:
        value (int or float): The first value.
        arg (int or float): The multiplier.

    Returns:
        int or float: The product of the two values.
    '''
    try:
        return value * arg
    except TypeError:
        return value
