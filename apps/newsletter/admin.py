from django.contrib import admin

from apps.newsletter.models import EmailCampaign, Subscriber


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "source", "created_at")
    list_filter = ("is_active", "source")
    search_fields = ("email",)
    date_hierarchy = "created_at"


@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    list_display = ("subject", "status", "sent_at", "created_at")
    list_filter = ("status",)
    search_fields = ("subject",)
    readonly_fields = ("created_at", "updated_at")
