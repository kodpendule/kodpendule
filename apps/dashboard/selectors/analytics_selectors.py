"""ORM aggregations for the admin analytics dashboard."""

from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Any

from django.db.models import Avg, Count, F, Sum
from django.db.models.functions import Coalesce, TruncDate, TruncMonth
from django.utils import timezone

from apps.categories.models import Category
from apps.dashboard.filters import ReportPeriod
from apps.orders.models import Order, OrderItem, OrderStatus
from apps.products.models import Product

EXCLUDED_STATUSES = (OrderStatus.CANCELLED,)


def _local_today() -> date:
    return timezone.localdate()


def _datetime_bounds(period: ReportPeriod) -> tuple[datetime, datetime]:
    """Inclusive date range as timezone-aware datetimes for filtering."""
    tz = timezone.get_current_timezone()
    start_dt = timezone.make_aware(
        datetime.combine(period.start, time.min),
        tz,
    )
    end_dt = timezone.make_aware(
        datetime.combine(period.end, time.max),
        tz,
    )
    return start_dt, end_dt


def completed_orders_qs():
    """Orders that count toward revenue (not cancelled)."""
    return Order.objects.exclude(status__in=EXCLUDED_STATUSES)


def orders_in_period(period: ReportPeriod):
    start_dt, end_dt = _datetime_bounds(period)
    return completed_orders_qs().filter(created_at__gte=start_dt, created_at__lte=end_dt)


def period_order_metrics(period: ReportPeriod) -> dict[str, Any]:
    agg = orders_in_period(period).aggregate(
        order_count=Count("id"),
        revenue=Coalesce(Sum("total"), Decimal("0")),
        avg_order_value=Coalesce(Avg("total"), Decimal("0")),
    )
    return {
        "order_count": agg["order_count"] or 0,
        "revenue": agg["revenue"],
        "avg_order_value": agg["avg_order_value"],
    }


def revenue_on_date(day: date) -> Decimal:
    start_dt, end_dt = _datetime_bounds(ReportPeriod(day, day, "day"))
    result = completed_orders_qs().filter(
        created_at__gte=start_dt,
        created_at__lte=end_dt,
    ).aggregate(total=Coalesce(Sum("total"), Decimal("0")))
    return result["total"]


def revenue_for_calendar_month(year: int, month: int) -> Decimal:
    last_day = monthrange(year, month)[1]
    period = ReportPeriod(
        start=date(year, month, 1),
        end=date(year, month, last_day),
        preset="calendar_month",
    )
    return period_order_metrics(period)["revenue"]


def overview_snapshot() -> dict[str, Any]:
    today = _local_today()
    return {
        "today_revenue": revenue_on_date(today),
        "monthly_revenue": revenue_for_calendar_month(today.year, today.month),
    }


def status_pipeline_counts() -> dict[str, int]:
    """Current counts for key fulfillment statuses (all non-cancelled orders)."""
    rows = (
        completed_orders_qs()
        .filter(
            status__in=(
                OrderStatus.PENDING,
                OrderStatus.SHIPPED,
                OrderStatus.DELIVERED,
            )
        )
        .values("status")
        .annotate(count=Count("id"))
    )
    counts = {row["status"]: row["count"] for row in rows}
    return {
        "pending": counts.get(OrderStatus.PENDING, 0),
        "shipped": counts.get(OrderStatus.SHIPPED, 0),
        "delivered": counts.get(OrderStatus.DELIVERED, 0),
    }


