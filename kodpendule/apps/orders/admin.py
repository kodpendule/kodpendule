from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.orders.models import Order, OrderItem, OrderStatus


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    verbose_name = _("Order item")
    verbose_name_plural = _("Order items")
    readonly_fields = ("product_name", "sku", "unit_price", "line_total_display")
    fields = ("product", "product_name", "sku", "unit_price", "quantity", "line_total_display")

    @admin.display(description=_("Line total"))
    def line_total_display(self, obj: OrderItem) -> str:
        if obj.pk:
            return str(obj.line_total)
        return "—"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "customer_display",
        "status",
        "total",
        "payment_method",
        "created_at",
    )
    list_editable = ("status",)
    list_filter = ("status", "payment_method", "flexible_delivery", "created_at")
    search_fields = (
        "order_number",
        "guest_email",
        "first_name",
        "last_name",
        "phone",
        "user__email",
        "user__username",
    )
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("user", "shipping_city")
    inlines = [OrderItemInline]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            _("Order"),
            {
                "fields": (
                    "order_number",
                    "user",
                    "guest_email",
                    "status",
                    "payment_method",
                ),
            },
        ),
        (
            _("Customer"),
            {"fields": ("first_name", "last_name", "phone")},
        ),
        (
            _("Shipping"),
            {
                "fields": (
                    "shipping_street",
                    "shipping_city_name",
                    "shipping_postal_code",
                    "shipping_city",
                    "shipping_method",
                    "shipping_price",
                    "delivery_date",
                    "flexible_delivery",
                    "order_notes",
                ),
            },
        ),
        (
            _("Billing"),
            {
                "fields": (
                    "billing_street",
                    "billing_city_name",
                    "billing_postal_code",
                ),
            },
        ),
        (
            _("Totals"),
            {"fields": ("subtotal", "total")},
        ),
        (
            _("Timestamps"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user", "shipping_city", "shipping_method")
            .prefetch_related("items")
        )

    @admin.action(description=_("Mark as confirmed"))
    def mark_confirmed(self, request, queryset):
        queryset.update(status=OrderStatus.CONFIRMED)

    @admin.action(description=_("Mark as shipped"))
    def mark_shipped(self, request, queryset):
        queryset.update(status=OrderStatus.SHIPPED)

    @admin.action(description=_("Mark as delivered"))
    def mark_delivered(self, request, queryset):
        queryset.update(status=OrderStatus.DELIVERED)

    actions = ["mark_confirmed", "mark_shipped", "mark_delivered"]

    @admin.display(description=_("Customer"))
    def customer_display(self, obj: Order) -> str:
        name = obj.customer_full_name
        if obj.is_guest_order:
            return format_html(
                '{} <span style="color:#666;">({})</span>',
                name,
                _("guest"),
            )
        return name
