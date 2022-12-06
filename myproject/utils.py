import os
from pathlib import Path

import magic
from django.template.loader import render_to_string

from myproject import settings
from myproject.email import EmailHTML


def _get_mime_type(filepath: Path) -> str:
    mime: magic.Magic = magic.Magic(mime=True)
    return mime.from_file(filepath)


def build_email_message(
    subject: str,
    message: str,
    from_email: bool = None,
    recipient_list: list[str] = [],
    bcc_list: list[str] = [],
) -> EmailHTML:
    return EmailHTML(
        subject,
        message,
        from_email,
        recipient_list,
        bcc_list,
    )


def attach_to_email_object(email_message: EmailHTML, filepath: Path) -> EmailHTML:
    with open(filepath, "rb") as file:
        email_message.attach(filepath.name, file.read(), _get_mime_type(filepath))

    return email_message


def send_email_message(email_message: EmailHTML) -> int:
    fail_silently: bool = True
    if settings.DEBUG:
        fail_silently = False
    return email_message.send(fail_silently=fail_silently)


def send_welcome_email(user_email: str, username: str, profile_url: str) -> int:
    context: dict[str, str] = {
        "email": user_email,
        "username": username,
        "profile_url": profile_url,
    }
    html_message: str = render_to_string(
        os.path.join(settings.EMAIL_TEMPLATE_ROOT, "welcome_email.html"), context
    )
    email_message: EmailHTML = build_email_message(
        subject="Welcome to CSCTN.net!",
        message=html_message,
        recipient_list=[user_email],
    )

    return send_email_message(email_message)
