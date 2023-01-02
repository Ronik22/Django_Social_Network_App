from pathlib import Path

import magic
from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

EMAIL_ADMIN_RECIPIENTS = [
    "spitfiretn@gmail.com",  # Gary
    "Mona261971@yahoo.com",  # Mona
    "Badamson074@gmail.com",  # Ben
]


def _get_mime_type(filepath: Path) -> str:
    mime: magic.Magic = magic.Magic(mime=True)
    return mime.from_file(filepath)


def send_welcome_email(user_email: str, username: str, profile_url: str) -> int:
    context: dict[str, str] = {
        "email": user_email,
        "username": username,
        "profile_url": profile_url,
    }

    html_message: str = render_to_string("users/welcome_email.html", context)

    return mail.send_mail(
        subject=f"Welcome to {settings.SITE_NAME}!",
        message=strip_tags(html_message),
        from_email=None,  # Uses DEFAULT_FROM_EMAIL setting
        recipient_list=[user_email],
        html_message=html_message,
    )


def new_user_created_email(user_email: str, username: str, profile_url: str) -> int:
    context: dict[str, str] = {
        "email": user_email,
        "username": username,
        "profile_url": profile_url,
    }

    html_message: str = render_to_string("users/new_user_admins_email.html", context)

    return mail.send_mail(
        subject=f"New user needs verification at {settings.SITE_NAME}!",
        message=strip_tags(html_message),
        from_email=None,  # Uses DEFAULT_FROM_EMAIL setting
        recipient_list=EMAIL_ADMIN_RECIPIENTS,
        html_message=html_message,
    )
