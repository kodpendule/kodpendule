"""
Shared Django settings for Kod Pendule webshop.

Environment-specific overrides: config.settings.local | config.settings.production
Full wiring (database, middleware, static, parler): Step 3.
"""

from pathlib import Path

# Build paths inside the project: BASE_DIR / 'templates', etc.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# --- Apps (installed in Step 3) -----------------------------------------------

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "parler",
    "django_extensions",
    # "django_ratelimit",  # Step 14
]

LOCAL_APPS = [
    "apps.core",
    "apps.accounts",
    "apps.categories",
    "apps.products",
    "apps.cart",
    "apps.checkout",
    "apps.orders",
    "apps.shipping",
    "apps.dashboard",
    "apps.newsletter",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# --- Defaults (completed in Step 3) -------------------------------------------

SECRET_KEY = "django-insecure-placeholder-change-in-env"
DEBUG = False
ALLOWED_HOSTS: list[str] = []

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"

LANGUAGE_CODE = "sr"
LANGUAGES = [
    ("sr", "Srpski"),
    ("en", "English"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Europe/Belgrade"
USE_I18N = True
USE_TZ = True

# Parler (Step 9)
PARLER_LANGUAGES = {
    None: (
        {"code": "sr"},
        {"code": "en"},
    ),
    "default": {
        "fallbacks": ["sr"],
        "hide_untranslated": False,
    },
}

# Currency display (Serbia)
SHOP_CURRENCY = "RSD"
SHOP_CURRENCY_SYMBOL = "din"
