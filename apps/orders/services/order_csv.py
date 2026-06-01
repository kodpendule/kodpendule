"""Export orders to CSV for admin."""

from __future__ import annotations

import csv
import io
from typing import Iterable

from apps.accounts.services.customer_contact_csv import _format_phone_for_excel
from apps.orders.models import Order

ORDER_EXPORT_FIELD_KEYS = [
    "order_number",
    "customer_name",
    "email",
    "phone",
    "delivery_address",
    "requested_delivery_date",
    "status",
    "total",
    "created_at",
    "order_notes",
]

ORDER_CSV_HEADERS_SR: dict[str, str] = {
    "order_number": "Broj narudžbine",
    "customer_name": "Ime kupca",
    "email": "Email",
    "phone": "Telefon",
    "delivery_address": "Adresa dostave",
    "requested_delivery_date": "Datum dostave",
    "status": "Status",
    "total": "Ukupno",
    "created_at": "Datum",
    "order_notes": "Napomena",
}

ORDER_EXPORT_FIELDNAMES = [ORDER_CSV_HEADERS_SR[key] for key in ORDER_EXPORT_FIELD_KEYS]


def export_orders_csv(orders: Iterable[Order]) -> bytes:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=ORDER_EXPORT_FIELDNAMES, extrasaction="ignore")
    writer.writeheader()

    for order in orders:
        row = {
            "order_number": order.order_number,
            "customer_name": order.customer_full_name,
            "email": order.customer_email,
            "phone": _format_phone_for_excel(order.phone),
            "delivery_address": order.delivery_address_display,
            "requested_delivery_date": order.requested_delivery_date.strftime("%Y-%m-%d"),
            "status": order.get_status_display(),
            "total": str(order.total),
            "created_at": order.created_at.strftime("%Y-%m-%d %H:%M"),
            "order_notes": order.order_notes or "",
        }
        writer.writerow({ORDER_CSV_HEADERS_SR[key]: row[key] for key in ORDER_EXPORT_FIELD_KEYS})

    return buffer.getvalue().encode("utf-8-sig")
