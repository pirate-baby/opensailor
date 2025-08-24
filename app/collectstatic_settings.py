# Minimal Django settings for collectstatic only
# This file allows running collectstatic without database or full app setup

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Minimal required settings
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "collectstatic-only-key")
DEBUG = False
ALLOWED_HOSTS = ["*"]

# Minimal apps needed for collectstatic
INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "django_htmx",
    "storages",
]

# Static files configuration
STATIC_ROOT = "/staticfiles"
STATICFILES_DIRS = [
    "/workspace/static",  # This is where our built CSS/JS assets are mounted
]

# S3 storage configuration for production
AWS_S3_ENDPOINT_URL = os.environ.get("AWS_S3_ENDPOINT_URL")
AWS_S3_CLIENT_ENDPOINT_URL = os.environ.get("AWS_S3_CLIENT_ENDPOINT_URL")
STATIC_URL = "https://static.opensailor.org/static/"

s3_storage_options = {
    "bucket_name": os.environ.get("AWS_S3_STORAGE_BUCKET"),
    "region_name": os.environ.get("AWS_DEFAULT_REGION_NAME"),
    "endpoint_url": STATIC_URL,
    "location": "static",
    "querystring_auth": False,
    "url_protocol": "https:",
    "file_overwrite": True,
    "gzip": True,
    "verify": True,
    "object_parameters": {
        "CacheControl": "max-age=31536000, public",
    },
    "custom_domain": "static.opensailor.org",
}

STORAGES = {
    "staticfiles": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": s3_storage_options,
    },
}

# Dummy database (won't be used for collectstatic)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Disable database usage
USE_TZ = True