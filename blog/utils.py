def is_ajax(request):
    """
    To fix request.is_ajax() error which is deprecated in django > v3.1

    Args:
        request (request)

    Returns:
        _type_: boolean
    """
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'