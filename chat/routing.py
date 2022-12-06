from django.urls import URLPattern, re_path

from . import consumers

websocket_urlpatterns: list[URLPattern] = [
    re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatRoomConsumer.as_asgi()),
]
