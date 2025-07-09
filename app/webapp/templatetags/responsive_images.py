from django import template

register = template.Library()

# Common responsive image sizes patterns
CARD_SIZES = "(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
DETAIL_SIZES = "(max-width: 1024px) 100vw, 66vw"
THUMBNAIL_SIZES = "120px"


@register.inclusion_tag("webapp/components/responsive_image.html")
def responsive_image(image, alt_text="", css_classes="", lazy=True, sizes="100vw"):
    """
    Render a responsive image with lazy loading.

    Args:
        image: Media object with image file
        alt_text: Alternative text for accessibility
        css_classes: CSS classes to apply to the image
        lazy: Whether to enable lazy loading (default: True)
        sizes: Sizes attribute for responsive images (default: "100vw")
    """
    return {
        "image": image,
        "alt_text": alt_text,
        "css_classes": css_classes,
        "lazy": lazy,
        "sizes": sizes,
    }


@register.inclusion_tag("webapp/components/responsive_image.html")
def card_image(image, alt_text="", css_classes="", lazy=True):
    """Responsive image for card layouts (index pages)."""
    return responsive_image(image, alt_text, css_classes, lazy, CARD_SIZES)


@register.inclusion_tag("webapp/components/responsive_image.html")
def detail_image(image, alt_text="", css_classes="", lazy=True):
    """Responsive image for detail page main images."""
    return responsive_image(image, alt_text, css_classes, lazy, DETAIL_SIZES)


@register.inclusion_tag("webapp/components/responsive_image.html")
def thumbnail_image(image, alt_text="", css_classes="", lazy=True):
    """Responsive image for small thumbnails."""
    return responsive_image(image, alt_text, css_classes, lazy, THUMBNAIL_SIZES)
