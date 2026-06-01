"""Contact form submission tests."""

from __future__ import annotations

from django.core import mail
from django.test import TestCase, override_settings

from apps.core.storefront_urls import shop_reverse

EMAIL_SETTINGS = {
    "EMAIL_BACKEND": "django.core.mail.backends.locmem.EmailBackend",
    "EMAIL_HOST": "smtp.sendgrid.net",
    "SENDGRID_API_KEY": "test-key",
    "SHOP_NOTIFICATION_EMAIL": "admin@example.com",
}


def _contact_post(**overrides) -> dict[str, str]:
    data = {
        "name": "Ana Anić",
        "email": "ana@example.com",
        "phone": "+381601112233",
        "message": "Imam pitanje o dostavi proizvoda.",
        "website": "",
    }
    data.update(overrides)
    return data


@override_settings(**EMAIL_SETTINGS)
class ContactFormViewTests(TestCase):
    def test_valid_submission_sends_email(self) -> None:
        response = self.client.post(
            shop_reverse("core:contact"),
            _contact_post(),
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("ana@example.com", mail.outbox[0].reply_to)

    def test_honeypot_does_not_send_email(self) -> None:
        response = self.client.post(
            shop_reverse("core:contact"),
            _contact_post(website="http://spam.example"),
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)

    def test_short_message_rejected(self) -> None:
        response = self.client.post(
            shop_reverse("core:contact"),
            _contact_post(message="Hi"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
