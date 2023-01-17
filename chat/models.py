from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Room(models.Model):
    room_id: models.AutoField = models.AutoField(primary_key=True)
    author: models.ForeignKey = models.ForeignKey(
        User, related_name="author_room", on_delete=models.CASCADE
    )
    friend: models.ForeignKey = models.ForeignKey(
        User, related_name="friend_room", on_delete=models.CASCADE
    )
    created: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.room_id}-{self.author}-{self.friend}"


class Chat(models.Model):
    room_id: models.ForeignKey = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name="chats"
    )
    author: models.ForeignKey = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="author_msg"
    )
    friend: models.ForeignKey = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="friend_msg"
    )
    text: models.CharField = models.CharField(max_length=300)
    date: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    has_seen: models.BooleanField = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.id} - {self.date}"


class ShoutBox(models.Model):
    shoutbox_id: models.AutoField = models.AutoField(primary_key=True)
    shoutbox_name: models.CharField = models.CharField(max_length=120, null=True, blank=True)
    author: models.ForeignKey = models.ForeignKey(
        User, related_name="author_shout_box", on_delete=models.CASCADE
    )
    participants: models.ManyToManyField = models.ManyToManyField(
        User, related_name="shoutbox_participants", null=True, blank=True
    )

    def __str__(self) -> str:
        return f"{self.shoutbox_id} - {self.shoutbox_name}"


class Shout(models.Model):
    shoutbox: models.ForeignKey = models.ForeignKey(
        ShoutBox, on_delete=models.CASCADE, related_name="shouts"
    )
    author: models.ForeignKey = models.ForeignKey(
        User,
        related_name="author_shout_mesage",
        on_delete=models.CASCADE,
        null=True,
    )
    text: models.CharField = models.CharField(max_length=300)
    date: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    who_has_seen: models.ManyToManyField = models.ManyToManyField(
        User, related_name="shoutbox_who_has_seen", null=True, blank=True
    )

    def __str__(self) -> str:
        return f"{self.shoutbox}-{self.author}-{self.date}"
