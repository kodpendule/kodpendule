from django.urls import path

from apps.products.views import ProductDetailView, ProductListView

app_name = "products"

urlpatterns = [
    path("proizvodi/", ProductListView.as_view(), name="list"),
    path("proizvodi/<slug:slug>/", ProductDetailView.as_view(), name="detail"),
]
