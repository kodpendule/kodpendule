"""Shared helpers for storefront views and selectors."""

from django.conf import settings
from django.http import HttpRequest
from django.utils.translation import get_language


def activate_parler_language(obj, preferred_language: str | None = None) -> None:
    """
    Set Parler's active translation to one that has a name (and slug if possible).
    Avoids empty fields when the UI language has no translation yet.
    """
    from apps.core.slugs import localized_slug

    lang = preferred_language or get_shop_language()
    slug = localized_slug(obj)
    if slug and hasattr(obj, "translations"):
        for trans in obj.translations.all():
            if trans.slug == slug:
                obj.set_current_language(trans.language_code)
                return
    for try_lang in (lang, settings.PARLER_DEFAULT_LANGUAGE_CODE):
        obj.set_current_language(try_lang)
        if obj.safe_translation_getter("name", language_code=try_lang):
            return
    obj.set_current_language(lang)


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
