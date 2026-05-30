from apps.core.storefront_urls import localized_path
from apps.core.views import ContactView, HomeView

app_name = "core"

urlpatterns = [
    *localized_path("core:home", HomeView.as_view(), sr="", en=""),
    *localized_path("core:contact", ContactView.as_view(), sr="kontakt/", en="contact/"),
]
