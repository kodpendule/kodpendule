from django.contrib import admin
from parler.admin import TranslatableAdmin

from apps.categories.models import Category


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display = ("__str__", "parent", "is_active", "sort_order")
    list_filter = ("is_active", "parent")
    search_fields = ("translations__name", "translations__slug")
    list_select_related = ("parent",)
    prepopulated_fields = {}
    fieldsets = (
        (None, {"fields": ("parent", "image", "is_active", "sort_order")}),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("parent")
            .prefetch_related("translations", "parent__translations")
        )
