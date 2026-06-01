from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _

from apps.core.kp_admin import KPModelAdmin
from apps.shipping.forms import CityPaymentSettingsForm, CitySelectorForm
from apps.shipping.models import City
from apps.shipping.selectors import active_cities


@admin.register(City)
class CityAdmin(KPModelAdmin):
    list_display = ("name", "slug", "shipping_price", "is_active", "sort_order")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order", "name")

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "payment-settings/",
                self.admin_site.admin_view(self.payment_settings_view),
                name="shipping_city_payment_settings",
            ),
        ]
        return custom + urls

    def payment_settings_view(self, request: HttpRequest) -> HttpResponse:
        cities = list(active_cities())
        if not cities:
            messages.warning(
                request,
                _("Add at least one active delivery city before configuring payment rules."),
            )
            return redirect(reverse("admin:shipping_city_changelist"))

        selected_pk = request.GET.get("city") or request.POST.get("city")
        city = None
        if selected_pk:
            city = get_object_or_404(City, pk=selected_pk, is_active=True)
        if city is None:
            city = cities[0]

        if request.method == "POST":
            form = CityPaymentSettingsForm(request.POST, instance=city)
            if form.is_valid():
                form.save()
                messages.success(
                    request,
                    _("Payment settings saved for %(city)s.")
                    % {"city": city.name},
                )
                url = reverse("admin:shipping_city_payment_settings")
                return redirect(f"{url}?city={city.pk}")
        else:
            form = CityPaymentSettingsForm(instance=city)

        city_selector = CitySelectorForm(initial={"city": city.pk})

        context = {
            **self.admin_site.each_context(request),
            "title": _("Payment settings"),
            "opts": self.model._meta,
            "form": form,
            "city_selector": city_selector,
            "selected_city": city,
            "payment_settings_url": reverse("admin:shipping_city_payment_settings"),
            "has_view_permission": self.has_view_permission(request),
            "has_change_permission": self.has_change_permission(request, city),
        }
        return render(request, "admin/shipping/city/payment_settings.html", context)
