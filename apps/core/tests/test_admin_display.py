from django.test import SimpleTestCase
from django.utils.translation import gettext as _

from apps.core.admin_display import order_status_badge, stock_cell
from apps.orders.models import OrderStatus


class AdminDisplayTests(SimpleTestCase):
    def test_order_status_badge_renders(self):
        html = order_status_badge(OrderStatus.PENDING)
        self.assertIn("kp-badge", html)
        self.assertIn("kp-badge--neutral", html)

    def test_low_stock_cell(self):
        html = stock_cell(2, is_low=True, alert_at=5)
        self.assertIn("kp-stock--low", html)
        self.assertIn(str(_("Restock")), html)
