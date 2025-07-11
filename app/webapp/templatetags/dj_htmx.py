from django.template.defaulttags import register
from django.templatetags.static import static as django_static
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.conf import settings


@register.simple_tag
def htmx_script(minified=True):
    """
    Use Django's built-in static file handling to properly respect CDN configuration.
    """
    path = f"django_htmx/htmx{'.min' if minified else ''}.js"
    return (
        format_html(
            '<script src="{}" defer></script>\n',
            django_static(path),
        )
        + django_htmx_script()
    )


def django_htmx_script():
    if settings.DEBUG:
        return mark_safe("")
    return format_html(
        '<script src="{}" defer></script>',
        django_static("django_htmx/htmx.js"),
    )
