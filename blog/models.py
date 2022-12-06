from datetime import datetime
from typing import Any

from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone

""" Post model """


class Post(models.Model):
    title: models.CharField[str] = models.CharField(max_length=150)
    content: RichTextField = RichTextField(blank=True, null=True)
    date_posted: models.DateTimeField[datetime] = models.DateTimeField(default=timezone.now)
    date_updated: models.DateTimeField[datetime] = models.DateTimeField(auto_now=True)
    author: models.ForeignKey[User] = models.ForeignKey(User, on_delete=models.CASCADE)
    likes: models.ManyToManyField[User, Any] = models.ManyToManyField(
        User, related_name="blogpost", blank=True
    )
    saves: models.ManyToManyField[User, Any] = models.ManyToManyField(
        User, related_name="blogsave", blank=True
    )

    def total_likes(self) -> int:
        return self.likes.count()

    def total_saves(self) -> int:
        return self.saves.count()

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("post-detail", kwargs={"pk": self.pk})


""" Comment model """


class Comment(models.Model):
    post: models.ForeignKey[Post] = models.ForeignKey(
        Post, related_name="comments", on_delete=models.CASCADE
    )
    name: models.ForeignKey[User] = models.ForeignKey(User, on_delete=models.CASCADE)
    body: models.TextField[str] = models.TextField(max_length=200)
    date_added: models.DateTimeField[datetime] = models.DateTimeField(auto_now_add=True)
    likes: models.ManyToManyField[User, Any] = models.ManyToManyField(
        User, related_name="blogcomment", blank=True
    )
    reply: models.ForeignKey[None] = models.ForeignKey(
        "self", null=True, related_name="replies", on_delete=models.CASCADE
    )

    def total_clikes(self) -> int:
        return self.likes.count()

    def __str__(self) -> str:
        return "%s - %s - %s" % (self.post.title, self.name, self.id)

    def get_absolute_url(self) -> str:
        return reverse("post-detail", kwargs={"pk": self.pk})
