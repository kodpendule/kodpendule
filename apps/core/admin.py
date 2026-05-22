from django.contrib import admin
from parler.admin import TranslatableAdmin

from apps.core.models import (
    FooterSettings,
    HeroBanner,
    HomepageSection,
    PromoSection,
    SiteSettings,
    SocialLink,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(TranslatableAdmin):
    def has_add_permission(self, request) -> bool:
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


@admin.register(FooterSettings)
class FooterSettingsAdmin(TranslatableAdmin):
    def has_add_permission(self, request) -> bool:
        return not FooterSettings.objects.exists()

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("platform", "url", "sort_order", "is_active")
    list_filter = ("platform", "is_active")
    ordering = ("sort_order",)


@admin.register(HeroBanner)
class HeroBannerAdmin(TranslatableAdmin):
    list_display = ("__str__", "sort_order", "is_active")
    list_filter = ("is_active",)
    ordering = ("sort_order",)


@admin.register(PromoSection)
class PromoSectionAdmin(TranslatableAdmin):
    list_display = ("__str__", "placement", "sort_order", "is_active")
    list_filter = ("placement", "is_active")
    ordering = ("sort_order",)


@admin.register(HomepageSection)
class HomepageSectionAdmin(admin.ModelAdmin):
    list_display = ("section_type", "is_active", "max_products")
    list_filter = ("is_active",)
