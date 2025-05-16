from django.template.defaulttags import register
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.conf import settings


@register.simple_tag
def htmx_script(minified=True):
    """
    For some reason django-storages breaks this tag if the client and server s3 paths are different.
    """
    path = f"django_htmx/htmx{'.min' if minified else ''}.js"
    return (
        format_html(
            '<script src="{}" defer></script>\n',
            settings.STATIC_URL + path,
        )
        + django_htmx_script()
    )


def django_htmx_script():
    if settings.DEBUG:
        return mark_safe("")
    return format_html(
        '<script src="{}" defer></script>',
        settings.STATIC_URL + "django_htmx/htmx.js",
    )
