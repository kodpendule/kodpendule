"""Resolve admin inboxes for transactional email."""

from __future__ import annotations

from django.conf import settings

from apps.core.contact_details import resolve_contact_details
from apps.core.models import FooterSettings


def shop_admin_recipients() -> list[str]:
    """Inboxes for staff alerts (orders, low stock, contact form)."""
    email = (getattr(settings, "SHOP_NOTIFICATION_EMAIL", "") or "").strip()
    if email:
        return [email]

    footer = FooterSettings.objects.filter(pk=1).first()
    contact = resolve_contact_details(footer)
    if contact.email:
        return [contact.email.strip()]
    return []
