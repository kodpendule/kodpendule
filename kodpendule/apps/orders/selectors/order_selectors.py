"""Read-only order queries for storefront tracking and history."""

from django.db.models import QuerySet

from apps.orders.models import Order


def order_detail_qs() -> QuerySet[Order]:
    return (
        Order.objects.select_related(
            "user",
            "shipping_city",
            "shipping_method",
        ).prefetch_related("items", "items__product", "items__product__translations")
    )


def normalize_order_number(order_number: str) -> str:
    return (order_number or "").strip()


def normalize_tracking_email(email: str) -> str:
    return (email or "").strip().lower()


def get_order_for_guest_tracking(
    order_number: str,
    email: str,
) -> Order | None:
    """
    Match order only when both number and email are correct (case-insensitive).
    Single query; returns None for any mismatch (no distinction for callers).
    """
    number = normalize_order_number(order_number)
    normalized_email = normalize_tracking_email(email)
    if not number or not normalized_email:
        return None
    return (
        order_detail_qs()
        .filter(
            order_number__iexact=number,
            guest_email__iexact=normalized_email,
        )
        .first()
    )


def get_order_for_user(user, order_number: str) -> Order | None:
    if not user or not getattr(user, "is_authenticated", False) or not user.is_authenticated:
        return None
    number = normalize_order_number(order_number)
    if not number:
        return None
    return (
        order_detail_qs()
        .filter(user_id=user.pk, order_number__iexact=number)
        .first()
    )


def orders_for_user(user) -> QuerySet[Order]:
    if not user or not user.is_authenticated:
        return Order.objects.none()
    return (
        order_detail_qs()
        .filter(user_id=user.pk)
        .order_by("-created_at")
    )
