from django import template

from apps.orders.status_display import STATUS_BADGE_CLASS, STATUS_LABELS

register = template.Library()


@register.inclusion_tag("orders/includes/_status_badge.html")
def order_status_badge(status: str):
    return {
        "label": STATUS_LABELS.get(status, status),
        "badge_class": STATUS_BADGE_CLASS.get(status, "text-bg-secondary"),
    }
