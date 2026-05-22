from django.urls import path

from apps.categories.views import CategoryDetailView, CategoryListView

app_name = "categories"

urlpatterns = [
    path("kategorije/", CategoryListView.as_view(), name="list"),
    path("kategorije/<slug:slug>/", CategoryDetailView.as_view(), name="detail"),
]
