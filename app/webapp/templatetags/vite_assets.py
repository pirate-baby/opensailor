import json
import requests
from django import template
from django.templatetags.static import static
from django.core.cache import cache
from webapp.settings import IS_PRODUCTION
from webapp.logging import get_logger


logger = get_logger(__name__)
register = template.Library()


@register.simple_tag
def vite_asset(asset_name):
    """
    Get the hashed filename from Vite's manifest for cache busting
    """
    # Check cache first
    cache_key = f"vite_manifest_{asset_name}"
    if cached_result := cache.get(cache_key):
        logger.info(f"Cache hit for {cache_key}")
        return cached_result
    if IS_PRODUCTION:
        try:
            logger.info("Fetching Vite manifest for production asset")
            fullpath = "https://static.opensailor.org/static/libraries/.vite/manifest.json"
            manifest = requests.get(fullpath, timeout=2).json()
            entry = manifest.get("src/main.js", {})
            if "file" in entry:
                logger.info(f"Caching asset {entry['file']} for {cache_key}")
                result = static(f'libraries/{entry["file"]}')
                cache.set(cache_key, result, 3600 * 24 * 30)  # Cache for 30 days
                logger.info(f"Cached asset {entry['file']} for {cache_key}")
                logger.info(f"Returning production asset {result}")
                return result
        except (
            requests.RequestException,
            json.JSONDecodeError,
            KeyError,
            FileNotFoundError,
        ):
            logger.error("Error fetching or parsing Vite manifest, falling back to unversioned asset", exc_info=True)
            pass
    logger.info("Returning unversioned asset for development or fallback")
    return static(f"libraries/{asset_name}")
