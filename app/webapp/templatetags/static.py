from django.template.defaulttags import register
from django.conf import settings


@register.simple_tag
def static(path):
    """
    For some reason django-storages breaks this tag if the client and server s3 paths are different.
    """
    return settings.STATIC_URL + path