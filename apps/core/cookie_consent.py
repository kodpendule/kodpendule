"""Storefront cookie consent levels (GDPR-friendly banner)."""

from __future__ import annotations

from urllib.parse import unquote

from django.conf import settings
from django.http import HttpRequest

CONSENT_LEVEL_ESSENTIAL = "essential"
CONSENT_LEVEL_ALL = "all"


def _cookie_name() -> str:
    return getattr(settings, "COOKIE_CONSENT_COOKIE_NAME", "kp_cookie_consent")


def _consent_version() -> str:
    return getattr(settings, "COOKIE_CONSENT_VERSION", "v1")


def parse_consent_cookie(raw: str | None) -> str | None:
    """
    Return consent level ('essential' | 'all') or None if missing/invalid.
    """
    if not raw:
        return None
    raw = unquote(raw.strip())
    parts = raw.split(":", 1)
    if len(parts) != 2:
        return None
    version, level = parts[0], parts[1]
    if version != _consent_version():
        return None
    if level in (CONSENT_LEVEL_ESSENTIAL, CONSENT_LEVEL_ALL):
        return level
    return None


def consent_from_request(request: HttpRequest) -> str | None:
    return parse_consent_cookie(request.COOKIES.get(_cookie_name()))


def consent_given(request: HttpRequest) -> bool:
    return consent_from_request(request) is not None
