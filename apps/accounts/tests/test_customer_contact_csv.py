import csv
import io

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from apps.accounts.models import CustomerContact
from apps.accounts.services.customer_contact_csv import (
    CSV_FIELD_KEYS,
    CSV_HEADERS_SR,
    EXPORT_FIELD_KEYS,
    export_contacts_csv,
    import_contacts_csv,
)


class CustomerContactCsvTests(TestCase):
    def setUp(self) -> None:
        self.contact = CustomerContact.objects.create(
            email="existing@example.com",
            first_name="Existing",
            last_name="User",
            phone="+381601112233",
            order_count=2,
        )

    def test_export_includes_serbian_header_and_row(self) -> None:
        csv_bytes = export_contacts_csv(CustomerContact.objects.all())
        self.assertTrue(csv_bytes.startswith(b"\xef\xbb\xbf"))
        csv_text = csv_bytes.decode("utf-8-sig")
        header = csv_text.splitlines()[0]
        self.assertIn("Korisničko ime", header)
        self.assertIn("Ulica i broj", header)
        self.assertIn("Grad dostave", header)
        self.assertNotIn("Datum registracije", header)
        self.assertNotIn("Prvi kontakt", header)
        self.assertNotIn("Poslednji kontakt", header)
        self.assertNotIn("Broj narudžbina", header)
        rows = list(csv.DictReader(io.StringIO(csv_text)))
        self.assertEqual(rows[0]["Email"], "existing@example.com")
        self.assertEqual(rows[0]["Ime"], "Existing")
        self.assertEqual(rows[0]["Telefon"], '="+381601112233"')

    def test_import_creates_and_updates_with_serbian_headers(self) -> None:
        fieldnames = [CSV_HEADERS_SR[key] for key in CSV_FIELD_KEYS]
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(
            {
                CSV_HEADERS_SR["email"]: "existing@example.com",
                CSV_HEADERS_SR["first_name"]: "Updated",
                CSV_HEADERS_SR["last_name"]: "Name",
                CSV_HEADERS_SR["phone"]: "+381609998877",
                CSV_HEADERS_SR["order_count"]: "5",
                CSV_HEADERS_SR["registered_at"]: "",
                CSV_HEADERS_SR["first_seen_at"]: "",
                CSV_HEADERS_SR["last_seen_at"]: "",
                CSV_HEADERS_SR["username"]: "",
            }
        )
        writer.writerow(
            {
                CSV_HEADERS_SR["email"]: "new@example.com",
                CSV_HEADERS_SR["first_name"]: "New",
                CSV_HEADERS_SR["last_name"]: "Contact",
                CSV_HEADERS_SR["phone"]: "+381601234567",
                CSV_HEADERS_SR["order_count"]: "1",
                CSV_HEADERS_SR["registered_at"]: "",
                CSV_HEADERS_SR["first_seen_at"]: "",
                CSV_HEADERS_SR["last_seen_at"]: "",
                CSV_HEADERS_SR["username"]: "",
            }
        )
        buffer.seek(0)

        result = import_contacts_csv(buffer)
        self.assertEqual(result.created, 1)
        self.assertEqual(result.updated, 1)

        self.contact.refresh_from_db()
        self.assertEqual(self.contact.first_name, "Updated")
        self.assertEqual(self.contact.order_count, 5)
        self.assertTrue(CustomerContact.objects.filter(email="new@example.com").exists())

    def test_import_strips_excel_phone_formula(self) -> None:
        fieldnames = [CSV_HEADERS_SR[key] for key in EXPORT_FIELD_KEYS]
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(
            {
                CSV_HEADERS_SR["email"]: "excel-phone@example.com",
                CSV_HEADERS_SR["first_name"]: "Excel",
                CSV_HEADERS_SR["last_name"]: "Phone",
                CSV_HEADERS_SR["phone"]: '="+381640000000"',
                CSV_HEADERS_SR["username"]: "",
            }
        )
        buffer.seek(0)

        result = import_contacts_csv(buffer)
        self.assertEqual(result.created, 1)
        contact = CustomerContact.objects.get(email="excel-phone@example.com")
        self.assertEqual(contact.phone, "+381640000000")

    def test_import_accepts_legacy_english_headers(self) -> None:
        csv_body = (
            "email,first_name,last_name,phone,order_count,registered_at,"
            "first_seen_at,last_seen_at,username\n"
            "legacy@example.com,Legacy,User,+381600000001,0,,,,\n"
        )
        result = import_contacts_csv(io.StringIO(csv_body))
        self.assertEqual(result.created, 1)
        self.assertTrue(CustomerContact.objects.filter(email="legacy@example.com").exists())

    def test_admin_export_selected_action(self) -> None:
        User = get_user_model()
        admin = User.objects.create_superuser("admin", "a@test.com", "pass")
        client = Client()
        client.force_login(admin)

        changelist_url = reverse("admin:accounts_customercontact_changelist")
        response = client.post(
            changelist_url,
            {
                "action": "export_selected_csv",
                "_selected_action": [str(self.contact.pk)],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        body = response.content.decode("utf-8-sig")
        header = body.splitlines()[0]
        self.assertIn("Ulica i broj", header)
        self.assertIn("existing@example.com", body)

    def test_admin_import_view(self) -> None:
        User = get_user_model()
        admin = User.objects.create_superuser("admin", "a@test.com", "pass")
        client = Client()
        client.force_login(admin)

        csv_body = (
            "Email,Ime,Prezime,Telefon,Broj narudžbina,Datum registracije,"
            "Prvi kontakt,Poslednji kontakt,Korisničko ime\n"
            "imported@example.com,Im,Ported,+381600000000,0,,,,\n"
        )
        response = client.post(
            reverse("admin:accounts_customercontact_import_csv"),
            {
                "csv_file": SimpleUploadedFile(
                    "contacts.csv",
                    csv_body.encode("utf-8"),
                    content_type="text/csv",
                )
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CustomerContact.objects.filter(email="imported@example.com").exists())
