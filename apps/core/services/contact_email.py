"""Contact form email delivery."""

from __future__ import annotations

import logging

from django.utils.translation import gettext as _

from apps.core.email_recipients import shop_admin_recipients
from apps.core.mail import send_shop_email

logger = logging.getLogger(__name__)


def send_contact_form_email(
    *,
    name: str,
    email: str,
    phone: str,
    message: str,
) -> bool:
    recipients = shop_admin_recipients()
    if not recipients:
        logger.warning("Contact form email skipped: no admin recipients configured")
        return False

    subject = _("Contact form: %(name)s") % {"name": name}
    lines = [
        _("A message was submitted via the shop contact form."),
        "",
        _("Name: %(name)s") % {"name": name},
        _("Email: %(email)s") % {"email": email},
    ]
    if phone:
        lines.append(_("Phone: %(phone)s") % {"phone": phone})
    lines.extend(["", _("Message:"), message])

    return send_shop_email(
        subject=subject,
        message="\n".join(lines),
        recipient_list=recipients,
        reply_to=email,
    )
