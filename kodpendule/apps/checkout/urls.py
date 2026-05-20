from django.urls import path

from apps.checkout.views import CheckoutSuccessView, CheckoutView

app_name = "checkout"

urlpatterns = [
    path("placanje/", CheckoutView.as_view(), name="checkout"),
    path("placanje/uspeh/", CheckoutSuccessView.as_view(), name="success"),
]
