"""Report period parsing for dashboard filters."""

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from django.utils import timezone
from django.utils.translation import gettext as _

from apps.core.locale_dates import latin_month_year, latin_short_date


@dataclass(frozen=True)
class ReportPeriod:
    """Inclusive date range in the active timezone."""

    start: date
    end: date
    preset: str

    @property
    def label(self) -> str:
        if self.start == self.end:
            return latin_short_date(self.start)
        return f"{latin_short_date(self.start)} — {latin_short_date(self.end)}"


def _local_today() -> date:
    return timezone.localdate()


def _default_period(today: date | None = None) -> ReportPeriod:
    today = today or _local_today()
    return ReportPeriod(
        start=today - timedelta(days=29),
        end=today,
        preset="30d",
    )


def parse_report_period(get_params) -> ReportPeriod:
    """
    Resolve reporting window from query params.

    filter_mode=quick (default): period=7d|30d|90d|month|year
    filter_mode=manual: from + to (YYYY-MM-DD), inclusive
    """
    today = _local_today()
    mode = (get_params.get("filter_mode") or "").strip().lower()

    from_raw = (get_params.get("from") or "").strip()
    to_raw = (get_params.get("to") or "").strip()
    if mode == "manual" or (from_raw and to_raw):
        start = _parse_date(from_raw) or today
        end = _parse_date(to_raw) or today
        if start > end:
            start, end = end, start
        return ReportPeriod(start=start, end=end, preset="custom")

    period = (get_params.get("period") or "30d").strip().lower()
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
        return ReportPeriod(
            start=today - timedelta(days=29),
            end=today,
            preset="30d",
        )

    return _default_period(today)


def resolve_filter_mode(get_params, period: ReportPeriod) -> str:
    explicit = (get_params.get("filter_mode") or "").strip().lower()
    if explicit in {"quick", "manual"}:
        return explicit
    if period.preset == "custom":
        return "manual"
    return "quick"


def _parse_date(value: str) -> date | None:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def period_filter_choices(today: date | None = None) -> list[tuple[str, str]]:
    today = today or _local_today()
    month_label = _("This month ({month_year})").format(
        month_year=latin_month_year(today),
    )
    return [
        ("7d", _("Last 7 days")),
        ("30d", _("Last 30 days")),
        ("90d", _("Last 90 days")),
        ("month", month_label),
        ("year", _("This year ({year})").format(year=today.year)),
    ]
