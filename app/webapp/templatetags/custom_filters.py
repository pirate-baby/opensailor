from django import template
from webapp.models.sailboat import Sailboat

register = template.Library()

@register.filter
def split_first(value, arg):
    """Split the value by arg and return the first part"""
    return value.split(arg)[0]

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using a key"""
    return dictionary.get(key)

@register.filter
def in_list(value, list_value):
    """Check if a value is in a list"""
    if isinstance(list_value, list):
        return value in list_value
    return False

@register.filter
def get_attr(sailboat, attr_name):
    """Get a dynamic attribute value from a sailboat"""
    try:
        return getattr(sailboat, attr_name)
    except AttributeError:
        return None