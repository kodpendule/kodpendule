"""Cash on delivery — default provider for v1."""

from __future__ import annotations

from apps.orders.payments.base import PaymentResult


class CashOnDeliveryProvider:
    code = "cod"

    def get_display_name(self) -> str:
        return "Plaćanje pouzećem"

    def charge(self, order) -> PaymentResult:
        return PaymentResult(success=True, message="Cash on delivery")
