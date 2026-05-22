"""Payment providers registry."""

from apps.orders.payments.cod import CashOnDeliveryProvider

PROVIDERS = {
    CashOnDeliveryProvider.code: CashOnDeliveryProvider(),
}


def get_provider(code: str):
    return PROVIDERS.get(code)
