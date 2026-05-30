import uuid
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core import mail
from django.test import Client, RequestFactory, TestCase
from django.utils import timezone

from apps.cart.cart import SESSION_KEY, get_cart
from apps.categories.models import Category
from apps.checkout.forms import CheckoutForm
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
        "shipping_postal_code": "11000",
        "order_notes": "Pozvati pre dostave.",
        "delivery_date": _tomorrow_iso(),
    }
    data.update(overrides)
    return data


def _tomorrow_iso() -> str:
    return (timezone.localdate() + timedelta(days=1)).isoformat()


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
            shipping_postal_code="11000",
            billing_street="Ulica 1",
            billing_city_name="Beograd",
            billing_postal_code="11000",
            order_notes="Pozvati pre dostave.",
            delivery_date=timezone.localdate() + timedelta(days=1),
            flexible_delivery=True,
        )
        self.assertTrue(order.order_number.startswith("KP-"))
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total, Decimal("2350.00"))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 9)
        self.assertTrue(get_cart(self.request).is_empty)

    def test_checkout_form_copies_billing_from_delivery_address(self) -> None:
        form = CheckoutForm(
            data={
                "guest_email": "a@b.rs",
                "first_name": "A",
                "last_name": "B",
                "phone": "123",
                "shipping_city": self.city.pk,
                "shipping_street": "Ulica 5",
                "shipping_postal_code": "22404",
                "order_notes": "Pozvati pre dostave.",
                "delivery_date": _tomorrow_iso(),
            },
            user=None,
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["billing_street"], "Ulica 5")
        self.assertEqual(form.cleaned_data["billing_city_name"], "Beograd")
        self.assertEqual(form.cleaned_data["billing_postal_code"], "22404")

    def test_checkout_page_omits_billing_section(self) -> None:
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
        self.assertNotContains(response, "checkout-billing-heading")
        self.assertNotContains(response, "id_billing_same")
        self.assertContains(response, "checkout-shipping-heading")

    def test_checkout_form_requires_notes(self) -> None:
        form = CheckoutForm(
            data={
                "guest_email": "a@b.rs",
                "first_name": "A",
                "last_name": "B",
                "phone": "123",
                "shipping_city": self.city.pk,
                "shipping_street": "St",
                "shipping_postal_code": "11000",
                "order_notes": "",
                "delivery_date": _tomorrow_iso(),
            },
            user=None,
        )
        self.assertFalse(form.is_valid())

    def test_checkout_form_requires_delivery_date(self) -> None:
        form = CheckoutForm(
            data={
                "guest_email": "a@b.rs",
                "first_name": "A",
                "last_name": "B",
                "phone": "123",
                "shipping_city": self.city.pk,
                "shipping_street": "St",
                "shipping_postal_code": "11000",
                "order_notes": "Notes",
            },
            user=None,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("delivery_date", form.errors)


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
            stock=5,
        )
        self.product.set_current_language("sr")
        self.product.name = "Product"
        self.product.slug = f"prod-{suffix}"
        self.product.save()

        session = self.client.session
        session[SESSION_KEY] = {str(self.product.pk): 1}
        session.save()

    def test_checkout_page_includes_city_price_script(self) -> None:
        response = self.client.get(shop_reverse("checkout:checkout"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="city-prices-data"')
        self.assertContains(response, f'"{self.vrdnik.pk}"')
        self.assertContains(response, "450.00")

    def test_order_records_vrdnik_shipping_fee(self) -> None:
        request = RequestFactory().get("/")
        request.session = self.client.session
        cart = get_cart(request)
        order = create_order_from_checkout(
            cart=cart,
            user=None,
            guest_email="guest@example.com",
            first_name="Ana",
            last_name="Anić",
            phone="+381601112233",
            shipping_city=self.vrdnik,
            shipping_street="Centar 1",
            shipping_postal_code="22404",
            billing_street="Centar 1",
            billing_city_name="Vrdnik",
            billing_postal_code="22404",
            order_notes="Pozvati pre dostave.",
            delivery_date=timezone.localdate() + timedelta(days=1),
            flexible_delivery=False,
        )
        self.assertEqual(order.shipping_price, Decimal("450.00"))
        self.assertEqual(order.shipping_city_name, "Vrdnik")
        self.assertEqual(order.total, Decimal("1450.00"))

    def test_post_checkout_places_order_clears_cart_and_redirects(self) -> None:
        with self.settings(SHOP_ORDER_NOTIFICATION_EMAILS=["shop@example.com"]):
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
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(order.order_number, mail.outbox[0].subject)

        success = self.client.get(response["Location"])
        self.assertEqual(success.status_code, 200)
        self.assertContains(success, order.order_number)

    def test_post_checkout_wrong_language_path_still_places_order(self) -> None:
        self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = "en"
        with self.settings(SHOP_ORDER_NOTIFICATION_EMAILS=["shop@example.com"]):
            response = self.client.post(
                "/placanje/",
                _checkout_post_data(self.vrdnik.pk),
            )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(self.client.session.get(SESSION_KEY), {})

    def test_post_checkout_invalid_data_shows_errors_without_creating_order(self) -> None:
        response = self.client.post(
            shop_reverse("checkout:checkout"),
            _checkout_post_data(self.vrdnik.pk, order_notes=""),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)
        self.assertContains(response, "shop-field--invalid")
        self.assertNotEqual(self.client.session.get(SESSION_KEY), {})
