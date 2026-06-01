from django import forms
from django.utils.translation import gettext_lazy as _

from apps.core.checkout_settings import ThresholdShippingMode
from apps.shipping.models import City
from apps.shipping.selectors import active_cities


class CityPaymentSettingsForm(forms.ModelForm):
    class Meta:
        model = City
        fields = (
            "promo_cart_threshold",
            "promo_shipping_mode",
            "promo_discounted_shipping_price",
        )
        widgets = {
            "promo_cart_threshold": forms.NumberInput(
                attrs={"class": "vTextField", "step": "0.01", "min": "0"}
            ),
            "promo_shipping_mode": forms.Select(attrs={"class": "kp-promo-mode-select"}),
            "promo_discounted_shipping_price": forms.NumberInput(
                attrs={
                    "class": "vTextField kp-promo-discounted-field",
                    "step": "0.01",
                    "min": "0",
                }
            ),
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["promo_shipping_mode"].help_text = _(
            "Free shipping sets delivery to 0 RSD. Discounted uses the price below."
        )

    def clean(self):
        cleaned = super().clean()
        mode = cleaned.get("promo_shipping_mode")
        discounted = cleaned.get("promo_discounted_shipping_price")
        if mode == ThresholdShippingMode.DISCOUNTED and discounted in (None, ""):
            self.add_error(
                "promo_discounted_shipping_price",
                _("Enter a discounted delivery price for this mode."),
            )
        return cleaned


class CitySelectorForm(forms.Form):
    city = forms.ModelChoiceField(
        label=_("Delivery city"),
        queryset=City.objects.none(),
        widget=forms.Select(attrs={"class": "kp-city-select", "id": "kp-payment-city"}),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["city"].queryset = active_cities()
