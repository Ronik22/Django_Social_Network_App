import json

from asgiref.sync import async_to_sync, sync_to_async  # noqa: F401
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User

from chat.models import Chat, Room, Shout, ShoutBox

"""MESSAGE DB ENTRY"""


@sync_to_async
def create_new_message(me, friend, message, room_id) -> Chat:
    get_room: Room = Room.objects.filter(room_id=room_id)[0]
    author_user: User = User.objects.filter(username=me)[0]
    friend_user: User = User.objects.filter(username=friend)[0]
    new_chat: Chat = Chat.objects.create(
        author=author_user, friend=friend_user, room_id=get_room, text=message
    )
    return new_chat


"""SHOUT DB ENTRY"""


@sync_to_async
def create_new_shout(me, message, shoutbox_id) -> Chat:
    shoutbox: ShoutBox = ShoutBox.objects.filter(shoutbox_id=shoutbox_id)[0]
    author_user: User = User.objects.filter(username=me)[0]
    new_shout: Shout = Shout.objects.create(author=author_user, shoutbox=shoutbox, text=message)
    return new_shout


class ChatRoomConsumer(AsyncWebsocketConsumer):

    """Connect"""

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    """Disconnect"""

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    """Receive"""

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json["username"]
        user_image = text_data_json["user_image"]

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chatroom_message",
                "message": message,
                "username": username,
                "user_image": user_image,
            },
        )

    """Messages"""

    async def chatroom_message(self, event):
        message = event["message"]
        username = event["username"]
        user_image = event["user_image"]

        await create_new_message(
            me=self.scope["user"], friend=username, message=message, room_id=self.room_name
        )

        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "username": username,
                    "user_image": user_image,
                }
            )
        )


class ShoutBoxConsumer(AsyncWebsocketConsumer):

    """Connect"""

    async def connect(self):
        self.shoutbox_id = self.scope["url_route"]["kwargs"]["shoutbox_id"]
        self.shoutbox_group_name = "shoutbox_%s" % self.shoutbox_id

        await self.channel_layer.group_add(self.shoutbox_group_name, self.channel_name)

        await self.accept()

    """Disconnect"""

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.shoutbox_group_name, self.channel_name)

    """Receive"""

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json["username"]
        user_image = text_data_json["user_image"]

        await self.channel_layer.group_send(
            self.shoutbox_group_name,
            {
                "type": "shoutbox_message",
                "message": message,
                "username": username,
                "user_image": user_image,
            },
        )

    """Messages"""

    async def shoutbox_message(self, event):
        message = event["message"]
        username = event["username"]
        user_image = event["user_image"]

        await create_new_shout(me=self.scope["user"], message=message, shoutbox_id=self.shoutbox_id)

        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "username": username,
                    "user_image": user_image,
                }
            )
        )
