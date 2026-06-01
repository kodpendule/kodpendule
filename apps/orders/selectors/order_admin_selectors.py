from apps.orders.models import Order


def unread_order_count() -> int:
    return Order.objects.filter(is_new=True).count()
