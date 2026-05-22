"""Slug helpers for Parler models (language-aware URLs)."""

from django.conf import settings
from django.utils.text import slugify

from apps.core.utils import get_shop_language


def slug_from_name(name: str, *, max_length: int = 270) -> str:
    """Build a URL slug from a display name."""
    return slugify(name, allow_unicode=True)[:max_length]


def unique_slug_for_translation(translation, *, fallback: str = "") -> str:
    """Return a slug unique across all rows of the translation model."""
    Translation = translation.__class__
    name = (getattr(translation, "name", None) or "").strip()
    base = slug_from_name(name) or slug_from_name(fallback) or "item"
    candidate = base
    suffix = 2
    while (
        Translation.objects.filter(slug=candidate)
        .exclude(pk=translation.pk)
        .exists()
    ):
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate


def localized_slug(obj, language: str | None = None) -> str:
    """
    Slug for the active UI language, falling back to any other translation.
    Reads translation rows directly so partially translated products still work.
    """
    lang = language or get_shop_language()

    translations = []
    if hasattr(obj, "translations"):
        translations = list(obj.translations.all())

    for trans in translations:
        if trans.language_code == lang and getattr(trans, "slug", None):
            return trans.slug

    for trans in translations:
        if getattr(trans, "slug", None):
            return trans.slug

    slug = obj.safe_translation_getter("slug", language_code=lang)
    if slug:
        return slug
    return obj.safe_translation_getter("slug", any_language=True) or ""


def translation_languages_to_try(language: str | None = None) -> list[str]:
    """Order of language codes to use when resolving a slug."""
    lang = language or get_shop_language()
    codes = [lang]
    default = settings.PARLER_DEFAULT_LANGUAGE_CODE
    if default not in codes:
        codes.append(default)
    for code, _ in settings.LANGUAGES:
        if code not in codes:
            codes.append(code)
    return codes
