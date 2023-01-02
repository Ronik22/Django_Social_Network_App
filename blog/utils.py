from users.models import Profile


def is_ajax(request) -> bool:
    """
    To fix request.is_ajax() error which is deprecated in django > v3.1

    Args:
        request (request)

    Returns:
        _type_: boolean
    """
    return request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"


def is_user_verified(request):
    userobj = Profile.objects.get(id=request.user.id)
    return userobj.verified
