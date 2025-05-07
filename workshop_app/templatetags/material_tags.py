from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary by key
    """
    return dictionary.get(key)

@register.filter
def div(value, arg):
    """
    Divide the value by the argument
    """
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return ''

@register.filter
def mul(value, arg):
    """
    Multiply the value by the argument
    """
    try:
        return float(value) * float(arg)
    except ValueError:
        return ''
