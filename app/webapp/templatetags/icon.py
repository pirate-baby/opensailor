from django.template.defaulttags import register
from django.utils.html import format_html


@register.simple_tag
def icon(name):
    """Icons available at https://fonts.google.com/icons?icon.style=Outlined
    Make sure you add the icons you use to the script in base.html, or they won't show up.
    """
    return format_html(
        '<span class="material-symbols-outlined">{name}</span>',
        name=name,
    )
