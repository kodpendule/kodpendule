from datetime import timedelta

from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.shipping.selectors import active_cities

User = get_user_model()


class CheckoutForm(forms.Form):
    guest_email = forms.EmailField(
        label=_("Email"),
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control", "autocomplete": "email"}),
    )
    first_name = forms.CharField(
        label=_("First name"),
        max_length=120,
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "given-name"}),
    )
    last_name = forms.CharField(
        label=_("Last name"),
        max_length=120,
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "family-name"}),
    )
    phone = forms.CharField(
        label=_("Phone"),
        max_length=32,
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "tel"}),
    )

    shipping_city = forms.ModelChoiceField(
        label=_("City"),
        queryset=active_cities(),
        empty_label=_("Select city"),
        widget=forms.Select(attrs={"class": "form-select", "id": "id_shipping_city"}),
    )
    shipping_street = forms.CharField(
        label=_("Street and number"),
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "street-address"}),
    )
    shipping_postal_code = forms.CharField(
        label=_("Postal code"),
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "postal-code"}),
    )

    billing_same_as_shipping = forms.BooleanField(
        label=_("Billing address is the same as shipping"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input", "id": "id_billing_same"}),
    )
    billing_street = forms.CharField(
        label=_("Billing street"),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    billing_city_name = forms.CharField(
        label=_("Billing city"),
        max_length=120,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    billing_postal_code = forms.CharField(
        label=_("Billing postal code"),
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    order_notes = forms.CharField(
        label=_("Order notes (required)"),
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": _("Delivery instructions, building entrance, etc."),
            }
        ),
    )
    delivery_date = forms.DateField(
        label=_("Preferred delivery date"),
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    flexible_delivery = forms.BooleanField(
        label=_("I am flexible with the delivery date"),
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    def __init__(self, *args, user=None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.user = user
        if user and user.is_authenticated:
            self.fields["guest_email"].required = False
            self.fields["guest_email"].widget = forms.HiddenInput()
        else:
            self.fields["guest_email"].required = True

        min_date = timezone.localdate() + timedelta(days=1)
        self._min_delivery_date = min_date
        self.fields["delivery_date"].widget.attrs["min"] = min_date.isoformat()

    def clean_delivery_date(self):
        delivery_date = self.cleaned_data.get("delivery_date")
        if not delivery_date:
            raise forms.ValidationError(_("This field is required."))
        min_date = getattr(self, "_min_delivery_date", timezone.localdate() + timedelta(days=1))
        if delivery_date < min_date:
            raise forms.ValidationError(
                _("Delivery date must be at least tomorrow.")
            )
        return delivery_date

    def clean_guest_email(self) -> str:
        email = self.cleaned_data.get("guest_email", "").strip()
        if self.user and self.user.is_authenticated:
            account_email = (self.user.email or "").strip()
            if not account_email:
                raise forms.ValidationError(_("Email is required for checkout."))
            return account_email
        if not email:
            raise forms.ValidationError(_("Email is required for guest checkout."))
        return email

    def clean_order_notes(self) -> str:
        notes = (self.cleaned_data.get("order_notes") or "").strip()
        if not notes:
            raise forms.ValidationError(_("Order notes are required."))
        return notes

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("billing_same_as_shipping"):
            city = cleaned.get("shipping_city")
            cleaned["billing_street"] = cleaned.get("shipping_street", "")
            cleaned["billing_city_name"] = city.name if city else ""
            cleaned["billing_postal_code"] = cleaned.get("shipping_postal_code", "")
        else:
            for field in ("billing_street", "billing_city_name", "billing_postal_code"):
                if not cleaned.get(field):
                    self.add_error(field, _("This field is required."))
        return cleaned
