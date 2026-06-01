from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from apps.core.checkout_settings import DeliveryTiming, checkout_today, min_scheduled_delivery_date
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

    delivery_timing = forms.ChoiceField(
        label=_("When should we deliver?"),
        choices=DeliveryTiming.choices,
        initial=DeliveryTiming.SAME_DAY,
        widget=forms.RadioSelect(attrs={"class": "shop-delivery-timing__input"}),
    )
    requested_delivery_date = forms.DateField(
        label=_("Preferred delivery date"),
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
                "id": "id_requested_delivery_date",
            }
        ),
        help_text=_("Choose any date after today — delivery is free for scheduled orders."),
    )

    order_notes = forms.CharField(
        label=_("Order note"),
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": _("Delivery instructions, building entrance, etc. (optional)"),
            }
        ),
    )

    accept_legal = forms.BooleanField(
        required=True,
        label=_("I have read and accept the Terms of Service and Privacy Policy."),
        error_messages={
            "required": _(
                "You must accept the Terms of Service and Privacy Policy to place an order."
            ),
        },
        widget=forms.CheckboxInput(
            attrs={
                "class": "shop-checkout-legal__checkbox",
            }
        ),
    )

    def __init__(self, *args, user=None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.user = user
        self.show_email_field = True
        if user and user.is_authenticated:
            account_email = (user.email or "").strip()
            if account_email:
                self.show_email_field = False
                self.fields["guest_email"].required = False
                self.fields["guest_email"].widget = forms.HiddenInput()
            else:
                self.fields["guest_email"].required = True
                self.fields["guest_email"].widget = forms.EmailInput(
                    attrs={"class": "form-control", "autocomplete": "email"}
                )
        else:
            self.fields["guest_email"].required = True

        min_date = min_scheduled_delivery_date()
        self.fields["requested_delivery_date"].widget.attrs["min"] = min_date.isoformat()

    def clean(self):
        cleaned = super().clean()
        timing = cleaned.get("delivery_timing")
        today = checkout_today()

        if timing == DeliveryTiming.SAME_DAY:
            cleaned["requested_delivery_date"] = today
        elif timing == DeliveryTiming.SCHEDULED:
            delivery_date = cleaned.get("requested_delivery_date")
            if not delivery_date:
                self.add_error(
                    "requested_delivery_date",
                    _("Choose a delivery date."),
                )
            elif delivery_date <= today:
                self.add_error(
                    "requested_delivery_date",
                    _("Choose a date after today for free scheduled delivery."),
                )
        return cleaned

    def clean_guest_email(self) -> str:
        email = (self.cleaned_data.get("guest_email") or "").strip()
        if self.user and self.user.is_authenticated:
            account_email = (self.user.email or "").strip()
            if account_email:
                return account_email
            if not email:
                raise forms.ValidationError(_("Email is required for checkout."))
            if User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
                raise forms.ValidationError(
                    _("This email is already linked to another account.")
                )
            return email
        if not email:
            raise forms.ValidationError(_("Email is required for guest checkout."))
        return email

    def clean_order_notes(self) -> str:
        return (self.cleaned_data.get("order_notes") or "").strip()
