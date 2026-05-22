"""Order status labels and progress steps for templates."""

from django.utils.translation import gettext_lazy as _

from apps.orders.models import OrderStatus

STATUS_LABELS = {
    OrderStatus.PENDING: _("Pending"),
    OrderStatus.CONFIRMED: _("Confirmed"),
    OrderStatus.PROCESSING: _("Processing"),
    OrderStatus.SHIPPED: _("Shipped"),
    OrderStatus.DELIVERED: _("Delivered"),
    OrderStatus.CANCELLED: _("Cancelled"),
}

STATUS_BADGE_CLASS = {
    OrderStatus.PENDING: "text-bg-secondary",
    OrderStatus.CONFIRMED: "text-bg-info",
    OrderStatus.PROCESSING: "text-bg-primary",
    OrderStatus.SHIPPED: "text-bg-warning",
    OrderStatus.DELIVERED: "text-bg-success",
    OrderStatus.CANCELLED: "text-bg-danger",
}

PROGRESS_STATUSES = [
    OrderStatus.PENDING,
    OrderStatus.CONFIRMED,
    OrderStatus.PROCESSING,
    OrderStatus.SHIPPED,
    OrderStatus.DELIVERED,
]


def order_status_context(status: str) -> dict:
    """Context for status badge and optional progress timeline."""
    if status == OrderStatus.CANCELLED:
        return {
            "status_label": STATUS_LABELS[status],
            "status_badge_class": STATUS_BADGE_CLASS[status],
            "show_progress": False,
            "progress_steps": [],
            "current_step_index": -1,
        }
    steps = [
        {"code": code, "label": STATUS_LABELS[code]}
        for code in PROGRESS_STATUSES
    ]
    try:
        current_index = PROGRESS_STATUSES.index(status)
    except ValueError:
        current_index = 0
    return {
        "status_label": STATUS_LABELS.get(status, status),
        "status_badge_class": STATUS_BADGE_CLASS.get(status, "text-bg-secondary"),
        "show_progress": True,
        "progress_steps": steps,
        "current_step_index": current_index,
    }
