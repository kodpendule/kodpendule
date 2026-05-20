"""Shared helpers for storefront views and selectors."""

from django.conf import settings
from django.http import HttpRequest
from django.utils.translation import get_language


def get_shop_language(request: HttpRequest | None = None) -> str:
    """Active UI language code for Parler queries (sr or en)."""
    lang = None
    if request is not None:
        lang = getattr(request, "LANGUAGE_CODE", None)
    if not lang:
        lang = get_language()
    if not lang:
        lang = settings.PARLER_DEFAULT_LANGUAGE_CODE
    lang = lang.split("-")[0]
    if lang in dict(settings.LANGUAGES):
        return lang
    return settings.PARLER_DEFAULT_LANGUAGE_CODE
