from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.dashboard.filters import ReportPeriod
from apps.dashboard.services.report_service import build_dashboard_context


class ReportServiceChartTests(TestCase):
    def test_build_dashboard_context_includes_time_series(self) -> None:
        today = timezone.localdate()
        period = ReportPeriod(
            start=today - timedelta(days=3),
            end=today,
            preset="custom",
        )
        context = build_dashboard_context(period)
        revenue = context["charts"]["revenue"]
        orders = context["charts"]["orders"]
        self.assertEqual(len(revenue["labels"]), 4)
        self.assertEqual(len(revenue["values"]), 4)
        self.assertEqual(len(orders["values"]), 4)
        self.assertIn("/", revenue["labels"][0])
