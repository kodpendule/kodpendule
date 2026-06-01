import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.orders.models import Order
from apps.orders.selectors.order_admin_selectors import unread_order_count
from apps.shipping.models import City


class OrderAdminUnreadTests(TestCase):
    def setUp(self) -> None:
        suffix = uuid.uuid4().hex[:8]
        self.city = City.objects.create(
            name="Beograd",
            slug=f"bg-{suffix}",
            shipping_price=Decimal("300"),
        )
        self.order = Order.objects.create(
            order_number=f"KP-NEW-{suffix}",
            guest_email="guest@example.com",
            first_name="Pera",
            last_name="Perić",
            phone="+381601112233",
            shipping_street="Ulica 1",
            shipping_city_name="Beograd",
            shipping_city=self.city,
            shipping_price=Decimal("300"),
            subtotal=Decimal("1000"),
            total=Decimal("1300"),
            is_new=True,
        )
        User = get_user_model()
        self.admin = User.objects.create_superuser("admin", "admin@test.com", "pass")
        self.client = Client()
        self.client.force_login(self.admin)

    def test_new_order_counts_as_unread(self) -> None:
        self.assertEqual(unread_order_count(), 1)

    def test_opening_order_marks_as_read(self) -> None:
        url = reverse("admin:orders_order_change", args=[self.order.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertFalse(self.order.is_new)
        self.assertEqual(unread_order_count(), 0)

    def test_export_selected_orders_csv(self) -> None:
        changelist_url = reverse("admin:orders_order_changelist")
        response = self.client.post(
            changelist_url,
            {
                "action": "export_selected_csv",
                "_selected_action": [str(self.order.pk)],
            },
        )
        self.assertEqual(response.status_code, 200)
        body = response.content.decode("utf-8-sig")
        self.assertIn("Broj narudžbine", body.splitlines()[0])
        self.assertIn(self.order.order_number, body)
        self.assertIn("Ulica 1", body)
