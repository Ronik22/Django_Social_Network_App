from django.http import HttpRequest
from users.models import Profile

RELATIONSHIP_BLOCKLIST: list[str] = ["single_male", "single_female"]


def is_ajax(request: HttpRequest) -> bool:
    """
    To fix request.is_ajax() error which is deprecated in django > v3.1

    Args:
        request (request)

    Returns:
        _type_: boolean
    """
    return request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"


def is_user_verified(userobj: Profile) -> bool:
    if userobj.verified or userobj.user.is_staff:
        return True
    else:
        return False


def can_user_see_images(userobj: Profile) -> bool:
    if (
        userobj.relationship_status in RELATIONSHIP_BLOCKLIST
        and not userobj.relationship_status_override
    ) or not is_user_verified(userobj):
        return False
    else:
        return True


def handle_uploaded_file(filedata, dest_filepath: str) -> None:
    with open(dest_filepath, "wb+") as destination:
        for chunk in filedata.chunks():
            destination.write(chunk)
