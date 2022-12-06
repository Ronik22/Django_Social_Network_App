from django.contrib.auth.decorators import login_required
from django.db.models.manager import BaseManager
from django.http import HttpResponse  # noqa: F401
from django.shortcuts import render

from notification.models import Notification

# Create your views here.

""" All notifications """


@login_required
def ShowNotifications(request) -> HttpResponse:
    user: str = request.user
    notifications: BaseManager[Notification] = Notification.objects.filter(user=user).order_by(
        "-date"
    )
    context: dict[str, BaseManager[Notification]] = {
        "notifications": notifications,
    }
    return render(request, "blog/notifications.html", context)
