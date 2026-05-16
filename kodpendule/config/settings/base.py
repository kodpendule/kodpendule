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

# --- Defaults -----------------------------------------------------------------

SECRET_KEY = "django-insecure-placeholder-change-in-env"
DEBUG = False
ALLOWED_HOSTS: list[str] = []

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

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

PARLER_DEFAULT_LANGUAGE_CODE = "sr"

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
