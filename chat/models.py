from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.

class Room(models.Model):
    # room_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_id = models.AutoField(primary_key=True)
    author = models.ForeignKey(User, related_name='author_room', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='friend_room', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.room_id}-{self.author}-{self.friend}"


class Chat(models.Model):
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='chats')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_msg')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_msg')
    text = models.CharField(max_length=300)
    date = models.DateTimeField(auto_now_add=True)
    has_seen = models.BooleanField(default=False)

    def __str__(self):
        return '%s - %s' %(self.id, self.date)


