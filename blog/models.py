import logging

from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone


def get_image_filename(instance, filename) -> str:
    title = instance.title
    slug = slugify(title)
    logging.debug(f"Uploading file {slug}-{filename}")
    return f"post_images/{slug}-{filename}"


""" Post model """


class Post(models.Model):
    title: models.CharField = models.CharField(max_length=150)
    content: RichTextField = RichTextField(blank=True, null=True)
    date_posted: models.DateTimeField = models.DateTimeField(default=timezone.now)
    date_updated: models.DateTimeField = models.DateTimeField(auto_now=True)
    author: models.ForeignKey = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_image_filename, null=True, blank=True)
    likes: models.ManyToManyField = models.ManyToManyField(
        User, related_name="blogpost", blank=True
    )
    saves: models.ManyToManyField = models.ManyToManyField(
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
    post: models.ForeignKey = models.ForeignKey(
        Post, related_name="comments", on_delete=models.CASCADE
    )
    name: models.ForeignKey = models.ForeignKey(User, on_delete=models.CASCADE)
    body: models.TextField = models.TextField(max_length=200)
    date_added: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    likes: models.ManyToManyField = models.ManyToManyField(
        User, related_name="blogcomment", blank=True
    )
    reply: models.ForeignKey = models.ForeignKey(
        "self", null=True, related_name="replies", on_delete=models.CASCADE
    )

    def total_clikes(self) -> int:
        return self.likes.count()

    def __str__(self) -> str:
        return "%s - %s - %s" % (self.post.title, self.name, self.id)

    def get_absolute_url(self) -> str:
        return reverse("post-detail", kwargs={"pk": self.pk})
