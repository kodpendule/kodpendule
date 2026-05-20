from django.urls import path

from apps.cart.views import CartAddView, CartDetailView, CartRemoveView, CartUpdateView

app_name = "cart"

urlpatterns = [
    path("korpa/", CartDetailView.as_view(), name="detail"),
    path("korpa/dodaj/", CartAddView.as_view(), name="add"),
    path("korpa/dodaj/<slug:slug>/", CartAddView.as_view(), name="add_by_slug"),
    path("korpa/azuriraj/<int:product_id>/", CartUpdateView.as_view(), name="update"),
    path("korpa/ukloni/<int:product_id>/", CartRemoveView.as_view(), name="remove"),
]
