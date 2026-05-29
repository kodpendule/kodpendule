from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.core.admin_display import money_cell, order_status_badge
from apps.core.kp_admin import KPModelAdmin
from apps.orders.models import Order, OrderItem, OrderStatus


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    verbose_name = _("Order item")
    verbose_name_plural = _("Order items")
    readonly_fields = ("product_name", "sku", "unit_price", "line_total_display")
    fields = (
        "product",
        "product_name",
        "sku",
        "unit_price",
        "quantity",
        "line_total_display",
    )
    classes = ("kp-inline-order-items",)

    @admin.display(description=_("Line total"))
    def line_total_display(self, obj: OrderItem) -> str:
        if obj.pk:
            return money_cell(obj.line_total, emphasize=True)
        return "—"


@admin.register(Order)
class OrderAdmin(KPModelAdmin):
    list_display = (
        "order_number",
        "customer_display",
        "status_badge",
        "total_display",
        "payment_method",
        "created_at",
    )
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
    list_per_page = 25
    save_on_top = True
    fieldsets = (
        (
            _("Order"),
            {
                "classes": ("kp-fieldset", "kp-fieldset--order-core"),
                "description": _(
                    "Update order status when you confirm, ship, or complete the order."
                ),
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
            {
                "classes": ("kp-fieldset", "kp-fieldset--customer"),
                "fields": ("first_name", "last_name", "phone"),
            },
        ),
        (
            _("Shipping"),
            {
                "classes": ("kp-fieldset", "kp-fieldset--shipping"),
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
                "classes": ("collapse", "kp-fieldset", "kp-fieldset--billing"),
                "fields": (
                    "billing_street",
                    "billing_city_name",
                    "billing_postal_code",
                ),
            },
        ),
        (
            _("Totals"),
            {
                "classes": ("kp-fieldset", "kp-fieldset--totals"),
                "description": _("Amounts charged to the customer."),
                "fields": ("subtotal", "total"),
            },
        ),
        (
            _("Timestamps"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "status" and formfield:
            formfield.widget = forms.Select(
                attrs={
                    **formfield.widget.attrs,
                    "class": "kp-status-select",
                },
                choices=formfield.choices,
            )
        return formfield

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

    @admin.display(description=_("Status"))
    def status_badge(self, obj: Order) -> str:
        return order_status_badge(obj.status)

    @admin.display(description=_("Total"))
    def total_display(self, obj: Order) -> str:
        return money_cell(obj.total, emphasize=True)

    @admin.display(description=_("Customer"))
    def customer_display(self, obj: Order) -> str:
        name = obj.customer_full_name
        if obj.is_guest_order:
            return format_html(
                '{} <span class="kp-guest-tag">({})</span>',
                name,
                _("guest"),
            )
        return name
