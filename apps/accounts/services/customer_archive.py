"""Upsert archived customer contacts (deduplicated by email)."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import CustomerContact

User = get_user_model()


def normalize_customer_email(email: str) -> str:
    return (email or "").strip().lower()


def archive_customer_from_registration(user: User) -> CustomerContact | None:
    email = normalize_customer_email(user.email or "")
    if not email:
        return None
    return _upsert_contact(
        email=email,
        first_name=user.first_name or "",
        last_name=user.last_name or "",
        phone=getattr(getattr(user, "profile", None), "phone", "") or "",
        user=user,
        mark_registered=True,
        increment_orders=False,
    )


def archive_customer_from_checkout(
    *,
    email: str,
    first_name: str,
    last_name: str,
    phone: str,
    user=None,
) -> CustomerContact | None:
    normalized = normalize_customer_email(email)
    if not normalized:
        return None
    linked_user = user if user and getattr(user, "is_authenticated", False) else None
    return _upsert_contact(
        email=normalized,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        user=linked_user,
        mark_registered=False,
        increment_orders=True,
    )


@transaction.atomic
def _upsert_contact(
    *,
    email: str,
    first_name: str,
    last_name: str,
    phone: str,
    user: User | None,
    mark_registered: bool,
    increment_orders: bool,
) -> CustomerContact:
    contact, created = CustomerContact.objects.select_for_update().get_or_create(
        email=email,
        defaults={
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "user": user,
            "registered_at": timezone.now() if mark_registered else None,
            "order_count": 1 if increment_orders else 0,
        },
    )

    if created:
        return contact

    contact.first_name = first_name or contact.first_name
    contact.last_name = last_name or contact.last_name
    contact.phone = phone or contact.phone

    if user and not contact.user_id:
        contact.user = user

    if mark_registered and contact.registered_at is None:
        contact.registered_at = timezone.now()

    if increment_orders:
        contact.order_count += 1

    update_fields = [
        "first_name",
        "last_name",
        "phone",
        "user",
        "registered_at",
        "order_count",
        "last_seen_at",
    ]
    contact.save(update_fields=update_fields)
    return contact
