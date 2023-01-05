import logging
from typing import Dict, List, Optional

from django.db.models.manager import BaseManager

from notification.models import Notification


def notifications_processor(request) -> Dict[str, List[Notification]]:
    notifications_list: List[Notification] = []
    if request.user.is_authenticated:
        notifications: Optional[BaseManager] = Notification.objects.filter(user=request.user)

        for notification in notifications:
            if not notification.is_seen:
                logging.debug(f"{notification=}")
                notifications_list.append(notification)

    return {"notifications_list": notifications_list}
