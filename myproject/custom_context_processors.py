import logging
from typing import Optional

from django.db.models.manager import BaseManager

from notification.models import Notification


def notifications_processor(request):
    notifications_list: list[Notification] = []
    if request.user.is_authenticated:
        notifications: Optional[BaseManager] = Notification.objects.filter(user=request.user)

        for notification in notifications:
            logging.debug(f"{notification=}:{notification.is_seen=}")
            if not notification.is_seen:
                notifications_list.append(notification)
    else:
        notifications = 0
    return {"notifications": notifications}