def order_status_distribution(period: ReportPeriod) -> list[dict[str, Any]]:
    start_dt, end_dt = _datetime_bounds(period)
    rows = (
        Order.objects.filter(created_at__gte=start_dt, created_at__lte=end_dt)
        .values("status")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    return [{"status": row["status"], "count": row["count"]} for row in rows]


def sales_by_day(period: ReportPeriod) -> list[dict[str, Any]]:
    start_dt, end_dt = _datetime_bounds(period)
    rows = (
        completed_orders_qs()
        .filter(created_at__gte=start_dt, created_at__lte=end_dt)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(
            revenue=Coalesce(Sum("total"), Decimal("0")),
            orders=Count("id"),
        )
        .order_by("day")
    )
    return [
        {
            "day": row["day"],
            "revenue": row["revenue"],
            "orders": row["orders"],
        }
        for row in rows
        if row["day"] is not None
    ]


def sales_by_month(period: ReportPeriod) -> list[dict[str, Any]]:
    start_dt, end_dt = _datetime_bounds(period)
    rows = (
        completed_orders_qs()
        .filter(created_at__gte=start_dt, created_at__lte=end_dt)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(
            revenue=Coalesce(Sum("total"), Decimal("0")),
            orders=Count("id"),
        )
        .order_by("month")
    )
    return [
        {
            "month": row["month"],
            "revenue": row["revenue"],
            "orders": row["orders"],
        }
        for row in rows
        if row["month"] is not None
    ]


def _line_revenue_expression():
    return F("unit_price") * F("quantity")


def top_products(period: ReportPeriod, *, limit: int = 10) -> list[dict[str, Any]]:
    start_dt, end_dt = _datetime_bounds(period)
    rows = (
        OrderItem.objects.filter(
            order__created_at__gte=start_dt,
            order__created_at__lte=end_dt,
        )
        .exclude(order__status__in=EXCLUDED_STATUSES)
        .values("sku", "product_name")
        .annotate(
            quantity_sold=Coalesce(Sum("quantity"), 0),
            revenue=Coalesce(Sum(_line_revenue_expression()), Decimal("0")),
        )
        .order_by("-revenue")[:limit]
    )
    return [
        {
            "sku": row["sku"],
            "name": row["product_name"],
            "quantity_sold": row["quantity_sold"],
            "revenue": row["revenue"],
        }
        for row in rows
    ]


def top_categories(period: ReportPeriod, *, limit: int = 10) -> list[dict[str, Any]]:
    start_dt, end_dt = _datetime_bounds(period)
    rows = (
        OrderItem.objects.filter(
            order__created_at__gte=start_dt,
            order__created_at__lte=end_dt,
            product__category_id__isnull=False,
        )
        .exclude(order__status__in=EXCLUDED_STATUSES)
        .values("product__category_id")
        .annotate(
            quantity_sold=Coalesce(Sum("quantity"), 0),
            revenue=Coalesce(Sum(_line_revenue_expression()), Decimal("0")),
        )
        .order_by("-revenue")[:limit]
    )
    category_ids = [row["product__category_id"] for row in rows]
    categories = {
        c.pk: c
        for c in Category.objects.filter(pk__in=category_ids).prefetch_related(
            "translations"
        )
    }
    result = []
    for row in rows:
        cat_id = row["product__category_id"]
        category = categories.get(cat_id)
        name = (
            category.safe_translation_getter("name", any_language=True)
            if category
            else f"#{cat_id}"
        )
        result.append(
            {
                "category_id": cat_id,
                "name": name,
                "quantity_sold": row["quantity_sold"],
                "revenue": row["revenue"],
            }
        )
    return result


def top_customers(period: ReportPeriod, *, limit: int = 10) -> list[dict[str, Any]]:
    start_dt, end_dt = _datetime_bounds(period)
    rows = (
        completed_orders_qs()
        .filter(created_at__gte=start_dt, created_at__lte=end_dt)
        .values("guest_email")
        .annotate(
            order_count=Count("id"),
            revenue=Coalesce(Sum("total"), Decimal("0")),
        )
        .order_by("-revenue")[:limit]
    )
    return [
        {
            "email": row["guest_email"],
            "order_count": row["order_count"],
            "revenue": row["revenue"],
        }
        for row in rows
    ]


def low_stock_products(*, limit: int = 15) -> list[Product]:
    return list(
        Product.objects.filter(is_active=True)
        .filter(stock__lte=F("minimum_stock_alert"))
        .select_related("category")
        .prefetch_related("translations", "category__translations")
        .order_by("stock", "sku")[:limit]
    )
