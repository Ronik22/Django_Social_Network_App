from django.contrib import admin

from .models import Chat, Room, Shout, ShoutBox

admin.site.register(Chat)
admin.site.register(Room)
admin.site.register(Shout)
admin.site.register(ShoutBox)
