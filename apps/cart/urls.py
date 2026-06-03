from apps.cart.views import (
    CartAddView,
    CartDetailView,
    CartRemoveView,
    CartStateView,
    CartUpdateView,
)
from apps.core.storefront_urls import localized_path

app_name = "cart"

urlpatterns = [
    *localized_path("cart:detail", CartDetailView.as_view(), sr="korpa/", en="cart/"),
    *localized_path("cart:state", CartStateView.as_view(), sr="korpa/stanje/", en="cart/state/"),
    *localized_path("cart:add", CartAddView.as_view(), sr="korpa/dodaj/", en="cart/add/"),
    *localized_path(
        "cart:add_by_slug",
        CartAddView.as_view(),
        sr="korpa/dodaj/<slug:slug>/",
        en="cart/add/<slug:slug>/",
    ),
    *localized_path(
        "cart:update",
        CartUpdateView.as_view(),
        sr="korpa/azuriraj/<int:product_id>/",
        en="cart/update/<int:product_id>/",
    ),
    *localized_path(
        "cart:remove",
        CartRemoveView.as_view(),
        sr="korpa/ukloni/<int:product_id>/",
        en="cart/remove/<int:product_id>/",
    ),
]
