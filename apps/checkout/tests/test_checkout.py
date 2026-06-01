import uuid
from decimal import Decimal

from django.conf import settings
from django.core import mail
from django.test import Client, RequestFactory, TestCase, override_settings

from apps.cart.cart import SESSION_KEY, get_cart
from apps.categories.models import Category
from apps.checkout.forms import CheckoutForm
from apps.core.checkout_settings import CheckoutSettings, ThresholdShippingMode
from apps.core.checkout_settings import resolve_checkout_shipping_price
from apps.core.storefront_urls import shop_reverse
from apps.orders.models import Order
from apps.orders.services import create_order_from_checkout
from apps.products.models import Product
from apps.shipping.models import City


def _checkout_post_data(city_pk: int, **overrides) -> dict[str, str]:
    data = {
        "guest_email": "guest@example.com",
        "first_name": "Pera",
        "last_name": "Perić",
        "phone": "+381601112233",
        "shipping_city": str(city_pk),
        "shipping_street": "Ulica 1",
        "order_notes": "",
        "accept_legal": "on",
    }
    data.update(overrides)
    return data


class CheckoutServiceTests(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.request.session = self.client.session

        self.city = City.objects.create(
            name="Beograd",
            slug="beograd",
            shipping_price=Decimal("350.00"),
            is_active=True,
        )

        suffix = uuid.uuid4().hex[:8]
        category = Category.objects.create(is_active=True)
        category.set_current_language("sr")
        category.name = "Kat"
        category.slug = f"kat-{suffix}"
        category.save()

        self.product = Product.objects.create(
            category=category,
            sku=f"SKU-CHK-{suffix}",
            price=Decimal("2000.00"),
            stock=10,
        )
        self.product.set_current_language("sr")
        self.product.name = "Checkout product"
        self.product.slug = f"chk-{suffix}"
        self.product.save()

        cart = get_cart(self.request)
        cart.add(self.product, 1)

    def test_create_order_from_checkout(self) -> None:
        cart = get_cart(self.request)
        order = create_order_from_checkout(
            cart=cart,
            user=None,
            guest_email="guest@example.com",
            first_name="Pera",
            last_name="Perić",
            phone="+381601112233",
            shipping_city=self.city,
            shipping_street="Ulica 1",
            order_notes="Pozvati pre dostave.",
        )
        self.assertTrue(order.order_number.startswith("KP-"))
        self.assertTrue(order.is_new)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total, Decimal("2350.00"))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 9)
        self.assertTrue(get_cart(self.request).is_empty)

    def test_free_shipping_when_threshold_met(self) -> None:
        settings_obj = CheckoutSettings.load()
        settings_obj.free_shipping_threshold = Decimal("1000.00")
        settings_obj.threshold_shipping_mode = ThresholdShippingMode.FREE
        settings_obj.save()

        price = resolve_checkout_shipping_price(
            subtotal=Decimal("2000.00"),
            city_shipping_price=Decimal("350.00"),
        )
        self.assertEqual(price, Decimal("0"))

    def test_discounted_shipping_when_threshold_met(self) -> None:
        settings_obj = CheckoutSettings.load()
        settings_obj.free_shipping_threshold = Decimal("1000.00")
        settings_obj.threshold_shipping_mode = ThresholdShippingMode.DISCOUNTED
        settings_obj.discounted_shipping_price = Decimal("199.00")
        settings_obj.save()

        price = resolve_checkout_shipping_price(
            subtotal=Decimal("2000.00"),
            city_shipping_price=Decimal("350.00"),
        )
        self.assertEqual(price, Decimal("199.00"))

    def test_checkout_form_allows_empty_notes(self) -> None:
        form = CheckoutForm(
            data={
                "guest_email": "a@b.rs",
                "first_name": "A",
                "last_name": "B",
                "phone": "123",
                "shipping_city": self.city.pk,
                "shipping_street": "St",
                "order_notes": "",
                "accept_legal": True,
            },
            user=None,
        )
        self.assertTrue(form.is_valid())

    def test_checkout_page_omits_removed_fields(self) -> None:
        suffix = uuid.uuid4().hex[:8]
        category = Category.objects.create(is_active=True)
        category.set_current_language("sr")
        category.name = "Kat"
        category.slug = f"kat-ui-{suffix}"
        category.save()
        product = Product.objects.create(
            category=category,
            sku=f"SKU-UI-{suffix}",
            price=Decimal("500.00"),
            stock=2,
        )
        session = self.client.session
        session[SESSION_KEY] = {str(product.pk): 1}
        session.save()

        response = self.client.get(shop_reverse("checkout:checkout"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "id_shipping_postal_code")
        self.assertNotContains(response, "id_delivery_date")
        self.assertNotContains(response, "id_flexible_delivery")
        self.assertNotContains(response, "Shipping method")


class CheckoutViewTests(TestCase):
    def setUp(self) -> None:
        suffix = uuid.uuid4().hex[:8]
        self.vrdnik = City.objects.create(
            name="Vrdnik",
            slug=f"vrdnik-{suffix}",
            shipping_price=Decimal("450.00"),
            is_active=True,
        )
        category = Category.objects.create(is_active=True)
        category.set_current_language("sr")
        category.name = "Kat"
        category.slug = f"kat-{suffix}"
        category.save()

        self.product = Product.objects.create(
            category=category,
            sku=f"SKU-CHK2-{suffix}",
            price=Decimal("1000.00"),
            stock=10,
        )
        self.product.set_current_language("sr")
        self.product.name = "Product"
        self.product.slug = f"prod-{suffix}"
        self.product.save()

        session = self.client.session
        session[SESSION_KEY] = {str(self.product.pk): 1}
        session.save()

    def test_checkout_page_includes_shipping_scripts(self) -> None:
        response = self.client.get(shop_reverse("checkout:checkout"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="city-prices-data"')
        self.assertContains(response, 'id="checkout-shipping-rules"')
        self.assertContains(response, f'"{self.vrdnik.pk}"')

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        EMAIL_HOST="smtp.sendgrid.net",
        SENDGRID_API_KEY="test-key",
        SHOP_NOTIFICATION_EMAIL="shop@example.com",
    )
    def test_checkout_triggers_low_stock_email(self) -> None:
        self.product.minimum_stock_alert = 10
        self.product.stock = 11
        self.product.save(update_fields=["minimum_stock_alert", "stock"])
        mail.outbox.clear()

        response = self.client.post(
            shop_reverse("checkout:checkout"),
            _checkout_post_data(self.vrdnik.pk),
        )
        self.assertEqual(response.status_code, 302)
        low_stock_msgs = [m for m in mail.outbox if "Malo zaliha" in m.subject or "Low stock" in m.subject]
        self.assertEqual(len(low_stock_msgs), 1)

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        EMAIL_HOST="smtp.sendgrid.net",
        SENDGRID_API_KEY="test-key",
        SHOP_NOTIFICATION_EMAIL="shop@example.com",
    )
    def test_post_checkout_sends_customer_and_staff_emails(self) -> None:
        mail.outbox.clear()
        response = self.client.post(
            shop_reverse("checkout:checkout"),
            _checkout_post_data(self.vrdnik.pk),
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 2)
        recipients = {addr for msg in mail.outbox for addr in msg.to}
        self.assertEqual(recipients, {"guest@example.com", "shop@example.com"})

    def test_checkout_rejects_order_without_legal_consent(self) -> None:
        post_data = _checkout_post_data(self.vrdnik.pk)
        post_data.pop("accept_legal")
        response = self.client.post(
            shop_reverse("checkout:checkout"),
            post_data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)
        self.assertContains(response, "accept_legal")

    def test_post_checkout_places_order_clears_cart_and_redirects(self) -> None:
        with self.settings(SHOP_NOTIFICATION_EMAIL="shop@example.com"):
            response = self.client.post(
                shop_reverse("checkout:checkout"),
                _checkout_post_data(self.vrdnik.pk),
            )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            shop_reverse("checkout:success"),
        )
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.get()
        self.assertEqual(order.total, Decimal("1450.00"))
        self.assertEqual(self.client.session.get(SESSION_KEY), {})

    def test_two_consecutive_orders_succeed(self) -> None:
        with self.settings(SHOP_NOTIFICATION_EMAIL="shop@example.com"):
            first = self.client.post(
                shop_reverse("checkout:checkout"),
                _checkout_post_data(self.vrdnik.pk),
            )
            self.assertEqual(first.status_code, 302)

            session = self.client.session
            session[SESSION_KEY] = {str(self.product.pk): 1}
            session.save()

            second = self.client.post(
                shop_reverse("checkout:checkout"),
                _checkout_post_data(self.vrdnik.pk, first_name="Mika"),
            )

        self.assertEqual(second.status_code, 302)
        self.assertEqual(Order.objects.count(), 2)
        self.assertEqual(
            Order.objects.order_by("pk").last().first_name,
            "Mika",
        )

    def test_checkout_error_does_not_show_validation_banner_for_valid_form(self) -> None:
        self.product.stock = 0
        self.product.save(update_fields=["stock"])

        response = self.client.post(
            shop_reverse("checkout:checkout"),
            _checkout_post_data(self.vrdnik.pk),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)
        self.assertNotContains(
            response,
            "Some fields need your attention",
        )
        self.assertContains(response, "Nema dovoljno")
