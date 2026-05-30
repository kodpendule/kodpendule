from apps.accounts.views import UserLoginView, UserLogoutView, UserRegisterView
from apps.core.storefront_urls import localized_path

app_name = "accounts"

urlpatterns = [
    *localized_path("accounts:login", UserLoginView.as_view(), sr="prijava/", en="login/"),
    *localized_path(
        "accounts:register",
        UserRegisterView.as_view(),
        sr="registracija/",
        en="register/",
    ),
    *localized_path("accounts:logout", UserLogoutView.as_view(), sr="odjava/", en="logout/"),
]
