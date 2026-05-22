from django.urls import path

from apps.accounts.views import UserLoginView, UserLogoutView, UserRegisterView

app_name = "accounts"

urlpatterns = [
    path("prijava/", UserLoginView.as_view(), name="login"),
    path("registracija/", UserRegisterView.as_view(), name="register"),
    path("odjava/", UserLogoutView.as_view(), name="logout"),
]
