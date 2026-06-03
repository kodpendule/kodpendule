from apps.categories.views import CategoryDetailView, CategoryListView
from apps.core.storefront_urls import localized_path

app_name = "categories"

urlpatterns = [
    *localized_path(
        "categories:list",
        CategoryListView.as_view(),
        sr="kategorije/",
        en="categories/",
    ),
    *localized_path(
        "categories:detail",
        CategoryDetailView.as_view(),
        sr="kategorije/<path:category_path>/",
        en="categories/<path:category_path>/",
    ),
]
