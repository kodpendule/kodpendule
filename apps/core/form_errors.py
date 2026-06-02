"""Storefront form validation copy in Serbian Latin (overrides Django Cyrillic defaults)."""

from django.utils.translation import gettext_lazy as _

LATIN_REQUIRED = _("This field is required.")


def apply_latin_required_messages(form) -> None:
    """Ensure required-field errors use project Latin translations, not Cyrillic fallbacks."""
    for field in form.fields.values():
        if field.required:
            field.error_messages.setdefault("required", LATIN_REQUIRED)
