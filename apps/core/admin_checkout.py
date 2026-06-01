from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.core.checkout_settings import CheckoutSettings
from apps.core.kp_admin import KPModelAdmin


@admin.register(CheckoutSettings)
class CheckoutSettingsAdmin(KPModelAdmin):
    """Singleton — opens the single settings row (pk=1)."""

    def has_add_permission(self, request):
        return not CheckoutSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    fieldsets = (
        (
            _("Promotional delivery"),
            {
                "description": _(
                    "When the cart subtotal reaches the threshold, delivery cost is "
                    "calculated automatically at checkout."
                ),
                "fields": (
                    "free_shipping_threshold",
                    "threshold_shipping_mode",
                    "discounted_shipping_price",
                ),
            },
        ),
    )

    def changelist_view(self, request, extra_context=None):
        CheckoutSettings.load()
        url = reverse("admin:core_checkoutsettings_change", args=[1])
        return redirect(url)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        formfield = super().formfield_for_choice_field(db_field, request, **kwargs)
        if db_field.name == "threshold_shipping_mode" and formfield:
            formfield.help_text = _(
                "Free shipping sets delivery to 0 RSD. Discounted uses the price below."
            )
        return formfield

    class Media:
        css = {"all": ("admin/css/operational.css",)}
