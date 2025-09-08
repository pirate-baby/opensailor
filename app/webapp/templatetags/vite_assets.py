import json
import requests
from django import template
from django.templatetags.static import static
from django.core.cache import cache
from webapp.settings import IS_PRODUCTION

register = template.Library()


@register.simple_tag
def vite_asset(asset_name):
    """
    Get the hashed filename from Vite's manifest for cache busting
    """
    # Check cache first
    cache_key = f"vite_manifest_{asset_name}"
    if cached_result := cache.get(cache_key):
        return cached_result
    if IS_PRODUCTION:
        try:
            manifest = requests.get("/static/libraries/.vite/manifest.json", timeout=2).json()
            entry = manifest.get("src/main.js", {})
            if "file" in entry:
                result = static(f'libraries/{entry["file"]}')
                cache.set(cache_key, result, 3600 * 24 * 30)  # Cache for 30 days
                return result
        except (
            requests.RequestException,
            json.JSONDecodeError,
            KeyError,
            FileNotFoundError,
        ):
            pass
    return static(f"libraries/{asset_name}")
