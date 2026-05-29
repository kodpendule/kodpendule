from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.accounts.forms import CustomerContactImportForm
from apps.core.kp_admin import KPModelAdmin
from apps.accounts.models import CustomerContact, CustomerProfile, User
from apps.accounts.services.customer_contact_csv import (
    EXPORT_FIELDNAMES,
    export_contacts_csv,
    import_contacts_csv,
)


class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    extra = 0
    verbose_name = _("Customer profile")
    verbose_name_plural = _("Customer profiles")


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    sortable_by = ()
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    inlines = [CustomerProfileInline]


@admin.register(CustomerContact)
class CustomerContactAdmin(KPModelAdmin):
    change_list_template = "admin/accounts/customercontact/change_list.html"
    list_display = (
        "email",
        "full_name_display",
        "phone",
        "account_link",
        "order_count",
        "registered_at",
        "last_seen_at",
    )
    search_fields = ("email", "first_name", "last_name", "phone", "user__username")
    readonly_fields = (
        "email",
        "first_name",
        "last_name",
        "phone",
        "user",
        "order_count",
        "registered_at",
        "first_seen_at",
        "last_seen_at",
    )
    list_select_related = ("user",)
    ordering = ("-last_seen_at",)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = [
            path(
                "export-csv/",
                self.admin_site.admin_view(self.export_csv_view),
                name="accounts_customercontact_export_csv",
            ),
            path(
                "import-csv/",
                self.admin_site.admin_view(self.import_csv_view),
                name="accounts_customercontact_import_csv",
            ),
        ]
        return urls + super().get_urls()

    def export_csv_view(self, request: HttpRequest) -> HttpResponse:
        if not self.has_view_permission(request):
            return redirect("admin:index")

        csv_data = export_contacts_csv()
        stamp = timezone.localdate().strftime("%Y%m%d")
        response = HttpResponse(csv_data, content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="customer-contacts-{stamp}.csv"'
        )
        return response

    def import_csv_view(self, request: HttpRequest) -> HttpResponse:
        if not self.has_change_permission(request):
            return redirect("admin:index")

        form = CustomerContactImportForm(request.POST or None, request.FILES or None)
        result = None

        if request.method == "POST" and form.is_valid():
            upload = form.cleaned_data["csv_file"]
            try:
                result = import_contacts_csv(upload)
            except ValueError as exc:
                form.add_error("csv_file", str(exc))
            else:
                from django.contrib import messages

                messages.success(
                    request,
                    _("Import finished: %(created)s created, %(updated)s updated, %(skipped)s skipped.")
                    % {
                        "created": result.created,
                        "updated": result.updated,
                        "skipped": result.skipped,
                    },
                )
                return redirect(reverse("admin:accounts_customercontact_changelist"))

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": _("Import customer contacts"),
            "form": form,
            "result": result,
            "export_columns": EXPORT_FIELDNAMES,
        }
        return render(request, "admin/accounts/customercontact/import_csv.html", context)

    @admin.display(description=_("Name"))
    def full_name_display(self, obj: CustomerContact) -> str:
        return obj.full_name or "—"

    @admin.display(description=_("Account"))
    def account_link(self, obj: CustomerContact) -> str:
        if not obj.user_id:
            return "—"
        user = obj.user
        url = reverse("admin:accounts_user_change", args=[user.pk])
        return format_html('<a href="{}">{}</a>', url, user.username)
