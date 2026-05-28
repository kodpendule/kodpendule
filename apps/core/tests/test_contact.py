from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.core.contact_details import resolve_contact_details
from apps.core.models import FooterSettings


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


@override_settings(CONTACT_EMAIL_TO="shop@example.com")
class ContactViewTests(TestCase):
    def test_contact_page_shows_dummy_details(self) -> None:
        response = self.client.get(reverse("core:contact"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "+381 11 123 4567")
        self.assertContains(response, "info@kodpendule.rs")
        self.assertNotContains(
            response,
            "Kontakt podaci će se pojaviti kada budu podešeni u administraciji.",
        )

    @patch("apps.core.views.send_contact_message")
    def test_contact_form_submits(self, send_mock) -> None:
        response = self.client.post(
            reverse("core:contact"),
            {
                "name": "Milan",
                "email": "milan@example.com",
                "subject": "Pitanje",
                "message": "Zdravo, imam pitanje o dostavi.",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("core:contact"))
        send_mock.assert_called_once_with(
            name="Milan",
            email="milan@example.com",
            subject="Pitanje",
            message="Zdravo, imam pitanje o dostavi.",
        )

    def test_send_contact_message_uses_mail_backend(self) -> None:
        from apps.core.services.contact_email import send_contact_message

        mail.outbox.clear()
        send_contact_message(
            name="Ana",
            email="ana@example.com",
            subject="Test",
            message="Poruka iz testa.",
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["shop@example.com"])
        self.assertEqual(mail.outbox[0].reply_to, ["ana@example.com"])
