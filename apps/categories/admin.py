from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from apps.categories.models import Category
from apps.core.slugs import localized_slug, unique_slug_for_translation


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display = ("name", "slug_display", "parent", "is_active", "sort_order")
    search_fields = ("translations__name", "translations__slug")
    list_select_related = ("parent",)
    fieldsets = (
        (
            _("Name & URL"),
            {
                "fields": ("name", "slug", "description"),
            },
        ),
        (None, {"fields": ("parent", "image", "is_active", "sort_order")}),
    )

    def save_translation(self, request, obj, form, change):
        translation = form.instance
        if not (translation.slug or "").strip():
            name = (translation.name or "").strip()
            if name:
                translation.slug = unique_slug_for_translation(translation)
        super().save_translation(request, obj, form, change)

    @admin.display(description=_("Slug"))
    def slug_display(self, obj: Category) -> str:
        return localized_slug(obj) or "—"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("parent")
            .prefetch_related("translations", "parent__translations")
        )
