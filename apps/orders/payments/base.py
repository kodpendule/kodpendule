"""
Payment provider abstraction.

Implementations live alongside this module; checkout selects provider by payment method.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from apps.orders.models import Order


@dataclass(frozen=True)
class PaymentResult:
    success: bool
    message: str
    transaction_id: str | None = None


class PaymentProvider(Protocol):
    """Interface for COD, Stripe, PayPal, and local gateways."""

    code: str

    def get_display_name(self) -> str:
        """Human-readable label for checkout."""

    def charge(self, order: Order) -> PaymentResult:
        """
        Authorize or record payment.
        COD returns success immediately; card gateways charge here.
        """
