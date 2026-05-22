from django import forms
from django.utils.translation import gettext_lazy as _

from apps.orders.selectors.order_selectors import normalize_order_number, normalize_tracking_email


class GuestOrderTrackForm(forms.Form):
    order_number = forms.CharField(
        label=_("Order number"),
        max_length=32,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "KP-20260520-ABC123",
                "autocomplete": "off",
            }
        ),
    )
    email = forms.EmailField(
        label=_("Email address"),
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "autocomplete": "email",
            }
        ),
    )

    def clean_order_number(self) -> str:
        return normalize_order_number(self.cleaned_data["order_number"])

    def clean_email(self) -> str:
        return normalize_tracking_email(self.cleaned_data["email"])
