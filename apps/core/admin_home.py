"""Context for Django admin index (operational home — no duplicate nav)."""

from __future__ import annotations

from datetime import timedelta

from django.http import HttpRequest
from django.utils import timezone

from apps.dashboard.filters import ReportPeriod
from apps.dashboard.selectors import analytics_selectors as analytics
from apps.orders.models import Order


def build_admin_home_context(request: HttpRequest) -> dict:
    today = timezone.localdate()
    period_7d = ReportPeriod(
        start=today - timedelta(days=6),
        end=today,
        preset="7d",
    )
    return {
        "home_overview": analytics.overview_snapshot(),
        "home_pipeline": analytics.status_pipeline_counts(),
        "home_period_7d": analytics.period_order_metrics(period_7d),
        "home_low_stock": analytics.low_stock_products(limit=8),
        "home_recent_orders": (
            Order.objects.select_related("user")
            .order_by("-created_at")[:8]
        ),
    }
