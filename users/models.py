from datetime import datetime
from typing import Any, Optional

from django.contrib.auth.models import User
from django.db import models

""" Model for User Profile """


class Profile(models.Model):
    user: models.OneToOneField[User] = models.OneToOneField(User, on_delete=models.CASCADE)
    is_online: models.BooleanField[bool] = models.BooleanField(default=False)
    following: models.ManyToManyField[User, Any] = models.ManyToManyField(
        User, related_name="following", blank=True
    )
    friends: models.ManyToManyField[User, Any] = models.ManyToManyField(
        User, related_name="my_friends", blank=True
    )
    bio: models.CharField[Optional[str]] = models.CharField(
        default="", blank=True, null=True, max_length=350
    )
    date_of_birth: models.CharField[str] = models.CharField(blank=True, max_length=150)
    updated: models.DateTimeField[datetime] = models.DateTimeField(auto_now=True)
    created: models.DateTimeField[datetime] = models.DateTimeField(auto_now_add=True)
    image: models.ImageField = models.ImageField(
        default="default.jpg", upload_to="profile_pics", blank=True, null=True
    )

    def profile_posts(self):
        return self.user.post_set.all()

    def get_friends(self) -> models.ManyToManyRelatedManager[User, Any]:
        return self.friends.all()

    def get_friends_no(self) -> int:
        return self.friends.all().count()

    def __str__(self) -> str:
        return f"{self.user.username} Profile"


STATUS_CHOICES = (("send", "send"), ("accepted", "accepted"))


class Relationship(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="friend_sender")
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="friend_receiver")
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}-{self.receiver}-{self.status}"
