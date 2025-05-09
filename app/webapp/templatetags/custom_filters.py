from django import template

register = template.Library()

@register.filter
def split_first(value, arg):
    """Split the value by arg and return the first part"""
    return value.split(arg)[0]