"""Export and import archived customer contacts as CSV."""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from apps.accounts.models import CustomerContact
from apps.accounts.services.customer_archive import normalize_customer_email

User = get_user_model()

CSV_FIELD_KEYS = [
    "email",
    "first_name",
    "last_name",
    "phone",
    "order_count",
    "registered_at",
    "first_seen_at",
    "last_seen_at",
    "username",
]

# Serbian CSV column headers (Latin script).
CSV_HEADERS_SR: dict[str, str] = {
    "email": "Email",
    "first_name": "Ime",
    "last_name": "Prezime",
    "phone": "Telefon",
    "order_count": "Broj narudžbina",
    "registered_at": "Datum registracije",
    "first_seen_at": "Prvi kontakt",
    "last_seen_at": "Poslednji kontakt",
    "username": "Korisničko ime",
}

EXPORT_FIELDNAMES = [CSV_HEADERS_SR[key] for key in CSV_FIELD_KEYS]

# English headers accepted on import for files exported before localization.
_CSV_HEADERS_EN: dict[str, str] = {
    "email": "email",
    "first_name": "first_name",
    "last_name": "last_name",
    "phone": "phone",
    "order_count": "order_count",
    "registered_at": "registered_at",
    "first_seen_at": "first_seen_at",
    "last_seen_at": "last_seen_at",
    "username": "username",
}


def _normalize_header(header: str) -> str:
    return header.strip().casefold()


def _build_header_to_field() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for key in CSV_FIELD_KEYS:
        mapping[_normalize_header(CSV_HEADERS_SR[key])] = key
        mapping[_normalize_header(_CSV_HEADERS_EN[key])] = key
    return mapping


HEADER_TO_FIELD = _build_header_to_field()

REQUIRED_IMPORT_FIELD = "email"


@dataclass
class ImportResult:
    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list[str] | None = None

    def __post_init__(self) -> None:
        if self.errors is None:
            self.errors = []


def export_contacts_csv() -> bytes:
    """UTF-8 CSV with BOM so Excel on Windows shows č, ž, đ, š correctly."""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=EXPORT_FIELDNAMES, extrasaction="ignore")
    writer.writeheader()

    contacts = CustomerContact.objects.select_related("user").order_by("-last_seen_at")
    for contact in contacts:
        row = {
            "email": contact.email,
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "phone": contact.phone,
            "order_count": contact.order_count,
            "registered_at": _format_dt(contact.registered_at),
            "first_seen_at": _format_dt(contact.first_seen_at),
            "last_seen_at": _format_dt(contact.last_seen_at),
            "username": contact.user.username if contact.user_id else "",
        }
        writer.writerow({CSV_HEADERS_SR[key]: row[key] for key in CSV_FIELD_KEYS})

    return buffer.getvalue().encode("utf-8-sig")


def _format_dt(value: datetime | None) -> str:
    if not value:
        return ""
    if timezone.is_aware(value):
        value = timezone.localtime(value)
    return value.strftime("%Y-%m-%d %H:%M:%S")


def _column_label(field: str) -> str:
    return CSV_HEADERS_SR.get(field, field)


def _parse_optional_int(raw: str, *, field: str, row_num: int) -> int | None:
    text = (raw or "").strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError as exc:
        raise ValueError(
            f"Red {row_num}: neispravan {_column_label(field)} '{raw}'."
        ) from exc


def _parse_optional_dt(raw: str, *, field: str, row_num: int) -> datetime | None:
    text = (raw or "").strip()
    if not text:
        return None
    parsed = parse_datetime(text)
    if parsed is None:
        raise ValueError(
            f"Red {row_num}: neispravan {_column_label(field)} '{raw}' "
            "(očekivan format YYYY-MM-DD HH:MM:SS)."
        )
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


def _read_csv_text(file_obj) -> str:
    if isinstance(file_obj, io.StringIO):
        return file_obj.getvalue()

    raw = file_obj.read()
    if isinstance(raw, bytes):
        return raw.decode("utf-8-sig")
    return raw


def _map_row(raw_row: dict[str, str | None]) -> dict[str, str]:
    mapped: dict[str, str] = {}
    for header, value in raw_row.items():
        if not header:
            continue
        field = HEADER_TO_FIELD.get(_normalize_header(header))
        if field:
            mapped[field] = value or ""
    return mapped


def _import_headers_include_email(fieldnames: list[str] | None) -> bool:
    if not fieldnames:
        return False
    mapped = {
        HEADER_TO_FIELD.get(_normalize_header(name))
        for name in fieldnames
        if name
    }
    return REQUIRED_IMPORT_FIELD in mapped


@transaction.atomic
def import_contacts_csv(file_obj) -> ImportResult:
    """Upsert contacts from CSV by email. Existing rows are updated; new emails are created."""
    reader = csv.DictReader(io.StringIO(_read_csv_text(file_obj)))
    if not reader.fieldnames:
        raise ValueError("CSV fajl nema red sa nazivima kolona.")

    if not _import_headers_include_email(reader.fieldnames):
        raise ValueError(f"Nedostaje obavezna kolona: {CSV_HEADERS_SR[REQUIRED_IMPORT_FIELD]}.")

    result = ImportResult()
    row_num = 1

    for raw_row in reader:
        row_num += 1
        row = _map_row(raw_row)
        email = normalize_customer_email(row.get("email", ""))
        if not email:
            result.skipped += 1
            continue

        first_name = (row.get("first_name") or "").strip()
        last_name = (row.get("last_name") or "").strip()
        phone = (row.get("phone") or "").strip()
        username = (row.get("username") or "").strip()

        user = None
        if username:
            user = User.objects.filter(username=username).first()

        order_count = _parse_optional_int(
            row.get("order_count", ""), field="order_count", row_num=row_num
        )
        registered_at = _parse_optional_dt(
            row.get("registered_at", ""), field="registered_at", row_num=row_num
        )

        contact, created = CustomerContact.objects.select_for_update().get_or_create(
            email=email,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "user": user,
                "order_count": order_count if order_count is not None else 0,
                "registered_at": registered_at,
            },
        )

        if created:
            result.created += 1
            continue

        contact.first_name = first_name or contact.first_name
        contact.last_name = last_name or contact.last_name
        contact.phone = phone or contact.phone
        if user:
            contact.user = user
        if order_count is not None:
            contact.order_count = order_count
        if registered_at is not None:
            contact.registered_at = registered_at

        contact.save(
            update_fields=[
                "first_name",
                "last_name",
                "phone",
                "user",
                "order_count",
                "registered_at",
                "last_seen_at",
            ]
        )
        result.updated += 1

    return result
