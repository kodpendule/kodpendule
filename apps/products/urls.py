from apps.core.storefront_urls import localized_path
from apps.products.views import (
    ProductDetailView,
    ProductListView,
    PromoProductListView,
    RecommendedProductListView,
)

app_name = "products"

urlpatterns = [
    *localized_path(
        "products:list",
        ProductListView.as_view(),
        sr="proizvodi/",
        en="products/",
    ),
    *localized_path(
        "products:detail",
        ProductDetailView.as_view(),
        sr="proizvodi/<slug:slug>/",
        en="products/<slug:slug>/",
    ),
    *localized_path(
        "products:promo",
        PromoProductListView.as_view(),
        sr="promo-akcije/",
        en="promo-sales/",
    ),
    *localized_path(
        "products:recommended",
        RecommendedProductListView.as_view(),
        sr="preporuceni-proizvodi/",
        en="recommended-products/",
    ),
]
