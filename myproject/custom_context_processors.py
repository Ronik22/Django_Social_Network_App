import logging
from typing import Dict, List, Optional

from django.db.models import Q
from django.db.models.manager import BaseManager

from chat.models import Room
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


def chat_notifications_processor(request) -> Dict[str, int]:
    chat_notifications_count: int = 0

    if request.user.is_authenticated:
        all_rooms: BaseManager = Room.objects.filter(
            Q(author=request.user) | Q(friend=request.user)
        ).order_by("-created")

        for room in all_rooms:
            if room.friend == request.user and room.chats.all().last().author != request.user:
                chat_notifications_count += 1

    logging.debug(f"Chat notifications count for {request.user}: {chat_notifications_count}")

    return {"chat_notifications_count": chat_notifications_count}
