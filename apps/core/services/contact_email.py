from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


def send_contact_message(*, name: str, email: str, subject: str, message: str) -> None:
    recipient = settings.CONTACT_EMAIL_TO
    if not recipient:
        raise ValueError("CONTACT_EMAIL_TO is not configured.")

    mail_subject = _("Contact form: %(subject)s") % {"subject": subject}
    body = _(
        "Name: %(name)s\n"
        "Email: %(email)s\n"
        "Subject: %(subject)s\n\n"
        "%(message)s"
    ) % {
        "name": name,
        "email": email,
        "subject": subject,
        "message": message,
    }

    mail = EmailMessage(
        subject=str(mail_subject),
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
        reply_to=[email],
    )
    mail.send(fail_silently=False)
    logger.info("Contact form message sent to %s from %s", recipient, email)
