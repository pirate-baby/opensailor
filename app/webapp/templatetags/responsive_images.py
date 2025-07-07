from django import template

register = template.Library()

@register.inclusion_tag('webapp/components/responsive_image.html')
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
        'image': image,
        'alt_text': alt_text,
        'css_classes': css_classes,
        'lazy': lazy,
        'sizes': sizes
    }