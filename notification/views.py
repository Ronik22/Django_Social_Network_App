import logging
from typing import Optional, Union

from django.contrib.auth.decorators import login_required
from django.db.models.manager import BaseManager
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from blog.utils import is_ajax
from notification.models import Notification

# Create your views here.

""" All notifications """


@login_required
def ShowNotifications(request) -> HttpResponse:
    user: str = request.user
    notifications: BaseManager = Notification.objects.filter(user=user).order_by("-date")
    context: dict[str, BaseManager] = {
        "notifications": notifications,
    }
    return render(request, "blog/notifications.html", context)


@login_required
def notification_status(request) -> Optional[JsonResponse]:
    notification_id: str = request.POST.get("notification_id")
    notification: Notification = Notification.objects.get(id=notification_id)

    # Simple toggle switch for this bool
    if not notification.is_seen:
        logging.debug(f"Before {notification.id=}:{notification.is_seen=}")
        notification.is_seen = True
        logging.debug(f"After {notification.id=}:{notification.is_seen=}")
    else:
        logging.debug(f"Before {notification.id=}:{notification.is_seen=}")
        notification.is_seen = False
        logging.debug(f"After {notification.id=}:{notification.is_seen=}")

    notification.save()

    context: dict[str, Union[Notification, bool]] = {
        "notification": notification,
    }

    if is_ajax(request=request):
        html: str = render_to_string("mark_read_section.html", context, request=request)
        return JsonResponse({"form": html})
