import calendar
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View

from apps.dashboard.filters import parse_report_period
from apps.dashboard.services import build_dashboard_context


@method_decorator(staff_member_required, name="dispatch")
class DashboardIndexView(View):
    """Staff-only analytics overview (server-rendered)."""

    template_name = "admin/dashboard/index.html"

    def get(self, request):
        period = parse_report_period(request.GET)
        today = timezone.localdate()
        filter_year = request.GET.get("year") or (
            str(period.start.year) if period.preset == "month_pick" else ""
        )
        month_options = [
            {
                "value": month,
                "label": calendar.month_name[month],
                "selected": period.preset == "month_pick" and period.start.month == month,
            }
            for month in range(1, 13)
        ]
        context = {
            "title": "Shop analytics",
            "month_options": month_options,
            "filter_year": filter_year,
            "current_year": today.year,
            **build_dashboard_context(period),
        }
        return render(request, self.template_name, context)
