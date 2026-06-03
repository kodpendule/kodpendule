from apps.core.storefront_urls import localized_path
from apps.orders.views import GuestOrderTrackView, OrderDetailView, OrderHistoryView

app_name = "orders"

urlpatterns = [
    *localized_path(
        "orders:track",
        GuestOrderTrackView.as_view(),
        sr="narudzbina/pracenje/",
        en="order/track/",
    ),
    *localized_path(
        "orders:detail",
        OrderDetailView.as_view(),
        sr="narudzba/<slug:order_number>/",
        en="order/<slug:order_number>/",
    ),
    *localized_path(
        "orders:history",
        OrderHistoryView.as_view(),
        sr="nalog/narudzbine/",
        en="account/orders/",
    ),
]
