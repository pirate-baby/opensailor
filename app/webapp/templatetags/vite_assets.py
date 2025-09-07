import json
import os
from django import template
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def vite_asset(asset_name):
    """
    Get the hashed filename from Vite's manifest for cache busting
    """
    manifest_path = "/static/libraries/.vite/manifest.json"

    # Fallback to original filename if manifest doesn't exist (development)
    if not os.path.exists(manifest_path):
        return static(f"libraries/{asset_name}")

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        # Get the entry file info
        entry = manifest.get("src/main.js", {})
        if "file" in entry:
            return static(f'libraries/{entry["file"]}')

    except (json.JSONDecodeError, FileNotFoundError, KeyError):
        pass

    # Fallback to original filename
    return static(f"libraries/{asset_name}")
