"""Serbian Latin date labels for admin (avoids Cyrillic locale month names)."""

from datetime import date

from django.utils.translation import gettext as _


def latin_month_name(month: int) -> str:
    names = (
        _("January"),
        _("February"),
        _("March"),
        _("April"),
        _("May"),
        _("June"),
        _("July"),
        _("August"),
        _("September"),
        _("October"),
        _("November"),
        _("December"),
    )
    return str(names[month - 1])


def latin_month_year(value: date) -> str:
    return f"{latin_month_name(value.month)} {value.year}"


def latin_short_date(value: date) -> str:
    """Admin / analytics date label (dd/mm/yyyy)."""
    return f"{value.day:02d}/{value.month:02d}/{value.year}"


def latin_short_datetime(value) -> str:
    """Admin datetime label (dd/mm/yyyy HH:mm)."""
    from django.utils import timezone

    if timezone.is_aware(value):
        value = timezone.localtime(value)
    return f"{value.day:02d}/{value.month:02d}/{value.year} {value:%H:%M}"
