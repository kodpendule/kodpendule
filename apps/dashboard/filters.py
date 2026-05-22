"""Report period parsing for dashboard filters."""

from calendar import monthrange
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext as _


@dataclass(frozen=True)
class ReportPeriod:
    """Inclusive date range in the active timezone."""

    start: date
    end: date
    preset: str

    @property
    def label(self) -> str:
        if self.start == self.end:
            return self.start.isoformat()
        return f"{self.start.isoformat()} — {self.end.isoformat()}"


def _local_today() -> date:
    return timezone.localdate()


def parse_report_period(get_params) -> ReportPeriod:
    """
    Resolve reporting window from query params.

    Supported:
    - period: 7d | 30d | 90d | month | year (default 30d)
    - month + year: specific calendar month
    - from + to: custom inclusive range (YYYY-MM-DD)
    """
    today = _local_today()
    period = (get_params.get("period") or "30d").strip().lower()
    from_raw = (get_params.get("from") or "").strip()
    to_raw = (get_params.get("to") or "").strip()

    month_raw = get_params.get("month")
    year_raw = get_params.get("year")
    if month_raw and year_raw:
        try:
            month = int(month_raw)
            year = int(year_raw)
            if 1 <= month <= 12:
                last_day = monthrange(year, month)[1]
                return ReportPeriod(
                    start=date(year, month, 1),
                    end=date(year, month, last_day),
                    preset="month_pick",
                )
        except (TypeError, ValueError):
            pass

    if from_raw and to_raw:
        start = _parse_date(from_raw) or today
        end = _parse_date(to_raw) or today
        if start > end:
            start, end = end, start
        return ReportPeriod(start=start, end=end, preset="custom")

    quick_presets = {"7d", "30d", "90d", "month", "year"}
    if period in quick_presets:
        if period == "7d":
            return ReportPeriod(
                start=today - timedelta(days=6),
                end=today,
                preset="7d",
            )
        if period == "90d":
            return ReportPeriod(
                start=today - timedelta(days=89),
                end=today,
                preset="90d",
            )
        if period == "month":
            return ReportPeriod(
                start=today.replace(day=1),
                end=today,
                preset="month",
            )
        if period == "year":
            return ReportPeriod(
                start=today.replace(month=1, day=1),
                end=today,
                preset="year",
            )
        # 30d
        return ReportPeriod(
            start=today - timedelta(days=29),
            end=today,
            preset="30d",
        )

    return ReportPeriod(
        start=today - timedelta(days=29),
        end=today,
        preset="30d",
    )


def _parse_date(value: str) -> date | None:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def period_filter_choices(today: date | None = None) -> list[tuple[str, str]]:
    today = today or _local_today()
    month_label = _("This month ({month_year})").format(
        month_year=date_format(today, format="F Y", use_l10n=True),
    )
    return [
        ("7d", _("Last 7 days")),
        ("30d", _("Last 30 days")),
        ("90d", _("Last 90 days")),
        ("month", month_label),
        ("year", _("This year ({year})").format(year=today.year)),
    ]
