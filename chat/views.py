import logging
from typing import Any, Optional, Union

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db.models.manager import BaseManager
from django.http import (
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.shortcuts import redirect, render

from chat.models import Chat, Room, Shout, ShoutBox
from friend.models import FriendList
from users.models import Profile


@login_required
def room_enroll(request) -> HttpResponse:
    friends = FriendList.objects.filter(user=request.user)[0].friends.all()
    all_rooms: BaseManager = Room.objects.filter(
        Q(author=request.user) | Q(friend=request.user)
    ).order_by("-created")

    context: dict[str, Any] = {
        "all_rooms": all_rooms,
        "all_friends": friends,
    }
    return render(request, "chat/join_room.html", context)


@login_required
def room_choice(request, friend_id) -> Union[HttpResponseRedirect, HttpResponsePermanentRedirect]:
    friend = User.objects.filter(pk=friend_id)
    if not friend:
        messages.error(request, "Invalid User ID")
        return redirect("room-enroll")
    if not FriendList.objects.filter(user=request.user, friends=friend[0]):
        messages.error(request, "You need to be friends to chat")
        return redirect("room-enroll")

    room: BaseManager = Room.objects.filter(
        Q(author=request.user, friend=friend[0]) | Q(author=friend[0], friend=request.user)
    )
    if not room:
        create_room: Room = Room(author=request.user, friend=friend[0])
        create_room.save()
        room = create_room.room_id
        return redirect("room", room, friend_id)

    return redirect("room", room[0].room_id, friend_id)


""" Chatroom between users """


@login_required
def room(
    request, room_name, friend_id
) -> Union[HttpResponseRedirect, HttpResponsePermanentRedirect, HttpResponse]:
    all_rooms: BaseManager = Room.objects.filter(room_id=room_name)
    if not all_rooms:
        messages.error(request, "Invalid Room ID")
        return redirect("room-enroll")

    chats: BaseManager = Chat.objects.filter(room_id=room_name).order_by("date")

    context: dict[str, Any] = {
        "old_chats": chats,
        "my_name": request.user,
        "friend_name": User.objects.get(pk=friend_id),
        "room_name": room_name,
    }
    return render(request, "chat/chatroom.html", context)


@login_required
def shoutbox_create(request) -> HttpResponse:
    if not request.user.is_staff:
        raise PermissionDenied()
    all_shoutboxes: BaseManager = ShoutBox.objects.filter(
        Q(author=request.user) | Q(participants=request.user)
    ).order_by("-created")

    context: dict[str, Any] = {
        "all_shoutboxes": all_shoutboxes,
    }
    return render(request, "chat/join_shoutbox.html", context)


""" Shoutbox for all users """


@login_required
def shoutbox(
    request, shoutbox_id
) -> Union[HttpResponseRedirect, HttpResponsePermanentRedirect, HttpResponse]:
    shoutbox: Optional[ShoutBox] = None
    userobj: Profile = Profile.objects.get(id=request.user.id)
    try:
        shoutbox = ShoutBox.objects.get(shoutbox_id=shoutbox_id)
    except ShoutBox.DoesNotExist:
        messages.error(request, "Invalid ShoutBox ID")
        # return redirect("shoutbox-join")

    if shoutbox.shoutbox_name.lower() == "admin" and not userobj.is_staff:
        raise PermissionDenied()  # Only Admins/staff in admin chat
    elif not userobj.verified:
        raise PermissionDenied()  # Only verified individuals can get into group chat
    else:
        if request.user not in shoutbox.participants.all():
            logging.debug(f"Adding user {userobj} to {shoutbox}")
            shoutbox.participants.add(request.user)

    shouts: BaseManager = Shout.objects.filter(shoutbox_id=shoutbox_id).order_by("date")

    context: dict[str, Any] = {
        "old_shouts": shouts,
        "my_name": request.user,
        "shoutbox_id": shoutbox_id,
    }
    return render(request, "chat/shoutbox.html", context)
