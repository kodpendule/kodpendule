from django.test import TestCase

from apps.core.contact_details import resolve_contact_details
from apps.core.models import FooterSettings
from apps.core.storefront_urls import shop_reverse


class ContactDetailsTests(TestCase):
    def test_dummy_details_when_footer_empty(self) -> None:
        details = resolve_contact_details(None)
        self.assertEqual(details.phone, "+381 11 123 4567")
        self.assertEqual(details.email, "info@kodpendule.rs")
        self.assertIn("Beograd", details.address)

    def test_admin_footer_overrides_dummy(self) -> None:
        footer = FooterSettings(pk=1)
        footer.set_current_language("sr")
        footer.phone = "+381 64 999 8888"
        footer.email = "prodavnica@example.com"
        footer.address = "Nova adresa 5"
        footer.working_hours = "08–20"
        footer.save()

        details = resolve_contact_details(footer)
        self.assertEqual(details.phone, "+381 64 999 8888")
        self.assertEqual(details.email, "prodavnica@example.com")


class ContactViewTests(TestCase):
    def test_contact_page_shows_dummy_details(self) -> None:
        response = self.client.get(shop_reverse("core:contact"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "+381 11 123 4567")
        self.assertContains(response, "info@kodpendule.rs")
        self.assertNotContains(response, "Send us a message")
        self.assertNotContains(response, 'name="subject"')
        self.assertNotContains(response, 'name="message"')
