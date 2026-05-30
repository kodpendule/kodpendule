from apps.checkout.views import CheckoutSuccessView, CheckoutView
from apps.core.storefront_urls import localized_path

app_name = "checkout"

urlpatterns = [
    *localized_path(
        "checkout:checkout",
        CheckoutView.as_view(),
        sr="placanje/",
        en="checkout/",
    ),
    *localized_path(
        "checkout:success",
        CheckoutSuccessView.as_view(),
        sr="placanje/uspeh/",
        en="checkout/success/",
    ),
]
