"""Assemble dashboard metrics and chart payloads from analytics selectors."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from django.utils.translation import gettext as _

from apps.core.locale_dates import latin_month_year, latin_short_date
from apps.dashboard.filters import ReportPeriod, period_filter_choices
from apps.dashboard.selectors import analytics_selectors as analytics
from apps.orders.models import OrderStatus


def build_dashboard_context(period: ReportPeriod) -> dict[str, Any]:
    overview = analytics.overview_snapshot()
    period_metrics = analytics.period_order_metrics(period)
    pipeline = analytics.status_pipeline_counts()
    days_in_period = (period.end - period.start).days + 1

    if days_in_period <= 90:
        raw_series = analytics.sales_by_day(period)
        time_labels, time_revenue, time_orders = _filled_daily_series(period, raw_series)
        time_chart_title = _("Daily revenue")
        orders_chart_title = _("Daily orders")
    else:
        raw_series = analytics.sales_by_month(period)
        time_labels, time_revenue, time_orders = _filled_monthly_series(period, raw_series)
        time_chart_title = _("Monthly revenue")
        orders_chart_title = _("Monthly orders")

    top_products = analytics.top_products(period)
    top_categories = analytics.top_categories(period)
    status_rows = analytics.order_status_distribution(period)
    top_customers = analytics.top_customers(period)

    return {
        "period": period,
        "period_choices": period_filter_choices(),
        "overview": overview,
        "period_metrics": period_metrics,
        "pipeline": pipeline,
        "low_stock_products": analytics.low_stock_products(),
        "top_products": top_products,
        "top_categories": top_categories,
        "top_customers": top_customers,
        "time_chart_title": time_chart_title,
        "orders_chart_title": orders_chart_title,
        "chart_legends": {
            "revenue": _("Revenue"),
            "orders": _("Orders"),
        },
        "charts": {
            "revenue": {
                "labels": time_labels,
                "values": time_revenue,
            },
            "orders": {
                "labels": time_labels,
                "values": time_orders,
            },
            "top_products": {
                "labels": [p["name"][:40] for p in top_products],
                "values": [float(p["revenue"]) for p in top_products],
            },
            "categories": {
                "labels": [c["name"][:40] for c in top_categories],
                "values": [float(c["revenue"]) for c in top_categories],
            },
            "order_status": {
                "labels": [_status_label(row["status"]) for row in status_rows],
                "values": [row["count"] for row in status_rows],
            },
        },
    }


def _filled_daily_series(
    period: ReportPeriod,
    rows: list[dict[str, Any]],
) -> tuple[list[str], list[float], list[int]]:
    by_day = {row["day"]: row for row in rows}
    labels: list[str] = []
    revenue_values: list[float] = []
    order_values: list[int] = []
    day = period.start
    while day <= period.end:
        row = by_day.get(day)
        labels.append(_format_day(day))
        revenue_values.append(float(row["revenue"]) if row else 0.0)
        order_values.append(int(row["orders"]) if row else 0)
        day += timedelta(days=1)
    return labels, revenue_values, order_values


def _filled_monthly_series(
    period: ReportPeriod,
    rows: list[dict[str, Any]],
) -> tuple[list[str], list[float], list[int]]:
    by_month: dict[tuple[int, int], dict[str, Any]] = {}
    for row in rows:
        month_date = row["month"]
        if month_date is None:
            continue
        by_month[(month_date.year, month_date.month)] = row

    labels: list[str] = []
    revenue_values: list[float] = []
    order_values: list[int] = []
    year, month = period.start.year, period.start.month
    end_year, end_month = period.end.year, period.end.month
    while (year, month) <= (end_year, end_month):
        row = by_month.get((year, month))
        labels.append(_format_month(date(year, month, 1)))
        revenue_values.append(float(row["revenue"]) if row else 0.0)
        order_values.append(int(row["orders"]) if row else 0)
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
    return labels, revenue_values, order_values


def _format_day(value: date) -> str:
    return latin_short_date(value)


def _format_month(value: date) -> str:
    return latin_month_year(value)


def _status_label(code: str) -> str:
    try:
        return OrderStatus(code).label
    except ValueError:
        return code


def decimal_display(value: Decimal) -> str:
    return f"{value:,.2f}"
