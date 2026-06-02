"""SendGrid SMTP — one API key env var; sensible defaults for everything else."""

from __future__ import annotations

from typing import Any

SENDGRID_SMTP_HOST = "smtp.sendgrid.net"
SENDGRID_SMTP_PORT = 587
SENDGRID_SMTP_USERNAME = "apikey"
SHOP_EMAIL_FROM_NAME = "Kod Pendule"


def _normalize_email(value: str, *, fallback: str) -> str:
    from email.utils import parseaddr

    raw = (value or fallback or "").strip()
    _, addr = parseaddr(raw)
    return (addr or raw or fallback).strip().lower()


def configure_sendgrid_email(settings_module: Any, config) -> None:
    """
    Enable email when SENDGRID_API_KEY is set.

    SHOP_FROM_EMAIL — must match a verified SendGrid Single Sender (default kodpendule@gmail.com).
    SHOP_NOTIFICATION_EMAIL — staff inbox for order/low-stock/contact alerts (same default).
    """
    default_inbox = getattr(
        settings_module,
        "SHOP_NOTIFICATION_EMAIL",
        "kodpendule@gmail.com",
    )
    notification_email = _normalize_email(
        config("SHOP_NOTIFICATION_EMAIL", default=default_inbox),
        fallback="kodpendule@gmail.com",
    )
    from_email = _normalize_email(
        config(
            "SHOP_FROM_EMAIL",
            default=getattr(settings_module, "SHOP_FROM_EMAIL", notification_email),
        ),
        fallback=notification_email,
    )

    settings_module.SHOP_NOTIFICATION_EMAIL = notification_email
    settings_module.SHOP_FROM_EMAIL = from_email

    api_key = (config("SENDGRID_API_KEY", default="") or "").strip()
    settings_module.SENDGRID_API_KEY = api_key

    if not api_key:
        return

    settings_module.EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    settings_module.EMAIL_HOST = SENDGRID_SMTP_HOST
    settings_module.EMAIL_PORT = SENDGRID_SMTP_PORT
    settings_module.EMAIL_HOST_USER = SENDGRID_SMTP_USERNAME
    settings_module.EMAIL_HOST_PASSWORD = api_key
    settings_module.EMAIL_USE_TLS = True
    settings_module.DEFAULT_FROM_EMAIL = from_email
    settings_module.SERVER_EMAIL = from_email
