from django import template
from django.utils.safestring import mark_safe
import re
import markdown

register = template.Library()


@register.filter
def split_first(value, arg):
    """Split the value by arg and return the first part"""
    return value.split(arg)[0]


@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key"""
    return dictionary.get(key)


@register.filter
def in_list(value, list_value):
    """Check if a value is in a list"""
    if isinstance(list_value, list):
        return value in list_value
    return False


@register.filter
def is_list(value):
    """Check if a value is a list type"""
    return isinstance(value, (list, tuple))


@register.filter
def get_attr(sailboat, attr_name):
    """Get attribute values from a sailboat's attributes"""
    attr = sailboat.attribute_values.get(attribute__snake_case_name=attr_name)
    return getattr(attr, 'values', None)


@register.filter(is_safe=True)
def format_boolean(value):
    """Format boolean values as checkboxes"""
    if value in (True, "true", "True", "yes", "Yes", "1", 1):
        return mark_safe(
            '<span class="inline-flex items-center justify-center w-5 h-5 border border-gray-400 rounded bg-accent text-white"><svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg></span>'
        )
    return mark_safe(
        '<span class="inline-block w-5 h-5 border border-gray-400 rounded"></span>'
    )


@register.filter
def is_boolean_attribute(attr_value):
    """Check if an attribute is a boolean type or has boolean values"""
    if not attr_value.values:
        return False

    boolean_values = ("true", "false", "yes", "no", "1", "0")
    return all(str(v).lower() in boolean_values for v in attr_value.values)


@register.filter(is_safe=True)
def markdown_no_headings(value):
    """Render markdown, but strip headings (lines starting with #)."""
    if not value:
        return ""
    # Remove markdown headings (lines starting with one or more #)
    no_headings = re.sub(r"^#+[ ].*$", "", value, flags=re.MULTILINE)
    html = markdown.markdown(no_headings)
    return mark_safe(html)
