from django.template.defaulttags import register
from django.templatetags.static import static as django_static


@register.simple_tag
def static(path):
    """
    Use Django's built-in static file handling to properly respect CDN configuration.
    """
    return django_static(path)
