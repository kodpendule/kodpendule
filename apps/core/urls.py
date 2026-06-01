from apps.core.storefront_urls import localized_path
from apps.core.views import ContactView, HomeView, PrivacyView, TermsView

app_name = "core"

urlpatterns = [
    *localized_path("core:home", HomeView.as_view(), sr="", en=""),
    *localized_path("core:contact", ContactView.as_view(), sr="kontakt/", en="contact/"),
    *localized_path(
        "core:terms",
        TermsView.as_view(),
        sr="uslovi-koriscenja/",
        en="terms-of-service/",
    ),
    *localized_path(
        "core:privacy",
        PrivacyView.as_view(),
        sr="politika-privatnosti/",
        en="privacy-policy/",
    ),
]
