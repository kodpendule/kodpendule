from django import forms
from django.utils.translation import gettext_lazy as _


class ContactForm(forms.Form):
    name = forms.CharField(
        label=_("Your name"),
        max_length=120,
        widget=forms.TextInput(
            attrs={"class": "form-control", "autocomplete": "name"},
        ),
    )
    email = forms.EmailField(
        label=_("Your email"),
        widget=forms.EmailInput(
            attrs={"class": "form-control", "autocomplete": "email"},
        ),
    )
    subject = forms.CharField(
        label=_("Subject"),
        max_length=200,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    message = forms.CharField(
        label=_("Message"),
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 6,
                "placeholder": _("How can we help you?"),
            }
        ),
    )
