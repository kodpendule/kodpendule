from django.urls import path

from apps.orders.views import GuestOrderTrackView, OrderDetailView, OrderHistoryView

app_name = "orders"

urlpatterns = [
    path("narudzba/pracenje/", GuestOrderTrackView.as_view(), name="track"),
    path("narudzba/<slug:order_number>/", OrderDetailView.as_view(), name="detail"),
    path("nalog/narudzbe/", OrderHistoryView.as_view(), name="history"),
]
