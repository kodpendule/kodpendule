"""SendGrid / SMTP email helpers for the shop."""

from __future__ import annotations

import logging
from email.utils import parseaddr
from typing import Iterable

from django.conf import settings
from django.core.mail import EmailMessage

from config.settings.sendgrid import SHOP_EMAIL_FROM_NAME

logger = logging.getLogger(__name__)


def is_email_configured() -> bool:
    return bool(getattr(settings, "SENDGRID_API_KEY", "") or getattr(settings, "EMAIL_HOST", ""))


def shop_sender_address() -> str:
    """Bare From address — must match a verified SendGrid sender identity."""
    raw = (
        getattr(settings, "SHOP_FROM_EMAIL", "")
        or getattr(settings, "SHOP_NOTIFICATION_EMAIL", "")
        or settings.DEFAULT_FROM_EMAIL
    )
    _, addr = parseaddr(str(raw).strip())
    return (addr or str(raw).strip()).lower()


def shop_from_email() -> tuple[str, str]:
    return (shop_sender_address(), SHOP_EMAIL_FROM_NAME)


def send_shop_email(
    *,
    subject: str,
    message: str,
    recipient_list: Iterable[str],
    reply_to: str | None = None,
    fail_silently: bool = True,
) -> bool:
    """
    Send a plain-text email. Returns True on success, False on skip/failure.

    Never raises when fail_silently=True (default).
    """
    recipients = [addr.strip() for addr in recipient_list if addr and addr.strip()]
    if not recipients:
        logger.warning("send_shop_email skipped: no recipients for subject %r", subject)
        return False

    if not is_email_configured():
        logger.warning(
            "send_shop_email skipped: SMTP not configured (subject=%r, recipients=%s)",
            subject,
            recipients,
        )
        return False

    from_email = shop_from_email()
    try:
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email,
            to=recipients,
            reply_to=[reply_to] if reply_to else None,
        )
        email.send(fail_silently=False)
        logger.info(
            "Email sent: subject=%r from=%s to=%s",
            subject,
            from_email[0],
            recipients,
        )
        return True
    except Exception:
        logger.exception(
            "Failed to send email: subject=%r from=%s to=%s",
            subject,
            from_email[0],
            recipients,
        )
        if not fail_silently:
            raise
        return False
