"""Helpers for models with explicit Serbian / English text columns."""

from __future__ import annotations

from apps.core.utils import get_shop_language


def localized_field_value(
    instance: object,
    base: str,
    *,
    language_code: str | None = None,
) -> str:
    """
    Return ``{base}_sr`` or ``{base}_en`` for the active language, with fallback.
    """
    lang = language_code or get_shop_language()
    sr = (getattr(instance, f"{base}_sr", None) or "").strip()
    en = (getattr(instance, f"{base}_en", None) or "").strip()
    if lang == "en":
        return en or sr
    return sr or en
