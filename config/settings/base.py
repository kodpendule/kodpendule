"""
Shared Django settings for Kod Pendule webshop.

Do not put secrets here. Use config.settings.local or config.settings.production.

Database: local = SQLite, production = PostgreSQL. Use portable ORM only
(no postgres-only fields, indexes, or raw SQL).
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# --- Apps ---------------------------------------------------------------------

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
    # Tombstone app: migrations only (newsletter feature removed).
    "apps.newsletter",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# --- Core ---------------------------------------------------------------------

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    # After LocaleMiddleware: default storefront to sr (ignore Accept-Language until /jezik/).
    "apps.core.middleware.StorefrontDefaultSerbianMiddleware",
    "apps.core.middleware.AdminSerbianLocaleMiddleware",
    "apps.core.middleware.StorefrontLocalizedUrlMiddleware",
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
                "apps.core.context_processors.shop_globals",
            ],
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# --- i18n ---------------------------------------------------------------------
# Default project language (admin + fallback). Storefront uses sr for new visitors;
# English only after the user picks it via /jezik/ (django_language cookie).
# AdminSerbianLocaleMiddleware forces sr on /admin/*.

LANGUAGE_CODE = "sr"
LANGUAGES = [
    ("sr", "Srpski"),
    ("en", "Engleski"),
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

# --- Static & media (URLs; storage backends set per environment) --------------

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Cloudflare R2 (enabled in production/local via configure_r2)
USE_R2 = False

# --- Session & auth redirects (views wired in Step 4) -------------------------

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14  # 2 weeks
LOGIN_URL = "/prijava/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# --- DRF ----------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

# --- Shop ---------------------------------------------------------------------

SHOP_CURRENCY = "RSD"
SHOP_CURRENCY_SYMBOL = "din"
SHOP_PRODUCTS_PER_PAGE = 12
SHOP_ORDER_NOTIFICATION_EMAILS: list[str] = []
DEFAULT_FROM_EMAIL = "noreply@kodpendule.rs"

