from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import View

from apps.core.admin_navigation import get_admin_nav_sections
from apps.dashboard.filters import parse_report_period, resolve_filter_mode
from apps.dashboard.services import build_dashboard_context


@method_decorator(staff_member_required, name="dispatch")
class DashboardIndexView(View):
    """Staff-only analytics overview (server-rendered)."""

    template_name = "admin/dashboard/index.html"

    def get(self, request):
        period = parse_report_period(request.GET)
        filter_mode = resolve_filter_mode(request.GET, period)
        admin_context = admin.site.each_context(request)
        if "kp_admin_nav_sections" not in admin_context:
            admin_context["kp_admin_nav_sections"] = get_admin_nav_sections(
                admin_context.get("available_apps", []),
                request,
            )
        context = {
            **admin_context,
            "title": _("Shop analytics"),
            "filter_mode": filter_mode,
            **build_dashboard_context(period),
        }
        return render(request, self.template_name, context)
