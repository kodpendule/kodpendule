import uuid
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.dashboard.filters import ReportPeriod, parse_report_period
from apps.dashboard.selectors import analytics_selectors as analytics
from apps.orders.models import Order, OrderItem, OrderStatus
from apps.shipping.models import City


class ReportPeriodTests(TestCase):
    def test_default_30d(self) -> None:
        period = parse_report_period({})
        self.assertEqual(period.preset, "30d")
        self.assertEqual((period.end - period.start).days, 29)

    def test_manual_date_range(self) -> None:
        period = parse_report_period(
            {
                "filter_mode": "manual",
                "from": "2026-03-01",
                "to": "2026-03-31",
            }
        )
        self.assertEqual(period.preset, "custom")
        self.assertEqual(period.start.isoformat(), "2026-03-01")
        self.assertEqual(period.end.isoformat(), "2026-03-31")
        self.assertEqual(period.label, "01/03/2026 — 31/03/2026")

    def test_single_day_label_uses_short_date(self) -> None:
        day = timezone.localdate()
        period = ReportPeriod(start=day, end=day, preset="custom")
        self.assertEqual(period.label, day.strftime("%d/%m/%Y"))


class AnalyticsSelectorTests(TestCase):
    def setUp(self) -> None:
        self.city = City.objects.create(
            name="Beograd",
            slug="beograd",
            shipping_price=Decimal("300"),
            is_active=True,
        )
        suffix = uuid.uuid4().hex[:8]
        today = timezone.localdate()
        self.period = ReportPeriod(
            start=today - timedelta(days=7),
            end=today,
            preset="7d",
        )
        self.order = Order.objects.create(
            order_number=f"KP-DASH-{suffix}",
            guest_email="dash@example.com",
            first_name="Test",
            last_name="User",
            phone="123",
            shipping_street="St",
            shipping_city_name="Beograd",
            shipping_city=self.city,
            requested_delivery_date=today,
            order_notes="Note",
            shipping_price=Decimal("300"),
            subtotal=Decimal("1000"),
            total=Decimal("1300"),
            status=OrderStatus.PENDING,
        )
        OrderItem.objects.create(
            order=self.order,
            product_name="Widget",
            sku=f"W-{suffix}",
            unit_price=Decimal("1000"),
            quantity=1,
        )

    def test_period_metrics(self) -> None:
        metrics = analytics.period_order_metrics(self.period)
        self.assertGreaterEqual(metrics["order_count"], 1)
        self.assertGreaterEqual(metrics["revenue"], Decimal("1300"))

    def test_status_distribution(self) -> None:
        rows = analytics.order_status_distribution(self.period)
        self.assertTrue(any(row["status"] == OrderStatus.PENDING for row in rows))

    def test_top_products(self) -> None:
        rows = analytics.top_products(self.period)
        self.assertEqual(rows[0]["sku"], self.order.items.first().sku)


class DashboardViewTests(TestCase):
    def test_requires_staff(self) -> None:
        response = self.client.get(reverse("dashboard:index"))
        self.assertEqual(response.status_code, 302)

    def test_staff_can_open_dashboard(self) -> None:
        from django.contrib.auth import get_user_model

        User = get_user_model()
        admin = User.objects.create_superuser("admin", "admin@test.com", "pass")
        self.client.login(username="admin", password="pass")
        response = self.client.get(reverse("dashboard:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Analitika prodavnice")
        self.assertContains(response, "Pregled")
        self.assertContains(response, 'id="nav-sidebar"')
        self.assertContains(response, "kp-admin-nav")
        self.assertContains(response, 'id="id_filter_mode"')
        self.assertContains(response, 'id="chart-revenue-data"')
        self.assertContains(response, 'id="chart-orders-data"')
        self.assertContains(response, "dashboard-charts.js")
        self.assertNotContains(response, "dashboard-quick-links")
        content = response.content.decode()
        self.assertEqual(content.count("<h1>"), 1)
