"""
Admin forms for Parler models without language tabs.

Translated fields are shown as stacked pairs, e.g. name_sr then name_en.
"""

from __future__ import annotations

from typing import Any, Iterable, Sequence

from django import forms
from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _

ADMIN_LANGUAGE_CODES: tuple[str, ...] = ("sr", "en")


def language_display_name(code: str) -> str:
    if code == "sr":
        return _("Serbian")
    if code == "en":
        return _("English")
    return code


def stacked_field_name(base: str, language_code: str) -> str:
    return f"{base}_{language_code}"


def expand_fieldsets(
    fieldsets: Sequence[tuple[Any, dict]],
    translatable_fields: Iterable[str],
) -> list[tuple[Any, dict]]:
    translatable = set(translatable_fields)
    expanded_fieldsets: list[tuple[Any, dict]] = []
    for title, options in fieldsets:
        fields = options.get("fields", ())
        new_fields: list[str] = []
        for name in fields:
            if name in translatable:
                for code in ADMIN_LANGUAGE_CODES:
                    new_fields.append(stacked_field_name(name, code))
            else:
                new_fields.append(name)
        expanded_fieldsets.append((title, {**options, "fields": tuple(new_fields)}))
    return expanded_fieldsets


def build_stacked_form_class(
    model_class: type[models.Model],
    translatable_fields: Sequence[str],
    *,
    master_fields: Sequence[str] | None = None,
) -> type[forms.ModelForm]:
    translation_model = model_class._parler_meta.get_all_models()[0]
    translated_names = list(translatable_fields)
    meta_fields = master_fields or [
        f.name
        for f in model_class._meta.fields
        if f.editable and not f.primary_key
    ]

    form_attrs: dict[str, Any] = {}

    for base_name in translated_names:
        try:
            source_field = translation_model._meta.get_field(base_name)
        except models.FieldDoesNotExist:
            continue
        for code in ADMIN_LANGUAGE_CODES:
            field_name = stacked_field_name(base_name, code)
            label = _("%(field)s (%(language)s)") % {
                "field": source_field.verbose_name,
                "language": language_display_name(code),
            }
            form_field = source_field.formfield(label=label, required=False)
            if form_field is not None:
                form_attrs[field_name] = form_field

    def _load_translation_values(self) -> None:
        if not self.instance or not self.instance.pk:
            return
        for trans in self.instance.translations.all():
            code = trans.language_code
            for base_name in translated_names:
                key = stacked_field_name(base_name, code)
                if key in self.fields:
                    self.initial[key] = getattr(trans, base_name, "") or ""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(TranslatableStackedForm, self).__init__(*args, **kwargs)
        self._load_translation_values()

    def _write_translations(self, obj: models.Model) -> None:
        for code in ADMIN_LANGUAGE_CODES:
            trans = obj.translations.filter(language_code=code).first()
            if trans is None:
                trans = translation_model(master=obj, language_code=code)
            for base_name in translated_names:
                value = self.cleaned_data.get(stacked_field_name(base_name, code), "")
                setattr(trans, base_name, value if value is not None else "")
            _autofill_slug(self, trans, obj)
            trans.save()

    def _autofill_slug(self, trans: models.Model, master: models.Model) -> None:
        if "slug" not in translated_names:
            return
        slug = (getattr(trans, "slug", None) or "").strip()
        name = (getattr(trans, "name", None) or "").strip()
        if slug or not name:
            return
        autofill = getattr(self, "autofill_slug_for_translation", None)
        if callable(autofill):
            trans.slug = autofill(trans, master)
        else:
            from apps.core.slugs import unique_slug_for_translation

            fallback = getattr(master, "sku", "") if hasattr(master, "sku") else ""
            trans.slug = unique_slug_for_translation(trans, fallback=fallback)

    def save(self, commit: bool = True) -> models.Model:
        obj = super(TranslatableStackedForm, self).save(commit=commit)
        if commit:
            self._write_translations(obj)
        return obj

    form_attrs["__init__"] = __init__
    form_attrs["_load_translation_values"] = _load_translation_values
    form_attrs["_write_translations"] = _write_translations
    form_attrs["_autofill_slug"] = _autofill_slug
    form_attrs["save"] = save
    form_attrs["Meta"] = type(
        "Meta",
        (),
        {"model": model_class, "fields": tuple(meta_fields)},
    )

    TranslatableStackedForm = type(
        f"{model_class.__name__}StackedForm",
        (forms.ModelForm,),
        form_attrs,
    )
    return TranslatableStackedForm


class TranslatableStackedAdmin(admin.ModelAdmin):
    """
    Parler model admin with Serbian / English fields stacked (no language tabs).
    """

    sortable_by = ()
    translatable_fields: tuple[str, ...] = ()

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        write = getattr(form, "_write_translations", None)
        if callable(write):
            write(obj)

    def get_form(self, request, obj=None, **kwargs):
        if self.translatable_fields:
            kwargs["form"] = build_stacked_form_class(
                self.model,
                self.translatable_fields,
            )
        return super().get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not self.translatable_fields:
            return fieldsets
        return expand_fieldsets(fieldsets, self.translatable_fields)

    @property
    def media(self):
        return super(admin.ModelAdmin, self).media
