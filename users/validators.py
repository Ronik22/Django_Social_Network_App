from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from users.models import BlockList


def validate_email(value) -> None:
    if User.objects.filter(email=value).exists():
        raise ValidationError(
            (f"{value} is already registered to an account."), params={"value": value}
        )

    if BlockList.objects.filter(email=value).exists():
        raise ValidationError((f"{value} is banned."), params={"value": value})
