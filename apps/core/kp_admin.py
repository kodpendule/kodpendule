"""Shared Kod Pendule Django admin base classes."""

from django.contrib import admin
from django.template.response import TemplateResponse

from apps.core.admin_translatable import TranslatableStackedAdmin
from apps.core.admin_ui import changelist_ui_context

__all__ = ("KPModelAdmin", "KPTranslatableAdmin")


class KPModelAdmin(admin.ModelAdmin):
    """Changelist tables without column sort controls or ?o= ordering toggles."""

    sortable_by = ()

    def changelist_view(self, request, extra_context=None):
        extra_context = {
            **changelist_ui_context(self.opts.app_label, self.opts.model_name),
            **(extra_context or {}),
        }
        response = super().changelist_view(request, extra_context=extra_context)
        if isinstance(response, TemplateResponse):
            title = extra_context.get("kp_admin_changelist_title")
            if title:
                response.context_data["title"] = title
        return response


class KPTranslatableAdmin(KPModelAdmin, TranslatableStackedAdmin):
    """Translatable models: stacked sr/en fields, no language tabs."""
