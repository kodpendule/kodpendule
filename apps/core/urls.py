from django.urls import path

from apps.core.views import ContactView, HomeView

app_name = "core"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("kontakt/", ContactView.as_view(), name="contact"),
]
